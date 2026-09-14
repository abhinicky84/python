# ─── INSTALL FIRST ─────────────────────────────────────────────────────────
# pip install python-pptx
# ───────────────────────────────────────────────────────────────────────────

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

# ─── COLORS ────────────────────────────────────────────────────────────────
DELL_DARK   = RGBColor(0,   45,  98)
DELL_BLUE   = RGBColor(0,  118, 206)
ACCENT      = RGBColor(0,  163, 224)
WHITE       = RGBColor(255, 255, 255)
LIGHT_GRAY  = RGBColor(245, 247, 250)
MID_GRAY    = RGBColor(200, 210, 220)
DARK_GRAY   = RGBColor(60,   70,  80)
TEXT_COLOR  = RGBColor(15,   23,  42)
MUTED       = RGBColor(91,  107, 133)
GREEN       = RGBColor(22,  163,  74)
ORANGE      = RGBColor(234,  88,  12)
YELLOW_BG   = RGBColor(255, 243, 205)
YELLOW_TXT  = RGBColor(120,  70,   0)
RED_ACCENT  = RGBColor(200,  40,  80)
PURPLE      = RGBColor(120,  60, 180)
TEAL        = RGBColor(0,   160, 140)
MS_BLUE     = RGBColor(0,   120, 212)
BLUE_TINT   = RGBColor(230, 240, 255)

# ─── PRESENTATION SETUP ────────────────────────────────────────────────────
prs = Presentation()
prs.slide_width  = Inches(13.33)
prs.slide_height = Inches(7.5)

# ─── HELPER FUNCTIONS ──────────────────────────────────────────────────────
def new_slide():
    layout = prs.slide_layouts[6]           # Blank layout
    return prs.slides.add_slide(layout)

