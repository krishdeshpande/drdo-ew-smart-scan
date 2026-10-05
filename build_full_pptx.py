import os
import sys
from pathlib import Path
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

BASE_DIR = Path(r"C:\Users\krish\.gemini\antigravity\scratch\drdo_ew_smart_scan")
ASSETS_DIR = BASE_DIR / "ppt_assets"
DIAG_DIR = BASE_DIR / "diagram_generator"
OUTPUT_PPTX = BASE_DIR / "DRDO_EW_Smart_Scan_Presentation.pptx"

# Exact scale factor from PDF points (1440 x 810) to EMU (12192000 x 6858000)
SCALE = 8466.66667

def to_emu(pt_val):
    return int(pt_val * SCALE)

def create_presentation():
    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333333) # 12192000 EMU
    prs.slide_height = Inches(7.5)      # 6858000 EMU
    blank_layout = prs.slide_layouts[6] # Blank slide layout

    sih_logo_path = ASSETS_DIR / "sih_logo_clean.png"
    sih_bulb_path = ASSETS_DIR / "sih_bulb_white.png"

    # -------------------------------------------------------------
    # Helper: Add Standard Background (Navy Footer, SIH Logo, Badge)
    # -------------------------------------------------------------
    def add_slide_frame(slide, slide_num, title_text=None, is_title_slide=False):
        # 1. Top Right SIH Logo
        if sih_logo_path.exists():
            slide.shapes.add_picture(
                str(sih_logo_path),
                to_emu(1160), to_emu(15), to_emu(250), to_emu(108)
            )

        # 2. Bottom Navy Banner
        footer = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            to_emu(0), to_emu(744), to_emu(1440), to_emu(66)
        )
        footer.fill.solid()
        footer.fill.fore_color.rgb = RGBColor(11, 83, 148) # #0b5394
        footer.line.fill.background()

        # Footer Center Text
        ft_tx = slide.shapes.add_textbox(to_emu(300), to_emu(746), to_emu(840), to_emu(60))
        tf = ft_tx.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = "SMART INDIA HACKATHON 2026"
        p.font.name = "Georgia"
        p.font.size = Pt(17)
        p.font.bold = True
        p.font.color.rgb = RGBColor(255, 255, 255)
        p.alignment = PP_ALIGN.CENTER

        # Footer Page Number
        pg_tx = slide.shapes.add_textbox(to_emu(1320), to_emu(746), to_emu(100), to_emu(60))
        tf2 = pg_tx.text_frame
        p2 = tf2.paragraphs[0]
        p2.text = str(slide_num)
        p2.font.name = "Arial"
        p2.font.size = Pt(17)
        p2.font.bold = True
        p2.font.color.rgb = RGBColor(255, 255, 255)
        p2.alignment = PP_ALIGN.RIGHT

        # 3. Top Left "numenors" Oval Badge (Slides 2 to 6)
        if not is_title_slide:
            badge = slide.shapes.add_shape(
                MSO_SHAPE.OVAL,
                to_emu(32), to_emu(28), to_emu(170), to_emu(78)
            )
            badge.fill.solid()
            badge.fill.fore_color.rgb = RGBColor(255, 255, 255)
            badge.line.color.rgb = RGBColor(94, 53, 177) # #5e35b1
            badge.line.width = Pt(2.5)
            tf_b = badge.text_frame
            tf_b.word_wrap = False
            tf_b.margin_left = 0
            tf_b.margin_right = 0
            tf_b.margin_top = 0
            tf_b.margin_bottom = 0
            tf_b.vertical_anchor = MSO_ANCHOR.MIDDLE
            pb = tf_b.paragraphs[0]
            pb.text = "numenors"
            pb.font.name = "Calibri"
            pb.font.size = Pt(21)
            pb.font.bold = True
            pb.font.color.rgb = RGBColor(20, 20, 20)
            pb.alignment = PP_ALIGN.CENTER

        # 4. Slide Title (Slides 2 to 6)
        if title_text:
            tbox = slide.shapes.add_textbox(to_emu(200), to_emu(25), to_emu(940), to_emu(70))
            tf_t = tbox.text_frame
            pt = tf_t.paragraphs[0]
            pt.text = title_text
            pt.font.name = "Georgia"
            pt.font.size = Pt(36)
            pt.font.bold = True
            pt.font.color.rgb = RGBColor(15, 23, 42)
            pt.alignment = PP_ALIGN.CENTER

    # =============================================================
    # SLIDE 1: TITLE PAGE
    # =============================================================
    print("[1/6] Building Slide 1: Title Page...")
    s1 = prs.slides.add_slide(blank_layout)
    add_slide_frame(s1, 1, is_title_slide=True)

    # Top Title
    s1_title = s1.shapes.add_textbox(to_emu(170), to_emu(25), to_emu(960), to_emu(70))
    p = s1_title.text_frame.paragraphs[0]
    p.text = "SMART INDIA HACKATHON 2026"
    p.font.name = "Georgia"
    p.font.size = Pt(34)
    p.font.bold = True
    p.font.color.rgb = RGBColor(11, 83, 148)
    p.alignment = PP_ALIGN.CENTER

    # "TITLE PAGE"
    s1_sub = s1.shapes.add_textbox(to_emu(350), to_emu(130), to_emu(600), to_emu(60))
    p = s1_sub.text_frame.paragraphs[0]
    p.text = "TITLE PAGE"
    p.font.name = "Georgia"
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = RGBColor(15, 23, 42)
    p.alignment = PP_ALIGN.CENTER

    # Left Details Block
    s1_box = s1.shapes.add_textbox(to_emu(85), to_emu(210), to_emu(980), to_emu(500))
    tf1 = s1_box.text_frame
    tf1.word_wrap = True

    bullets = [
        ("Problem Statement ID –", "26055"),
        ("Problem Statement Title-", "Smart Scan Strategy for Electronic Warfare"),
        ("Theme-", "Robotics and Drones"),
        ("PS Category-", "Software"),
        ("Team ID-", "468750"),
        ("Team Name (Registered on portal)-", "numenors")
    ]

    for idx, (label, val) in enumerate(bullets):
        p = tf1.paragraphs[0] if idx == 0 else tf1.add_paragraph()
        p.space_after = Pt(22)
        r1 = p.add_run()
        r1.text = f"• {label} "
        r1.font.name = "Segoe UI"
        r1.font.size = Pt(21)
        r1.font.bold = True
        r1.font.color.rgb = RGBColor(15, 23, 42)

        r2 = p.add_run()
        r2.text = val
        r2.font.name = "Segoe UI"
        r2.font.size = Pt(21)
        r2.font.bold = False
        r2.font.color.rgb = RGBColor(30, 41, 59)

    # Right Bulb Graphic
    if sih_bulb_path.exists():
        s1.shapes.add_picture(
            str(sih_bulb_path),
            to_emu(1080), to_emu(175), to_emu(297), to_emu(480)
        )

    # =============================================================
    # SLIDE 2: PROPOSED SOLUTION
    # =============================================================
    print("[2/6] Building Slide 2: Proposed Solution...")
    s2 = prs.slides.add_slide(blank_layout)
    add_slide_frame(s2, 2, title_text="SENTINEL-EW")

    # Subtitle
    s2_sub = s2.shapes.add_textbox(to_emu(240), to_emu(74), to_emu(860), to_emu(38))
    p = s2_sub.text_frame.paragraphs[0]
    p.text = "Turning Wideband Spectrum Uncertainty into Predictive Intercept Intelligence"
    p.font.name = "Georgia"
    p.font.size = Pt(17)
    p.font.italic = False
    p.font.color.rgb = RGBColor(71, 85, 105)
    p.alignment = PP_ALIGN.CENTER

    # Left: "Proposed Solution" pill badge
    s2_pill = s2.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        to_emu(24), to_emu(126), to_emu(420), to_emu(44)
    )
    s2_pill.fill.solid()
    s2_pill.fill.fore_color.rgb = RGBColor(0, 85, 150)
    s2_pill.line.fill.background()
    s2_pill.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = s2_pill.text_frame.paragraphs[0]
    p.text = "Proposed Solution"
    p.font.name = "Georgia"
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = RGBColor(255, 255, 255)
    p.alignment = PP_ALIGN.CENTER

    # Left Main Card: 5 Bullets
    s2_card = s2.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        to_emu(24), to_emu(178), to_emu(770), to_emu(550)
    )
    s2_card.fill.solid()
    s2_card.fill.fore_color.rgb = RGBColor(255, 255, 255)
    s2_card.line.color.rgb = RGBColor(15, 23, 42)
    s2_card.line.width = Pt(2.5)

    tf2 = s2_card.text_frame
    tf2.word_wrap = True
    tf2.margin_left = to_emu(24)
    tf2.margin_right = to_emu(24)
    tf2.margin_top = to_emu(24)
    tf2.margin_bottom = to_emu(24)

    s2_bullets = [
        ("Dynamic Wideband Sweeping:", " Sweeps multi-GHz threat spectrums using narrow instantaneous bandwidth (IBW) receivers, replacing rigid open-loop schedules with closed-loop adaptive dwell allocation."),
        ("Non-Stationary Multi-Armed Bandits:", " Employs Discounted-UCB and EXP3 algorithms to dynamically learn emitter presence without requiring pre-mission intelligence databases."),
        ("Deep Q-Network (DQN) Scheduling:", " Reinforcement learning policy trained on 100,000+ radar pulse bursts, maximizing intercept probability (Pd) and achieving +32.36 cumulative reward."),
        ("Predictive Intercept Engine:", " Synchronizes receiver dwells with hostile rotating radar scan intervals, cutting lookahead intercept error down to 38.0 ms."),
        ("Closed-Loop Mission Intelligence & C2:", " Streams real-time Pulse Descriptor Words (PDWs), threat angle-of-arrival, and Figures of Merit over WebSockets to a tactical 360° PPI radar scope.")
    ]

    for idx, (head, body) in enumerate(s2_bullets):
        p = tf2.paragraphs[0] if idx == 0 else tf2.add_paragraph()
        p.space_after = Pt(14)
        p.line_spacing = 1.15
        
        r1 = p.add_run()
        r1.text = f"• {head}"
        r1.font.name = "Segoe UI"
        r1.font.size = Pt(14)
        r1.font.bold = True
        r1.font.color.rgb = RGBColor(15, 23, 42)

        r2 = p.add_run()
        r2.text = body
        r2.font.name = "Segoe UI"
        r2.font.size = Pt(14)
        r2.font.bold = False
        r2.font.color.rgb = RGBColor(51, 65, 85)

    # Right Top: Workflow Diagram
    wf_png = DIAG_DIR / "s2_workflow.png"
    if wf_png.exists():
        s2.shapes.add_picture(
            str(wf_png),
            to_emu(822), to_emu(126), to_emu(600), to_emu(350)
        )

    # Right Bottom: Innovation Cards
    inv_png = DIAG_DIR / "s2_innovation.png"
    if inv_png.exists():
        s2.shapes.add_picture(
            str(inv_png),
            to_emu(830), to_emu(484), to_emu(592), to_emu(244)
        )

    # =============================================================
    # SLIDE 3: TECHNICAL APPROACH
    # =============================================================
    print("[3/6] Building Slide 3: Technical Approach...")
    s3 = prs.slides.add_slide(blank_layout)
    add_slide_frame(s3, 3, title_text="TECHNICAL APPROACH")

    # Top Left: 4 Zones Architecture
    zones_png = DIAG_DIR / "s3_zones.png"
    if zones_png.exists():
        s3.shapes.add_picture(
            str(zones_png),
            to_emu(24), to_emu(116), to_emu(950), to_emu(522)
        )

    # Bottom Left: Tech Stack
    tech_png = DIAG_DIR / "s3_techstack.png"
    if tech_png.exists():
        s3.shapes.add_picture(
            str(tech_png),
            to_emu(24), to_emu(642), to_emu(950), to_emu(98)
        )

    # Right: Implementation Process
    proc_png = DIAG_DIR / "s3_process.png"
    if proc_png.exists():
        s3.shapes.add_picture(
            str(proc_png),
            to_emu(990), to_emu(116), to_emu(425), to_emu(624)
        )

    # =============================================================
    # SLIDE 4: FEASIBILITY AND VIABILITY
    # =============================================================
    print("[4/6] Building Slide 4: Feasibility and Viability...")
    s4 = prs.slides.add_slide(blank_layout)
    add_slide_frame(s4, 4, title_text="FEASIBILITY AND VIABILITY")

    # Top Row: 3 White Cards
    feas_png = DIAG_DIR / "s4_feasibility.png"
    if feas_png.exists():
        s4.shapes.add_picture(
            str(feas_png),
            to_emu(235), to_emu(100), to_emu(970), to_emu(280)
        )

    # Bottom Row: Challenges Hub-and-Spoke
    chal_png = DIAG_DIR / "s4_challenges.png"
    if chal_png.exists():
        s4.shapes.add_picture(
            str(chal_png),
            to_emu(140), to_emu(390), to_emu(1160), to_emu(340)
        )

    # =============================================================
    # SLIDE 5: IMPACT AND BENEFITS
    # =============================================================
    print("[5/6] Building Slide 5: Impact and Benefits...")
    s5 = prs.slides.add_slide(blank_layout)
    add_slide_frame(s5, 5, title_text="IMPACT AND BENEFITS")

    # Left: Stakeholders Hub-and-Spoke
    stk_png = DIAG_DIR / "s5_stakeholders.png"
    if stk_png.exists():
        s5.shapes.add_picture(
            str(stk_png),
            to_emu(45), to_emu(115), to_emu(755), to_emu(545)
        )

    # Right: Benefits Quote Cards
    ben_png = DIAG_DIR / "s5_benefits.png"
    if ben_png.exists():
        s5.shapes.add_picture(
            str(ben_png),
            to_emu(825), to_emu(115), to_emu(570), to_emu(545)
        )

    # Bottom Banner Quote
    banner_png = DIAG_DIR / "s5_banner.png"
    if banner_png.exists():
        s5.shapes.add_picture(
            str(banner_png),
            to_emu(45), to_emu(674), to_emu(1350), to_emu(60)
        )

    # =============================================================
    # SLIDE 6: RESEARCH AND REFERENCES
    # =============================================================
    print("[6/6] Building Slide 6: Research and References...")
    s6 = prs.slides.add_slide(blank_layout)
    add_slide_frame(s6, 6, title_text="RESEARCH  AND REFERENCES")

    # Large Content Card
    s6_box = s6.shapes.add_textbox(to_emu(70), to_emu(120), to_emu(1300), to_emu(600))
    tf6 = s6_box.text_frame
    tf6.word_wrap = True

    # Header 1
    p = tf6.paragraphs[0]
    p.text = "• Academic & Defence Research Sources"
    p.font.name = "Georgia"
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = RGBColor(15, 23, 42)
    p.space_after = Pt(10)

    refs = [
        ("Defence Research & Development Organisation (DRDO / DLRL) – Electronic Support Measures (ESM) receiver architecture, wideband search strategies, and Figures of Merit standards.",
         "https://www.drdo.gov.in/drdo/labs-and-establishments/defence-electronics-research-laboratory-dlrl"),
        ("JC Wise (2024) – Alan Turing Institute Radar Emitter Dataset: High-fidelity synthetic radar pulse trains and agile emitter classification benchmarks.",
         "https://huggingface.co/datasets/jcwise/radar-emitter-database"),
        ("P. Auer, N. Cesa-Bianchi, P. Fischer (2002) / A. Garivier & E. Moulines (2011) – Non-Stationary Multi-Armed Bandits: The Discounted-UCB and EXP3 algorithms for dynamic environments.",
         "https://arxiv.org/abs/0805.3415"),
        ("V. Mnih et al. (2015) – Nature: Human-level control through deep reinforcement learning (DQN application to cognitive sensor scheduling).",
         "https://www.nature.com/articles/nature14236")
    ]

    for title, url in refs:
        p_t = tf6.add_paragraph()
        p_t.text = f"• {title}"
        p_t.font.name = "Segoe UI"
        p_t.font.size = Pt(14)
        p_t.font.bold = True
        p_t.font.color.rgb = RGBColor(15, 23, 42)
        p_t.space_after = Pt(2)

        p_u = tf6.add_paragraph()
        p_u.text = url
        p_u.font.name = "Segoe UI"
        p_u.font.size = Pt(13)
        p_u.font.color.rgb = RGBColor(2, 132, 199)
        p_u.space_after = Pt(12)

    # Header 2: Links to Project
    p_lp = tf6.add_paragraph()
    p_lp.space_before = Pt(14)
    p_lp.text = "LINKS TO PROJECT:"
    p_lp.font.name = "Georgia"
    p_lp.font.size = Pt(20)
    p_lp.font.bold = True
    p_lp.font.color.rgb = RGBColor(15, 23, 42)
    p_lp.space_after = Pt(6)

    p_repo = tf6.add_paragraph()
    r_lbl = p_repo.add_run()
    r_lbl.text = "Repository link: "
    r_lbl.font.bold = True
    r_lbl.font.size = Pt(15)
    r_url = p_repo.add_run()
    r_url.text = "https://github.com/krishdeshpande/drdo-ew-smart-scan.git"
    r_url.font.size = Pt(15)
    r_url.font.color.rgb = RGBColor(2, 132, 199)
    p_repo.space_after = Pt(4)

    p_live = tf6.add_paragraph()
    l_lbl = p_live.add_run()
    l_lbl.text = "Live Tactical C2 Prototype: "
    l_lbl.font.bold = True
    l_lbl.font.size = Pt(15)
    l_url = p_live.add_run()
    l_url.text = "http://localhost:8080/dashboard.html"
    l_url.font.size = Pt(15)
    l_url.font.color.rgb = RGBColor(2, 132, 199)

    # Save Presentation
    prs.save(str(OUTPUT_PPTX))
    print(f"SUCCESS: Presentation created at {OUTPUT_PPTX} ({OUTPUT_PPTX.stat().st_size} bytes)")

if __name__ == "__main__":
    create_presentation()

