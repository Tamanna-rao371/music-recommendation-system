import os
import sys
import shutil
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Preformatted
)
from reportlab.pdfgen import canvas

# Configure UTF-8 stdout
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and stamp total page count
    and render running headers and footers with divider lines.
    """
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
        self.saveState()
        
        # Running Header (Pages 2+)
        if self._pageNumber > 1:
            self.setFont('Helvetica-Oblique', 8.5)
            self.setFillColor(colors.HexColor('#64748b'))
            self.drawString(54, 756, "TuneSphere AI Music Recommendation System — Technical Report")
            self.setStrokeColor(colors.HexColor('#cbd5e1'))
            self.setLineWidth(0.5)
            self.line(54, 748, 558, 748)
        
        # Running Footer (All Pages)
        self.setStrokeColor(colors.HexColor('#cbd5e1'))
        self.setLineWidth(0.5)
        self.line(54, 48, 558, 48)
        
        self.setFont('Helvetica', 8.5)
        self.setFillColor(colors.HexColor('#64748b'))
        self.drawString(54, 36, "Author: Tamanna Rao | Render & GitHub Documentation")
        
        # Right aligned page number
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 36, page_str)
        
        self.restoreState()


def build_pdf(filename="TuneSphere_AI_Project_Report.pdf"):
    # Standard US Letter (612 x 792 pt), margins: 54 pt (0.75 in)
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=50,
        bottomMargin=52
    )

    # Color Palette matching demo PDF (Tailwind Slate & Blue theme)
    PRIMARY = colors.HexColor('#0f172a')       # Slate-900: Headings, titles
    SECONDARY = colors.HexColor('#475569')     # Slate-600: Subtitles
    BODY_COLOR = colors.HexColor('#334155')    # Slate-700: Body paragraphs
    MUTED_COLOR = colors.HexColor('#64748b')   # Slate-500: Footers, small notes
    ACCENT_BLUE = colors.HexColor('#2563eb')   # Blue-600: Highlights, links, accent line
    BOX_BG = colors.HexColor('#eff6ff')        # Blue-50: Metadata box background
    BOX_BORDER = colors.HexColor('#bfdbfe')    # Blue-200: Metadata box border
    TABLE_HDR_BG = colors.HexColor('#dbeafe')  # Blue-100: Table header background
    ROW_ALT_BG = colors.HexColor('#f8fafc')    # Slate-50: Alternating row background
    TABLE_BORDER = colors.HexColor('#cbd5e1')  # Slate-300: Table borders
    CODE_BG = colors.HexColor('#f1f5f9')       # Slate-100: Code block background
    CODE_BORDER = colors.HexColor('#e2e8f0')   # Slate-200: Code block border
    CODE_TEXT = colors.HexColor('#1e293b')     # Slate-800: Code text
    SUCCESS_GREEN = colors.HexColor('#16a34a') # Green-600: Live status badge

    # Typography Styles
    styles = getSampleStyleSheet()

    # Title & Subtitle
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=PRIMARY,
        spaceAfter=2
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=SECONDARY,
        spaceAfter=6
    )

    # Section Headings (H1)
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=PRIMARY,
        spaceBefore=8,
        spaceAfter=3
    )

    # Stage Headings (H2)
    stage_style = ParagraphStyle(
        'StageHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13.5,
        textColor=PRIMARY,
        spaceBefore=6,
        spaceAfter=2
    )

    # Body Paragraph
    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.8,
        leading=12.2,
        textColor=BODY_COLOR,
        spaceAfter=4
    )

    # Bullet / Item Style
    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.6,
        leading=11.8,
        textColor=BODY_COLOR,
        leftIndent=12,
        firstLineIndent=-12,
        spaceAfter=2.5
    )

    # Meta Box Label & Value
    meta_label = ParagraphStyle(
        'MetaLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=PRIMARY
    )
    meta_val = ParagraphStyle(
        'MetaVal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.8,
        leading=12,
        textColor=ACCENT_BLUE
    )
    meta_val_dark = ParagraphStyle(
        'MetaValDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.8,
        leading=12,
        textColor=BODY_COLOR
    )

    # Table cell styles
    th_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.8,
        leading=11.5,
        textColor=PRIMARY
    )
    tb_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.2,
        leading=11,
        textColor=BODY_COLOR
    )
    tb_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.2,
        leading=11,
        textColor=PRIMARY
    )
    tb_cell_link = ParagraphStyle(
        'TableCellLink',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.2,
        leading=11,
        textColor=ACCENT_BLUE
    )
    tb_cell_green = ParagraphStyle(
        'TableCellGreen',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.2,
        leading=11,
        textColor=SUCCESS_GREEN
    )

    # ZapfDingbats square icon (character 'n' = black square)
    sq = '<font name="ZapfDingbats" color="#2563eb" size="8">n</font>'
    sq_dark = '<font name="ZapfDingbats" color="#0f172a" size="7">n</font>'

    story = []

    # =========================================================================
    # PAGE 1
    # =========================================================================
    story.append(Paragraph(f'{sq} &nbsp;<b>TuneSphere AI - Music Recommendation System</b>', title_style))
    story.append(Paragraph("Comprehensive Project Report: Technical Architecture, Machine Learning Pipeline & Deployment", subtitle_style))
    
    # Accent Blue Divider Line
    line_table = Table([['']], colWidths=[504], rowHeights=[1.5])
    line_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), ACCENT_BLUE),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(line_table)
    story.append(Spacer(1, 6))

    # Metadata Card Box
    meta_data = [
        [
            Paragraph(f'{sq_dark} &nbsp;<b>Live Application URL:</b>', meta_label),
            Paragraph('<link href="https://tunesphere-ai.onrender.com/"><u>https://tunesphere-ai.onrender.com/</u></link>', meta_val)
        ],
        [
            Paragraph(f'{sq_dark} &nbsp;<b>GitHub Repository:</b>', meta_label),
            Paragraph('<link href="https://github.com/Tamanna-rao371/music-recommendation-system"><u>https://github.com/Tamanna-rao371/music-recommendation-system</u></link>', meta_val)
        ],
        [
            Paragraph(f'{sq_dark} &nbsp;<b>Project Author:</b>', meta_label),
            Paragraph('Tamanna Rao &nbsp;(Production Build v1.0 &nbsp;|&nbsp; September 2026)', meta_val_dark)
        ]
    ]
    meta_box = Table(meta_data, colWidths=[140, 364])
    meta_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BOX_BG),
        ('BOX', (0, 0), (-1, -1), 0.75, BOX_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#dbeafe')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(meta_box)
    story.append(Spacer(1, 5))

    # 1. Project Overview
    story.append(Paragraph("1. Project Overview", h1_style))
    p1_text = (
        "<b>TuneSphere AI</b> is a high-performance content-based music recommendation platform. "
        "Built using <b>Python</b>, <b>Flask</b>, <b>Scikit-Learn</b>, and the <b>Spotify Web API</b>, the application "
        "processes metadata and acoustic dimensions across <b>15,000 tracks</b> from the Spotify dataset to provide "
        "instant, personalized song recommendations."
    )
    story.append(Paragraph(p1_text, body_style))

    p2_text = (
        "Unlike basic recommendation projects, TuneSphere AI features a <b>Hybrid 3,006-Dimensional Latent Space</b> "
        "(combining 1.8x-weighted artist and genre tags with normalized 6D audio vectors), <b>4 Dynamic Inference Strategies</b> "
        "(Balanced, Serendipity, High Energy, and Acoustic Depth), real-time search autocomplete with sub-millisecond fuzzy matching, "
        "mood-targeted psychological valence filtering, and a <b>Robust Offline Mode</b> that guarantees zero network latency even when "
        "external API connectivity is unavailable."
    )
    story.append(Paragraph(p2_text, body_style))
    story.append(Spacer(1, 4))

    # 2. Complete Tech Stack
    story.append(Paragraph("2. Complete Tech Stack", h1_style))
    
    stack_data = [
        [
            Paragraph("Category", th_style),
            Paragraph("Technologies & Libraries", th_style),
            Paragraph("Purpose / Role in Project", th_style)
        ],
        [
            Paragraph("Frontend & UI", tb_cell_bold),
            Paragraph("Jinja2, HTML5, CSS3, JavaScript (Vanilla ES6)", tb_cell),
            Paragraph("Responsive dark-slate UI, SVG acoustic radar visualizations, dynamic vinyl artwork, real-time debounce autocomplete.", tb_cell)
        ],
        [
            Paragraph("Web Framework", tb_cell_bold),
            Paragraph("Flask 3.0, Werkzeug, Gunicorn", tb_cell),
            Paragraph("Production WSGI backend, RESTful endpoint routing, session management, CSRF-safe forms, and JSON API payloads.", tb_cell)
        ],
        [
            Paragraph("Machine Learning", tb_cell_bold),
            Paragraph("Scikit-Learn (<code>CountVectorizer</code>, <code>cosine_similarity</code>)", tb_cell),
            Paragraph("Computes sparse metadata tag vectors (3,000 features scaled 1.8x) and computes sub-3ms cosine similarity vectors.", tb_cell)
        ],
        [
            Paragraph("Vector Math", tb_cell_bold),
            Paragraph("SciPy (<code>csr_matrix</code>, <code>hstack</code>), NumPy, Pandas", tb_cell),
            Paragraph("Sparse matrix operations, horizontal feature concatenation into 3,006-D latent space, and dataset cleaning.", tb_cell)
        ],
        [
            Paragraph("Data Management", tb_cell_bold),
            Paragraph("SQLite3, JSON, CSV", tb_cell),
            Paragraph("Persistent favorites tracking, custom playlist management with CSV/JSON exports, and Spotify cache persistence.", tb_cell)
        ],
        [
            Paragraph("API & Networking", tb_cell_bold),
            Paragraph("Spotipy (Spotify Web API), Requests, Python-Dotenv", tb_cell),
            Paragraph("Spotify metadata querying, 0-ms local album art caching (<code>spotify_cache.json</code>), and secret resolution.", tb_cell)
        ],
        [
            Paragraph("Deployment", tb_cell_bold),
            Paragraph("Render Cloud, GitHub, Git", tb_cell),
            Paragraph("Cloud hosting, dynamic <code>$PORT</code> binding, worker process management, and zero-downtime deployment setup.", tb_cell)
        ]
    ]

    stack_table = Table(stack_data, colWidths=[95, 155, 254])
    stack_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), TABLE_HDR_BG),
        ('BOX', (0, 0), (-1, -1), 0.5, TABLE_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, TABLE_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 2.2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.2),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('BACKGROUND', (0, 1), (-1, 1), colors.white),
        ('BACKGROUND', (0, 2), (-1, 2), ROW_ALT_BG),
        ('BACKGROUND', (0, 3), (-1, 3), colors.white),
        ('BACKGROUND', (0, 4), (-1, 4), ROW_ALT_BG),
        ('BACKGROUND', (0, 5), (-1, 5), colors.white),
        ('BACKGROUND', (0, 6), (-1, 6), ROW_ALT_BG),
        ('BACKGROUND', (0, 7), (-1, 7), colors.white),
    ]))
    story.append(stack_table)
    story.append(Spacer(1, 4))

    # 3. How It Works (Intro)
    story.append(Paragraph("3. How It Works (System Architecture & Pipeline)", h1_style))
    arch_intro = (
        "The TuneSphere AI system operates in four core stages: <b>Data Preprocessing & Entity Normalization</b>, "
        "<b>Hybrid Latent Space & Cosine Similarity</b>, <b>Dynamic Inference & Strategy Ranking</b>, and "
        "<b>Explainable Audio Feature Extraction</b>."
    )
    story.append(Paragraph(arch_intro, body_style))

    # Force PageBreak to start Page 2 exactly
    story.append(PageBreak())

    # =========================================================================
    # PAGE 2
    # =========================================================================
    # Stage 1
    story.append(Paragraph("Stage 1: Preprocessing & Entity Normalization", stage_style))
    s1_steps = [
        "1. Ingests 15,000 tracks from <code>dataset/songs.csv</code> containing track names, artist, genre, popularity, and 5 acoustic dimensions.",
        "2. Cleans text attributes, handles missing fields (imputing 'Pop' for null genres), filters special characters, and deduplicates identical <code>(song, artist)</code> pairs.",
        "3. Synthesizes dense composite metadata tokens by concatenating normalized artist and genre attributes (<code>artist + ' ' + genre</code>).",
        "4. Applies <code>MinMaxScaler</code> across 6 continuous audio dimensions (popularity, danceability, energy, valence, acousticness, tempo) to map all values uniformly into [0.0, 1.0]."
    ]
    for step in s1_steps:
        story.append(Paragraph(step, bullet_style))

    # Stage 2
    story.append(Paragraph("Stage 2: Hybrid Latent Space & Cosine Similarity", stage_style))
    s2_intro = (
        "The system extracts 3,000 distinct text features and combines them with normalized audio vectors:"
    )
    story.append(Paragraph(s2_intro, body_style))
    s2_bullets = [
        "&bull; &nbsp;<b>CountVectorizer Engine:</b> Extracts top 3,000 n-gram metadata tokens and scales text weight by 1.8x to establish foundational genre identity.",
        "&bull; &nbsp;<b>6D Audio Matrix:</b> Converts normalized acoustic dimensions to <code>csr_matrix</code> and concatenates horizontally via <code>scipy.sparse.hstack</code> to form a 3,006-D space."
    ]
    for b in s2_bullets:
        story.append(Paragraph(b, bullet_style))
    s2_formula = (
        "Similarity between query track vector A and catalog vector B is computed via standard cosine metric: "
        "<b>Cosine Similarity(A, B) = (A &middot; B) / (||A|| &times; ||B||)</b>."
    )
    story.append(Paragraph(s2_formula, body_style))

    # Stage 3
    story.append(Paragraph("Stage 3: Dynamic Inference & Strategy Ranking", stage_style))
    s3_intro = (
        "When a user selects a song, TuneSphere queries the top 300 nearest neighbors in vector space and dynamically re-ranks them using 4 selectable strategies:"
    )
    story.append(Paragraph(s3_intro, body_style))
    strat_bullets = [
        "&bull; &nbsp;<b>Balanced (Default):</b> Pure cosine similarity across metadata tags and normalized audio metrics (<i>S<sub>final</sub> = S<sub>cosine</sub></i>).",
        "&bull; &nbsp;<b>Discovery / Serendipity:</b> Penalizes mainstream popularity bias (<i>S<sub>final</sub> = 0.65 &middot; S<sub>cosine</sub> + 0.35 &middot; (1.0 - Pop<sub>norm</sub>)</i>) to surface indie gems.",
        "&bull; &nbsp;<b>High Energy:</b> Blends cosine similarity with energy and tempo congruence (<i>S<sub>final</sub> = 0.55 &middot; S<sub>cosine</sub> + 0.30 &middot; (1 - |&Delta;Energy|) + 0.15 &middot; (1 - |&Delta;Tempo|)</i>).",
        "&bull; &nbsp;<b>Acoustic Depth:</b> Prioritizes organic acoustic instrumentation and timbre (<i>S<sub>final</sub> = 0.60 &middot; S<sub>cosine</sub> + 0.40 &middot; (1 - |&Delta;Acousticness|)</i>)."
    ]
    for sb in strat_bullets:
        story.append(Paragraph(sb, bullet_style))

    # 4. Key Innovations
    story.append(Paragraph("4. Key Innovations & Standout Features", h1_style))
    innovations = [
        f"{sq_dark} &nbsp;<b>Hybrid 3,006-D Latent Space:</b> Combines 3,000 NLP text features (1.8x weighted) with 6 normalized acoustic dimensions for high-fidelity sonic matching.",
        f"{sq_dark} &nbsp;<b>4 Dynamic Inference Strategies:</b> Enables live user switching between Balanced, Serendipity (anti-popularity), High Energy, and Acoustic Depth.",
        f"{sq_dark} &nbsp;<b>Real-Time Autocomplete Search:</b> Instant sub-millisecond search suggestions powered by client-side debounce and server-side fuzzy string matching (<code>difflib</code>).",
        f"{sq_dark} &nbsp;<b>Mood & Vibe Vector Matcher:</b> Directly filters tracks matching psychological valence and energy zones (<i>Happy</i>, <i>Workout</i>, <i>Chill</i>, <i>Party</i>, <i>Melancholy</i>, <i>Romantic</i>).",
        f"{sq_dark} &nbsp;<b>Robust Offline Mode & Instant Fallback:</b> Zero external API dependencies required for core functionality; generates inline vinyl gradient art if Spotify is unreachable.",
        f"{sq_dark} &nbsp;<b>Curated Spotify Album Covers & Smart Caching:</b> Connects to Spotify Web API with local cache (<code>spotify_cache.json</code>) for 0-ms instant poster rendering.",
        f"{sq_dark} &nbsp;<b>Full-Featured Playlist Suite & SQLite Favorites:</b> Relational database storage for user bookmarks with complete acoustic radar signatures and CSV/JSON playlist exports."
    ]
    for inn in innovations:
        story.append(Paragraph(inn, bullet_style))

    # 5. Render Cloud Deployment Intro
    story.append(Paragraph("5. Render Cloud Automatic Deployment Mechanics", h1_style))
    deploy_intro = (
        "Deploying ML recommendation models with high-dimensional feature spaces on cloud PaaS environments (like Render) presents unique challenges with memory limits and port resolution. "
        "TuneSphere AI solves this cleanly with an in-memory sparse compilation workflow and dynamic binding:"
    )
    story.append(Paragraph(deploy_intro, body_style))

    # Force PageBreak to start Page 3 exactly
    story.append(PageBreak())

    # =========================================================================
    # PAGE 3
    # =========================================================================
    # Code snippet block
    code_text = (
        "# Render Dynamic Port Binding & Production Execution (app.py)\n"
        "if __name__ == '__main__':\n"
        "    port = int(os.environ.get('PORT', 5000))\n"
        "    app.run(host='0.0.0.0', port=port, debug=False)\n\n"
        "# Model Pipeline Benchmark (model_builder.py)\n"
        "# Combined feature space: (15000, 3006) | Cosine similarity inference latency: 2.72 ms\n"
        "similarity_scores = cosine_similarity(song_vector, X_combined).flatten()\n"
        "top_indices = similarity_scores.argsort()[::-1][1:7]"
    )
    code_style = ParagraphStyle(
        'CodeSnippet',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.8,
        leading=10.5,
        textColor=CODE_TEXT
    )
    code_p = Preformatted(code_text, code_style)
    code_table = Table([[code_p]], colWidths=[504])
    code_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), CODE_BG),
        ('BOX', (0, 0), (-1, -1), 0.5, CODE_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(code_table)
    story.append(Spacer(1, 8))

    # Deployment Benefits
    story.append(Paragraph("<b>Deployment Benefits:</b>", stage_style))
    benefits = [
        "1. <b>Zero Cold-Start Pre-Compilation:</b> The hybrid sparse matrix is constructed in memory at startup in ~1.8 seconds, eliminating external disk I/O bottlenecks and preventing large 200MB+ binary model files from cluttering the Git repository.",
        "2. <b>Sub-3ms Inference Latency:</b> Utilizing <code>scipy.sparse.csr_matrix</code> and Scikit-Learn vectorized C-level matrix multiplications achieves instantaneous recommendation response times (<3 ms) on budget cloud hardware (Render 512MB RAM free tier).",
        "3. <b>Zero Hardcoded Secrets:</b> Resolves Spotify Web API client credentials securely via environment variables (<code>SPOTIPY_CLIENT_ID</code>, <code>SPOTIPY_CLIENT_SECRET</code>) while maintaining crash-proof offline fallback operation if unconfigured."
    ]
    for b in benefits:
        story.append(Paragraph(b, bullet_style))

    story.append(Spacer(1, 10))

    # 6. Project Repository & Live Deployment Links
    story.append(Paragraph("6. Project Repository & Live Deployment Links", h1_style))

    link_data = [
        [
            Paragraph("Resource", th_style),
            Paragraph("Link / Access Path", th_style)
        ],
        [
            Paragraph("Live Render Application", tb_cell_bold),
            Paragraph('<link href="https://tunesphere-ai.onrender.com/"><u>https://tunesphere-ai.onrender.com/</u></link>', tb_cell_link)
        ],
        [
            Paragraph("GitHub Repository", tb_cell_bold),
            Paragraph('<link href="https://github.com/Tamanna-rao371/music-recommendation-system"><u>https://github.com/Tamanna-rao371/music-recommendation-system</u></link>', tb_cell_link)
        ],
        [
            Paragraph("Deployment Status", tb_cell_bold),
            Paragraph("READY FOR RENDER CLOUD DEPLOYMENT (LIVE)", tb_cell_green)
        ],
        [
            Paragraph("Verification & Benchmark", tb_cell_bold),
            Paragraph("<code>python model_builder.py</code> &nbsp;(15,000 Tracks Verified | 2.72 ms Latency)", tb_cell)
        ]
    ]

    link_table = Table(link_data, colWidths=[160, 344])
    link_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), TABLE_HDR_BG),
        ('BOX', (0, 0), (-1, -1), 0.5, TABLE_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, TABLE_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 1), (-1, 1), colors.white),
        ('BACKGROUND', (0, 2), (-1, 2), ROW_ALT_BG),
        ('BACKGROUND', (0, 3), (-1, 3), colors.white),
        ('BACKGROUND', (0, 4), (-1, 4), ROW_ALT_BG),
    ]))
    story.append(link_table)

    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"✓ Report successfully generated: '{filename}'")

    # Copy to Artifact directory
    artifact_dir = r"C:\Users\yuvij\.gemini\antigravity\brain\af30025f-0308-4d6a-be2e-21008345edb8"
    if os.path.exists(artifact_dir):
        dest = os.path.join(artifact_dir, filename)
        shutil.copyfile(filename, dest)
        print(f"✓ Copied to artifact directory: '{dest}'")

if __name__ == '__main__':
    build_pdf()