def add_rect(slide, l, t, w, h, fill_rgb, border_rgb=None, border_pt=0.5):
    shape = slide.shapes.add_shape(
        1,                                  # 1 = Rectangle
        Inches(l), Inches(t), Inches(w), Inches(h)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_rgb
    if border_rgb:
        shape.line.color.rgb = border_rgb
        shape.line.width = Pt(border_pt)
    else:
        shape.line.fill.background()
    return shape

def add_oval(slide, l, t, w, h, fill_rgb):
    shape = slide.shapes.add_shape(
        9,                                  # 9 = Oval
        Inches(l), Inches(t), Inches(w), Inches(h)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_rgb
    shape.line.fill.background()
    return shape

def add_txt(slide, text, l, t, w, h, size,
        bold=False, italic=False,
        color=None, align=PP_ALIGN.LEFT, wrap=True):
    if color is None:
        color = TEXT_COLOR
    txb = slide.shapes.add_textbox(
        Inches(l), Inches(t), Inches(w), Inches(h)
    )
    tf = txb.text_frame
    tf.word_wrap = wrap
    para = tf.paragraphs[0]
    para.alignment = align
    run = para.add_run()
    run.text           = text
    run.font.size      = Pt(size)
    run.font.bold      = bold
    run.font.italic    = italic
    run.font.color.rgb = color
    return txb

def build_header(slide, eyebrow, title, subtitle, bar_color, num):
    add_rect(slide, 0, 0, 13.33, 7.5,  LIGHT_GRAY)
    add_rect(slide, 0, 0, 13.33, 1.12, DELL_DARK)
    add_rect(slide, 0, 1.12, 0.06, 6.38, bar_color)
    add_txt(slide, eyebrow,  0.25, 0.10, 11.0, 0.28, 8,
            bold=True, color=ACCENT)
    add_txt(slide, title,    0.25, 0.36, 10.0, 0.62, 24,
            bold=True, color=WHITE)
    add_txt(slide, subtitle, 0.25, 0.80, 12.5, 0.28, 9.5,
            color=RGBColor(180, 210, 240))
    add_txt(slide, f"{num} / 5", 12.1, 0.42, 1.0, 0.28, 10,
            color=RGBColor(180, 210, 240), align=PP_ALIGN.RIGHT)

def build_col_headers(slide):
    col_x = [0.30, 3.80, 5.10, 6.60]
    col_w = [3.30, 1.10, 1.30, 6.30]
    labels = ["Tool / Framework", "Version", "License", "Role & Notes"]
    add_rect(slide, 0.25, 1.22, 12.80, 0.38, DELL_BLUE)
    for i, label in enumerate(labels):
        add_txt(slide, label, col_x[i], 1.27, col_w[i], 0.30, 10,
                bold=True, color=WHITE)
    return col_x, col_w

def build_rows(slide, data, col_x, col_w):
    fills = [WHITE, LIGHT_GRAY]
    for i, row in enumerate(data):
        y = 1.62 + i * 0.378
        add_rect(slide, 0.25, y, 12.80, 0.365,
                 fills[i % 2], border_rgb=MID_GRAY, border_pt=0.4)
        for j, cell in enumerate(row):
            add_txt(slide, cell, col_x[j], y + 0.04,
                    col_w[j], 0.30, 9, bold=(j == 0), color=TEXT_COLOR)

def build_footer(slide, note):
    add_rect(slide, 0.25, 7.14, 12.80, 0.29,
             BLUE_TINT, border_rgb=DELL_BLUE, border_pt=0.5)
    add_txt(slide, note, 0.38, 7.17, 12.50, 0.24, 8,
            italic=True, color=MUTED)

# ═══════════════════════════════════════════════════════════════════════════
# SLIDE 1 — TITLE
# ═══════════════════════════════════════════════════════════════════════════
s1 = new_slide()

add_rect(s1, 0, 0, 13.33, 7.5, DELL_DARK)
add_rect(s1, 0, 0,    13.33, 0.07, ACCENT)
add_rect(s1, 0, 7.43, 13.33, 0.07, ACCENT)

add_oval(s1,  9.4, -1.1, 6.2, 6.2, RGBColor(0, 70, 140))
add_oval(s1, 10.6,  3.2, 4.2, 4.2, RGBColor(0, 50, 110))

add_txt(s1, "PREPARED BY WPP  |  FOR DELL TECHNOLOGIES",
    0.7, 0.48, 9.0, 0.28, 8.5, bold=True, color=ACCENT)

add_txt(s1, "Technology &",
    0.7, 1.15, 10.0, 0.98, 54, bold=True, color=WHITE)

add_txt(s1, "AI Tooling Overview",
    0.7, 2.10, 10.0, 0.98, 54, bold=True, color=ACCENT)

add_txt(s1,
    "Bill of Materials  |  AI Governance Framework  |  Dell Approval Requirements",
    0.7, 3.18, 10.0, 0.42, 16, color=RGBColor(180, 210, 240))

add_rect(s1, 0.7, 3.72, 5.0, 0.05, ACCENT)

add_txt(s1,
    "Dell Digital Experience Platform  |  Contentstack Migration Engagement",
    0.7, 3.88, 10.0, 0.34, 13, color=RGBColor(180, 210, 240))

add_rect(s1, 0.65, 5.65, 9.0, 1.0,
     RGBColor(0, 28, 65),
     border_rgb=RGBColor(255, 200, 0), border_pt=1.2)

add_txt(s1,
    "ALL AI TOOLS REQUIRE EXPLICIT DELL OPT-IN APPROVAL PRIOR TO USAGE",
    0.90, 5.75, 8.5, 0.35, 11, bold=True,
    color=RGBColor(255, 220, 80))

add_txt(s1,
    "Governed by RFP Section 16. No tool is activated without written Dell sign-off.",
    0.90, 6.12, 8.5, 0.35, 10,
    color=RGBColor(255, 220, 80))

add_txt(s1, "1 / 5", 12.1, 7.1, 1.0, 0.28, 10,
    color=RGBColor(130, 160, 200), align=PP_ALIGN.RIGHT)

# ═══════════════════════════════════════════════════════════════════════════
# SLIDE 2 — FRONTEND & TESTING BOM
# ═══════════════════════════════════════════════════════════════════════════
s2 = new_slide()

build_header(s2,
"TECHNOLOGY BILL OF MATERIALS  —  SLIDE 2 OF 5",
"Frontend, Testing & Integration Stack",
"Core frameworks and libraries. Open-source under permissive licenses unless noted.",
DELL_BLUE, 2)

col_x, col_w = build_col_headers(s2)

frontend_rows = [
("React",                 "19.2.1",  "MIT",          "Core UI library for component-based interface development"),
("Next.js",               "16.2.6",  "MIT",          "React framework — SSR, SSG, ISR for SEO-optimized delivery"),
("TypeScript",            "5.4",     "Apache 2.0",   "Strongly typed JS for maintainability at team scale"),
("Tailwind CSS",          "3.4",     "MIT",          "Utility-first CSS aligned to Dell design system tokens"),
("Jest",                  "29.7",    "MIT",          "Unit and integration testing framework"),
("React Testing Library", "16",      "MIT",          "Component testing with an accessibility-first approach"),
("Playwright",            "1.44",    "Apache 2.0",   "End-to-end browser automation and regression testing"),
("axe-core",              "4.9",     "MPL 2.0",      "Automated WCAG accessibility compliance validation"),
("next-i18next",          "16.0.5",  "MIT",          "Internationalization for multilingual Dell.com experiences"),
("Apollo Client",         "4.2.0",   "MIT",          "GraphQL state management for local and remote data"),
("Apollo Server",         "5.1.0",   "MIT",          "GraphQL server — widely adopted for content API layer"),
("Contentstack JS SDK",   "3.27.0",  "MIT",          "Official SDK for Contentstack content delivery APIs"),
]

build_rows(s2, frontend_rows, col_x, col_w)

build_footer(s2,
"MIT = free commercial use. Apache 2.0 & MPL 2.0 require attribution. "
"Full license obligations to be reviewed with Dell Legal before deployment.")

# ═══════════════════════════════════════════════════════════════════════════
# SLIDE 3 — INFRASTRUCTURE & CLOUD BOM
# ═══════════════════════════════════════════════════════════════════════════
s3 = new_slide()

build_header(s3,
"TECHNOLOGY BILL OF MATERIALS  —  SLIDE 3 OF 5",
"Infrastructure, Cloud & DevOps Stack",
"Cloud services, CI/CD, observability, and connectors — pending Dell cloud environment confirmation.",
ACCENT, 3)

col_x, col_w = build_col_headers(s3)

infra_rows = [
("Terraform",                       "1.15.x",   "BSL v1.1",          "Core IaC tool for provisioning all cloud resources"),
("GitLab CI/CD",                    "18.11.x",  "Commercial/MIT",    "Dell-approved CI/CD for IaC, middleware & frontend deploys"),
("Azure App Service / AWS Fargate", "Managed",  "Azure/AWS Agmt.",   "PaaS hosting for containerised frontends & Node.js services"),
("Azure Service Bus / AWS SQS",     "Managed",  "Azure/AWS Agmt.",   "Managed message broker for async event-driven workflows"),
("Azure Functions / AWS Lambda",    "Managed",  "Azure/AWS Agmt.",   "Serverless compute for event-driven automation & tasks"),
("Azure Cache / AWS ElastiCache",   "Redis 8.x","Azure/AWS Agmt.",   "Distributed caching layer for performance optimisation"),
("Azure Blob / Amazon S3",          "Managed",  "Azure/AWS Agmt.",   "Object storage for IaC state, backups, and static assets"),
("Azure Key Vault / AWS KMS",       "Managed",  "Azure/AWS Agmt.",   "Centralised secrets, tokens & encryption key management"),
("Azure Monitor / AWS CloudWatch",  "Managed",  "Azure/AWS Agmt.",   "Native cloud observability and alerting"),
("Datadog Agent",                   "7.78.3",   "Apache 2.0/Comm.",  "Advanced APM & infrastructure monitoring (if Dell approved)"),
("Akamai EdgeGrid",                 "Managed",  "Akamai ToS",        "CDN and edge security — fully managed service"),
("Contentstack Mgmt API SDK",       "1.30.2",   "MIT",               "Content management automation via Contentstack APIs"),
]

build_rows(s3, infra_rows, col_x, col_w)

build_footer(s3,
"Azure vs. AWS finalised based on Dell preferred cloud environment. "
"All services governed by existing enterprise agreements. Terraform BSL v1.1 to be reviewed with Dell Legal.")

# ═══════════════════════════════════════════════════════════════════════════
# SLIDE 4 — AI TOOLS (3x3 CARD GRID)
# ═══════════════════════════════════════════════════════════════════════════
s4 = new_slide()

build_header(s4,
"AI GOVERNANCE & DISCLOSURE  —  SLIDE 4 OF 5",
"AI Tools & How They Will Be Used for Dell",
"All 9 tools require explicit Dell opt-in per RFP Section 16. No Dell PII or proprietary data transmitted.",
GREEN, 4)

ai_cards = [
("Claude Code",
 "Code Generation & Review",
 "Senior engineer reviews all AI output before merge. "
 "No PII, credentials, or Dell data in prompts. Usage logged.",
 DELL_BLUE),
("Cursor",
 "AI-Assisted Development",
 "Engineers accountable for all AI output. "
 "Code context only — no business data or credentials transmitted.",
 DELL_BLUE),
("Figma MCP",
 "Design-to-Code Accuracy",
 "Pulls design tokens from Dell Figma files locally. "
 "No design data leaves the local engineer environment.",
 PURPLE),
("GitLab MCP",
 "Repo & Pipeline Management",
 "Follows Dell GitLab governance. "
 "No code merged without passing all CI/CD pipeline gates.",
 ORANGE),
("Playwright MCP",
 "Browser Automation Testing",
 "LLM-driven automation via structured accessibility snapshots. "
 "Works with VS Code and Cursor — no vision models required.",
 TEAL),
("Next.js MCP",
 "Dev Tools & Faster Debugging",
 "Dev tooling for quicker development cycles "
 "and accelerated debugging workflows.",
 DELL_BLUE),
("WPP Open",
 "Marketing & Delivery AI OS",
 "Proprietary WPP platform for requirements refinement, "
 "test case generation, and tooling recommendations.",
 RED_ACCENT),
("Microsoft Copilot",
 "Meeting Productivity",
 "Teams AI for meeting summaries and live translation. "
 "No project or confidential data shared externally.",
 MS_BLUE),
("Gradial",
 "Content Migration AI",
 "Multi-agent CMS migration — scrapes, maps, ingests, and "
 "validates content at scale into Contentstack.",
 TEAL),
]

CARD_W = 4.10
CARD_H = 1.54
GAP_X  = 0.12
GAP_Y  = 0.12
OX     = 0.25
OY     = 1.22

for idx, (name, role, desc, color) in enumerate(ai_cards):
    col = idx % 3
    row = idx // 3
    cx  = OX + col * (CARD_W + GAP_X)
    cy  = OY + row * (CARD_H + GAP_Y)

    add_rect(s4, cx, cy, CARD_W, CARD_H,
             WHITE, border_rgb=MID_GRAY, border_pt=0.5)
    add_rect(s4, cx, cy, CARD_W, 0.07, color)

    add_txt(s4, name,
            cx + 0.12, cy + 0.10, CARD_W - 0.18, 0.30,
            12, bold=True, color=color)

    add_rect(s4, cx + 0.12, cy + 0.42, CARD_W - 0.26, 0.22,
             RGBColor(235, 245, 255), border_rgb=MID_GRAY, border_pt=0.3)
    add_txt(s4, role,
            cx + 0.16, cy + 0.44, CARD_W - 0.34, 0.18,
            8, bold=True, color=DARK_GRAY)

    add_txt(s4, desc,
            cx + 0.12, cy + 0.68, CARD_W - 0.22, 0.80,
            8.5, color=MUTED)

add_rect(s4, 0.25, 7.10, 12.80, 0.33,
     YELLOW_BG, border_rgb=RGBColor(200, 150, 0), border_pt=1.0)
add_txt(s4,
    "DELL APPROVAL REQUIRED:  All 9 AI tools require individual "
    "Dell opt-in sign-off prior to any usage on this engagement (RFP Section 16).",
    0.42, 7.14, 12.50, 0.26, 10, bold=True, color=YELLOW_TXT)

# ═══════════════════════════════════════════════════════════════════════════
# SLIDE 5 — GOVERNANCE & DELL APPROVAL FRAMEWORK
# ═══════════════════════════════════════════════════════════════════════════
s5 = new_slide()

build_header(s5,
"AI GOVERNANCE SUMMARY  —  SLIDE 5 OF 5",
"Governance, Compliance & Dell Approval Framework",
"How we ensure responsible AI usage and maintain Dell's trust throughout the engagement.",
RED_ACCENT, 5)

pillars = [
("Dell Opt-In First", DELL_BLUE, [
    "No AI tool activated without explicit written Dell approval",
    "All tools governed by RFP Section 16 — individual opt-in required",
    "Approval confirmed before any tool enters production use",
]),
("Data Protection", GREEN, [
    "Zero PII, credentials, or Dell proprietary data in any AI prompt",
    "Code context only — no business logic or confidential data",
    "All AI usage logged and available for Dell audit on request",
]),
("Human Oversight", RED_ACCENT, [
    "All AI-generated code reviewed by senior engineer before merge",
    "Tech Lead & Architect conduct periodic AI output reviews",
    "Engineers remain fully accountable for every deliverable",
]),
("Transparency & Audit", ORANGE, [
    "Full disclosure of all AI tools, models, and services upfront",
    "Usage logs maintained — accessible to Dell at any time",
    "AI-generated content flagged in documentation where applicable",
]),
]

CW2 = 3.10
CH2 = 4.50
G2  = 0.14
PX  = 0.25
PY  = 1.25

for i, (title, color, points) in enumerate(pillars):
    cx = PX + i * (CW2 + G2)

    add_rect(s5, cx, PY, CW2, CH2,
             WHITE, border_rgb=MID_GRAY, border_pt=0.5)
    add_rect(s5, cx, PY, CW2, 0.09, color)

    add_oval(s5, cx + 0.13, PY + 0.18, 0.38, 0.38, color)
    add_txt(s5, str(i + 1),
            cx + 0.19, PY + 0.22, 0.26, 0.28,
            11, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

    add_txt(s5, title,
            cx + 0.60, PY + 0.19, CW2 - 0.72, 0.36,
            12, bold=True, color=color)

    for j, point in enumerate(points):
        py = PY + 0.70 + j * 1.20
        add_rect(s5, cx + 0.14, py, CW2 - 0.28, 1.08,
                 LIGHT_GRAY, border_rgb=MID_GRAY, border_pt=0.3)
        add_rect(s5, cx + 0.14, py, 0.05, 1.08, color)
        add_txt(s5, point,
                cx + 0.26, py + 0.12, CW2 - 0.44, 0.84,
                9.5, color=DARK_GRAY)

add_rect(s5, 0.25, 5.88, 12.80, 1.50,
     DELL_DARK, border_rgb=ACCENT, border_pt=1.0)

add_txt(s5, "ENGAGEMENT SUMMARY",
    0.50, 5.95, 5.0, 0.28, 10, bold=True, color=ACCENT)

summary_lines = [
"  9 AI tools fully disclosed — all require individual Dell opt-in per RFP Section 16",
"  30+ technologies in BOM — open-source or covered by enterprise agreements",
"  Zero tolerance for AI processing Dell PII, credentials, or confidential data",
"  Full audit trail maintained — AI usage logs available to Dell at any time",
]

for i, line in enumerate(summary_lines):
    col = i % 2
    row = i // 2
    add_txt(s5, line,
            0.50 + col * 6.35,
            6.28 + row * 0.49,
            6.10, 0.42,
            9.5, color=WHITE)

# ─── SAVE ──────────────────────────────────────────────────────────────────
output_file = "Dell_Technology_BOM_AI_Governance.pptx"
prs.save(output_file)
print(f"\nSaved successfully: {output_file}")
print("Open with Microsoft PowerPoint or Google Slides.")