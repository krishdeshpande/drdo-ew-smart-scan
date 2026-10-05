"""
Deep Q-Network (DQN) Reinforcement Learning Scheduler for Electronic Support Receivers.
Uses PyTorch to learn optimal scanning policy directly from hit/miss/threat rewards.
"""

import os
import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
from typing import Optional, Dict, Any, List
from .base import BaseScheduler


class QNetwork(nn.Module):
    def __init__(self, input_dim: int, output_dim: int):
        super(QNetwork, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, output_dim)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class DQNScheduler(BaseScheduler):
    """
    Deep Q-Network ES Scheduler:
    Maps current spectrum observation (recent hit history, dwell elapsed time,
    current tuning state) to Q-values for each candidate frequency band.
    """
    def __init__(
        self,
        num_bands: int,
        obs_dim: Optional[int] = None,
        lr: float = 1e-3,
        gamma: float = 0.95,
        epsilon_start: float = 1.0,
        epsilon_min: float = 0.05,
        epsilon_decay: float = 0.995,
        buffer_size: int = 10000,
        batch_size: int = 64,
        target_update_interval: int = 50,
        device: str = "cpu"
    ):
        super().__init__(
            num_bands=num_bands,
            name="Deep Q-Network (RL Closed-Loop)",
            description="Neural network policy trained via reinforcement learning on hit/miss rewards."
        )
        self.obs_dim = obs_dim if obs_dim is not None else (3 * num_bands)
        self.gamma = gamma
        self.epsilon = epsilon_start
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.batch_size = batch_size
        self.target_update_interval = target_update_interval
        self.device = torch.device(device)

        self.policy_net = QNetwork(self.obs_dim, num_bands).to(self.device)
        self.target_net = QNetwork(self.obs_dim, num_bands).to(self.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()

        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=lr)
        self.loss_fn = nn.SmoothL1Loss()  # Huber loss for stability
        self.replay_buffer = deque(maxlen=buffer_size)

        self.last_state: Optional[np.ndarray] = None
        self.last_action: Optional[int] = None
        self.train_step_count = 0

    def reset(self):
        super().reset()
        self.last_state = None
        self.last_action = None

    def select_band(self, obs: np.ndarray) -> int:
        self.last_state = obs.copy()

        # Epsilon-greedy exploration
        if random.random() < self.epsilon:
            action = random.randint(0, self.num_bands - 1)
        else:
            with torch.no_grad():
                state_t = torch.FloatTensor(obs).unsqueeze(0).to(self.device)
                q_values = self.policy_net(state_t)
                action = int(torch.argmax(q_values).item())

        self.last_action = action
        return action

    def update(
        self,
        action: int,
        hit: bool,
        snr: float,
        reward: float,
        next_obs: np.ndarray,
        pdw: Optional[Dict[str, Any]] = None
    ):
        super().update(action, hit, snr, reward, next_obs, pdw)

        if self.last_state is not None and self.last_action is not None:
            # Store transition in replay buffer
            self.replay_buffer.append((
                self.last_state,
                self.last_action,
                reward,
                next_obs,
                False
            ))

        # Train step if enough samples in buffer
        if len(self.replay_buffer) >= self.batch_size:
            self._train_step()

        # Decay exploration rate
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def _train_step(self):
        batch = random.sample(self.replay_buffer, self.batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)

        states_t = torch.FloatTensor(np.array(states)).to(self.device)
        actions_t = torch.LongTensor(actions).unsqueeze(1).to(self.device)
        rewards_t = torch.FloatTensor(rewards).unsqueeze(1).to(self.device)
        next_states_t = torch.FloatTensor(np.array(next_states)).to(self.device)
        dones_t = torch.FloatTensor(dones).unsqueeze(1).to(self.device)

        # Current Q-values: Q(s, a)
        curr_q = self.policy_net(states_t).gather(1, actions_t)

        # Target Q-values: r + gamma * max_a' Q_target(s', a')
        with torch.no_grad():
            next_q = self.target_net(next_states_t).max(1)[0].unsqueeze(1)
            target_q = rewards_t + (1.0 - dones_t) * self.gamma * next_q

        loss = self.loss_fn(curr_q, target_q)

        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.policy_net.parameters(), max_norm=10.0)
        self.optimizer.step()

        self.train_step_count += 1
        if self.train_step_count % self.target_update_interval == 0:
            self.target_net.load_state_dict(self.policy_net.state_dict())

    def save_weights(self, path: str):
        torch.save({
            "policy_net": self.policy_net.state_dict(),
            "target_net": self.target_net.state_dict(),
            "epsilon": self.epsilon
        }, path)

    def load_weights(self, path: str):
        if os.path.exists(path):
            checkpoint = torch.load(path, map_location=self.device)
            self.policy_net.load_state_dict(checkpoint["policy_net"])
            self.target_net.load_state_dict(checkpoint["target_net"])
            self.epsilon = checkpoint.get("epsilon", self.epsilon_min)
