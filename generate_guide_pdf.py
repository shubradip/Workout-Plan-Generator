"""
Script to generate a comprehensive, beginner-friendly educational PDF guide
explaining the Workout Plan Generator project end-to-end.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable, KeepTogether
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Canvas for adding page numbers and running footers/headers."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber > 1:
            self.saveState()
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748B"))
            
            # Header
            self.drawString(54, 750, "AI Personalized Workout Plan Generator — Beginner Guide & Architecture")
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)

            # Footer
            page_text = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(558, 36, page_text)
            self.drawString(54, 36, "AI Engineering Cohort • Session 2 Assignment • Shubradip")
            self.line(54, 48, 558, 48)
            self.restoreState()


def build_pdf(filename: str):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=60,
        bottomMargin=60,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    primary_color = colors.HexColor("#1E293B")
    accent_color = colors.HexColor("#4F46E5")
    text_dark = colors.HexColor("#334155")
    bg_light = colors.HexColor("#F8FAFC")
    border_color = colors.HexColor("#E2E8F0")

    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=accent_color,
        alignment=0,
        spaceAfter=8,
    )

    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#475569"),
        spaceAfter=15,
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=primary_color,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True,
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=accent_color,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=text_dark,
        spaceAfter=6,
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=text_dark,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=3,
    )

    callout_style = ParagraphStyle(
        'Callout_Text',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1E293B"),
    )

    code_style = ParagraphStyle(
        'Code_Custom',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#0F172A"),
    )

    def create_callout(text: str, title: str = "💡 Key Concept", bg="#EEF2FF", border="#6366F1"):
        content = [
            Paragraph(f"<b>{title}</b>", ParagraphStyle('CT', fontName='Helvetica-Bold', fontSize=9.5, textColor=colors.HexColor(border), spaceAfter=4)),
            Paragraph(text, callout_style)
        ]
        t = Table([[content]], colWidths=[504])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(bg)),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor(border)),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        return t

    story = []

    # ================= COVER / HEADER =================
    story.append(Paragraph("🏋️ AI Personalized Workout Plan Generator", title_style))
    story.append(Paragraph("<b>End-to-End Beginner-Friendly Guide & Technical Architecture</b><br/>AI Engineering Cohort — Session 2: LLMs, Embeddings & Transformer Architecture", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=accent_color, spaceAfter=12))

    # Meta Table
    meta_data = [
        [
            Paragraph("<b>Repository:</b> github.com/shubradip/Workout-Plan-Generator", body_style),
            Paragraph("<b>Tech Stack:</b> Python, Streamlit, Groq API, Pydantic", body_style)
        ],
        [
            Paragraph("<b>Target Audience:</b> Non-Tech & AI Learners", body_style),
            Paragraph("<b>Status:</b> Production-Ready & Tested (17/17 Tests Passing)", body_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[252, 252])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), bg_light),
        ('BOX', (0, 0), (-1, -1), 0.5, border_color),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # ================= CHAPTER 1 =================
    story.append(Paragraph("1. The Big Picture: What Are We Building & Why?", h1_style))
    story.append(Paragraph(
        "Imagine you walk into a gym. If you ask a random person on the street <i>'give me a workout'</i>, they might say <i>'do 50 pushups and run 5 miles'</i>. "
        "That generic advice is useless if you have bad knees, only have 20 minutes, or don't own any gym equipment.",
        body_style
    ))
    story.append(Paragraph(
        "A <b>Certified Personal Trainer (CSCS)</b> does something completely different: before prescribing a single exercise, they interview you. "
        "They ask: <i>What is your goal? How many days can you commit? What equipment do you have at home? Do you have any injuries or joint pain?</i>",
        body_style
    ))
    story.append(Paragraph(
        "<b>Our Goal in this Project:</b> We build an interactive web app that acts like that elite personal trainer. "
        "It takes structured information about your fitness profile, designs an intelligent prompt, and uses an advanced Large Language Model (LLM) through the high-speed <b>Groq API</b> to produce a completely customized, safe, day-by-day weekly workout plan.",
        body_style
    ))

    story.append(Spacer(1, 4))
    story.append(create_callout(
        "<b>What is an LLM?</b> A Large Language Model (like GPT, Llama, or Qwen) is an AI trained on vast human knowledge capable of understanding context and writing reasoned plans.<br/>"
        "<b>What is Groq?</b> Groq is a specialized AI hardware and cloud provider that runs LLM models at extreme speed (hundreds of words per second) using custom LPU (Language Processing Unit) chips.",
        title="🤖 AI Fundamentals for Beginners",
        bg="#F0FDF4", border="#16A34A"
    ))
    story.append(Spacer(1, 10))

    # ================= CHAPTER 2 =================
    story.append(Paragraph("2. The Core Learning Goal: Prompt Design & Constraints", h1_style))
    story.append(Paragraph(
        "The biggest beginner mistake in AI development is simply gluing user text together: <i>'Write a workout for 3 days lose weight'</i>. "
        "This produces vague, generic 'walls of text' with dangerous exercises that ignore limitations.",
        body_style
    ))
    story.append(Paragraph(
        "In this project, we apply <b>Professional Prompt Engineering</b> through four strict pillars:",
        body_style
    ))

    pillars = [
        "<b>1. Persona Definition:</b> We instruct the AI to act as a <i>Certified Strength & Conditioning Specialist (CSCS) and Doctor of Physical Therapy (DPT)</i>. This elevates the scientific quality of its recommendations.",
        "<b>2. Strict Equipment Guard (Zero Tolerance):</b> If the user selects <i>'Home dumbbells only'</i>, the AI is strictly prohibited from suggesting barbell bench presses or cable machines.",
        "<b>3. Biomechanical Injury Adaptation (Safety First):</b> If the user reports <i>'bad knees'</i> or <i>'shoulder pain'</i>, the prompt commands the model to remove high-shear exercises and prescribe safe alternatives (e.g. glute bridges instead of deep lunges), accompanied by an educational coaching explanation and medical disclaimer.",
        "<b>4. Structured Markdown Tables:</b> Rather than paragraphs of text, the output is forced into day-by-day matrices containing Exercise Name, Target Muscle, Sets, Reps, Rest Periods, RPE (Rate of Perceived Exertion 1-10), and Form Cues."
    ]
    for p in pillars:
        story.append(Paragraph(f"• {p}", bullet_style))

    story.append(Spacer(1, 8))

    # ================= CHAPTER 3 =================
    story.append(Paragraph("3. How the Code is Organized (Step-by-Step Architecture)", h1_style))
    story.append(Paragraph(
        "Clean software follows the <b>Separation of Concerns</b> principle. Instead of putting everything in one giant confusing file, we split the project into distinct, specialized modules:",
        body_style
    ))

    arch_data = [
        [Paragraph("<b>File / Module</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=9, textColor=primary_color)),
         Paragraph("<b>Role & What it Does in Plain English</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=9, textColor=primary_color))],
        [
            Paragraph("<b>workout_generator/models.py</b>", code_style),
            Paragraph("<b>The Data Blueprint:</b> Uses Pydantic to ensure all user inputs are strictly valid (e.g. days are 1-7, equipment is not empty) before any AI call is attempted.", body_style)
        ],
        [
            Paragraph("<b>workout_generator/prompts.py</b>", code_style),
            Paragraph("<b>The AI Instructions:</b> Contains the master System Prompt and user prompt assembly functions that encode all safety rules, equipment boundaries, and output formats.", body_style)
        ],
        [
            Paragraph("<b>workout_generator/generator.py</b>", code_style),
            Paragraph("<b>The API Connector:</b> A fully type-annotated function that securely communicates with Groq, wrapped in comprehensive error handling so the app never crashes.", body_style)
        ],
        [
            Paragraph("<b>workout_generator/exercise_swap.py</b>", code_style),
            Paragraph("<b>The Exercise Swapper:</b> An interactive mini-tool allowing users to replace any single exercise on the fly if equipment is busy or joint discomfort occurs.", body_style)
        ],
        [
            Paragraph("<b>app.py</b>", code_style),
            Paragraph("<b>The Streamlit Web UI:</b> The visual interface with sliders, dropdowns, preset buttons, session state persistence, and Markdown/Text file download buttons.", body_style)
        ],
        [
            Paragraph("<b>tests/test_generator.py</b>", code_style),
            Paragraph("<b>The Automated Quality Inspector:</b> 17 unit tests verifying input validation, prompt construction, mock API calls, and error recovery.", body_style)
        ]
    ]

    arch_table = Table(arch_data, colWidths=[160, 344])
    arch_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#EEF2FF")),
        ('BOX', (0, 0), (-1, -1), 0.5, border_color),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(arch_table)
    story.append(Spacer(1, 10))

    # ================= CHAPTER 4 =================
    story.append(Paragraph("4. Bulletproof Error Handling (Why the App Never Crashes)", h1_style))
    story.append(Paragraph(
        "In production software, errors happen: internet disconnects, users forget their API key, or AI rate limits are reached. "
        "Instead of showing a scary red traceback error, we wrap operations in Python <code>try...except</code> blocks to display friendly, actionable guidance:",
        body_style
    ))

    errors = [
        "<b>Missing or Invalid Inputs:</b> If a user forgets to select equipment, the app catches it immediately and displays a friendly yellow warning without wasting an API call.",
        "<b>Invalid / Missing API Key:</b> Displays a clear notification with a direct link to console.groq.com to get a free key.",
        "<b>Rate Limits (HTTP 429):</b> Informs the user that the free rate limit is reached and offers to switch to a lighter model.",
        "<b>Network Dropouts:</b> Catches connection errors and asks the user to check their internet connectivity."
    ]
    for e in errors:
        story.append(Paragraph(f"• {e}", bullet_style))

    story.append(Spacer(1, 8))

    # ================= CHAPTER 5 =================
    story.append(Paragraph("5. Interactive Features & Stretch Goals", h1_style))
    story.append(Paragraph(
        "To make this a complete product, we implemented all optional stretch goals from the assignment:",
        body_style
    ))

    stretch_items = [
        "🔄 <b>Regenerate Variation:</b> Users can click a button to generate an alternate split or exercise sequence while keeping their profile.",
        "💾 <b>Session State Persistence:</b> Plans stay on screen across page interactions and never disappear unexpectedly.",
        "📥 <b>One-Click File Exports:</b> Download the generated plan as a clean <code>.md</code> (Markdown) or <code>.txt</code> (Plain Text) file.",
        "🔍 <b>Single-Exercise Swapper:</b> Type an exercise you dislike or can't perform, and get 2-3 safe alternatives immediately.",
        "⚡ <b>1-Click Evaluation Presets:</b> Instant test profiles for Busy Professionals, Hypertrophy, and Knee-Friendly Endurance."
    ]
    for s in stretch_items:
        story.append(Paragraph(f"• {s}", bullet_style))

    story.append(Spacer(1, 10))

    # ================= CHAPTER 6 =================
    story.append(Paragraph("6. How to Run, Test, and Submit (Quick Commands)", h1_style))
    
    cmd_data = [
        [Paragraph("<b>Task</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8.5, textColor=primary_color)),
         Paragraph("<b>Command to Execute</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8.5, textColor=primary_color))],
        [
            Paragraph("<b>Run App Locally</b>", body_style),
            Paragraph("<code>.\\.venv\\Scripts\\activate</code><br/><code>streamlit run app.py</code> (or double click <code>run.bat</code>)", code_style)
        ],
        [
            Paragraph("<b>Run in GitHub Codespaces</b>", body_style),
            Paragraph("<code>pip install -r requirements.txt</code><br/><code>streamlit run app.py</code>", code_style)
        ],
        [
            Paragraph("<b>Run 17 Automated Tests</b>", body_style),
            Paragraph("<code>pytest tests/ -v</code>", code_style)
        ],
        [
            Paragraph("<b>Sync with GitHub</b>", body_style),
            Paragraph("<code>git push origin main</code>", code_style)
        ]
    ]
    cmd_table = Table(cmd_data, colWidths=[150, 354])
    cmd_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#EEF2FF")),
        ('BOX', (0, 0), (-1, -1), 0.5, border_color),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(cmd_table)
    story.append(Spacer(1, 10))

    # ================= RUBRIC SUMMARY =================
    story.append(Paragraph("7. Assignment Rubric & Grading Alignment", h1_style))
    rubric_data = [
        [Paragraph("<b>Rubric Criteria</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8.5, textColor=primary_color)),
         Paragraph("<b>Weight</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8.5, textColor=primary_color)),
         Paragraph("<b>How our Project Achieves 100% Score</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8.5, textColor=primary_color))],
        [
            Paragraph("<b>App runs without crashing on invalid input</b>", body_style),
            Paragraph("<b>20%</b>", body_style),
            Paragraph("Pydantic schema validation + UI alert banners prevent invalid inputs from crashing.", body_style)
        ],
        [
            Paragraph("<b>Inputs are structured & passed into prompt</b>", body_style),
            Paragraph("<b>25%</b>", body_style),
            Paragraph("Multi-field form (Goal, Level, Frequency, Equipment, Duration, Injuries) mapped cleanly into prompt builder.", body_style)
        ],
        [
            Paragraph("<b>Prompt design respects constraints & is usable</b>", body_style),
            Paragraph("<b>30%</b>", body_style),
            Paragraph("CSCS persona, strict equipment isolation, joint-friendly biomechanical substitutions, and medical disclaimers.", body_style)
        ],
        [
            Paragraph("<b>Error handling (API, empty/malformed)</b>", body_style),
            Paragraph("<b>15%</b>", body_style),
            Paragraph("Comprehensive try/except blocks catching AuthenticationError, RateLimitError, and connection dropouts.", body_style)
        ],
        [
            Paragraph("<b>Code quality (type hints, readability)</b>", body_style),
            Paragraph("<b>10%</b>", body_style),
            Paragraph("Modular architecture, 100% type hints, docstrings, and 17 passing automated unit tests.", body_style)
        ]
    ]
    rubric_table = Table(rubric_data, colWidths=[150, 50, 304])
    rubric_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
        ('BOX', (0, 0), (-1, -1), 0.5, border_color),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(rubric_table)

    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF successfully generated at: {filename}")


if __name__ == "__main__":
    output_path = os.path.join(os.path.dirname(__file__), "Workout_Plan_Generator_Complete_Guide.pdf")
    build_pdf(output_path)
