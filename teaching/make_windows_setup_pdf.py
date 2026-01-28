from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, ListFlowable, ListItem, Preformatted, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

OUT = './cc_templates_windows_handout.pdf'
REPO_URL = 'https://github.com/Erotemic/cc_templates'

styles = getSampleStyleSheet()

Title = ParagraphStyle(
    'Title', parent=styles['Title'], fontName='Helvetica-Bold', fontSize=22, leading=26,
    alignment=1, spaceAfter=10
)
Subtitle = ParagraphStyle(
    'Subtitle', parent=styles['Normal'], fontName='Helvetica', fontSize=11, leading=14,
    alignment=1, textColor=colors.black, spaceAfter=14
)
H1 = ParagraphStyle(
    'H1', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=14, leading=18,
    spaceBefore=14, spaceAfter=8
)
H2 = ParagraphStyle(
    'H2', parent=styles['Heading3'], fontName='Helvetica-Bold', fontSize=12.5, leading=16,
    spaceBefore=10, spaceAfter=6
)
Body = ParagraphStyle(
    'Body', parent=styles['Normal'], fontName='Helvetica', fontSize=10.8, leading=14
)
BodySmall = ParagraphStyle(
    'BodySmall', parent=styles['Normal'], fontName='Helvetica', fontSize=9.5, leading=12, textColor=colors.black
)
Code = ParagraphStyle(
    'Code', parent=styles['Code'], fontName='Courier', fontSize=10, leading=13,
    leftIndent=18, rightIndent=18, spaceBefore=4, spaceAfter=8
)
Link = ParagraphStyle(
    'Link', parent=Body, textColor=colors.blue
)
Footer = ParagraphStyle(
    'Footer', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, leading=10,
    textColor=colors.grey
)


def bullet_list(items, level=0):
    # Where the bullet should start (relative to the normal text block)
    level_indent = 14 * level          # extra indent for nested lists
    bullet_gap = 12                    # distance between bullet and text

    # In ReportLab: bullet x-position = leftIndent - bulletDedent
    left_indent = level_indent + bullet_gap

    return ListFlowable(
        [ListItem(Paragraph(i, Body)) for i in items],
        bulletType='bullet',
        leftIndent=left_indent,
        bulletDedent=bullet_gap,       # <-- this is the key (NOT bulletIndent)
        bulletFontName='Helvetica',
        bulletFontSize=Body.fontSize,  # match body text
        bulletOffsetY=1,
        spaceBefore=0,
        spaceAfter=6,
    )



def code_block(text):
    return Preformatted(text.strip('\n'), Code, dedent=0)


def on_page(canvas, doc):
    canvas.saveState()
    w, h = letter
    y = 0.5 * inch
    canvas.setFont('Helvetica', 8.5)
    canvas.setFillColor(colors.grey)
    # canvas.drawString(doc.leftMargin, y, f'cc_templates: {REPO_URL}')
    canvas.drawRightString(w - doc.rightMargin, y, f'Page {doc.page}')
    canvas.restoreState()


doc = SimpleDocTemplate(
    OUT,
    pagesize=letter,
    leftMargin=0.85*inch,
    rightMargin=0.85*inch,
    topMargin=0.75*inch,
    bottomMargin=0.8*inch,
)

story = []

# Page 1
story.append(Paragraph('Platformer Project Quick Start (Windows)', Title))
story.append(Paragraph('Goal: set up coding tools, then download the starter code and run the game.', Subtitle))

story.append(Paragraph('Tools you need', H1))
story.append(bullet_list([
    '<b>VS Code</b> - the editor where you write code and run commands.',
    '<b>Python 3.13</b> - runs your program when you type <font face="Courier">python ...</font>.',
    '<b>Git</b> - downloads the starter code using a single command.',
]))

story.append(Paragraph('Download pages (official links)', H1))

table_data = [
    [Paragraph('<b>VS Code</b>', Body), Paragraph(f'<link href="https://code.visualstudio.com/download">https://code.visualstudio.com/download</link>', Link)],
    [Paragraph('<b>Python 3.13 (Windows)</b>', Body), Paragraph(f'<link href="https://www.python.org/downloads/latest/python3.13/">https://www.python.org/downloads/latest/python3.13/</link>', Link)],
    [Paragraph('<b>Git for Windows</b>', Body), Paragraph(f'<link href="https://git-scm.com/install/windows">https://git-scm.com/install/windows</link>', Link)],
]

t = Table(table_data, colWidths=[1.85*inch, 4.65*inch])

t.setStyle(TableStyle([
    ('GRID', (0,0), (-1,-1), 0.75, colors.black),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('BACKGROUND', (0,0), (0,-1), colors.whitesmoke),
    ('LEFTPADDING', (0,0), (-1,-1), 8),
    ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ('TOPPADDING', (0,0), (-1,-1), 6),
    ('BOTTOMPADDING', (0,0), (-1,-1), 6),
]))

story.append(t)

story.append(Paragraph('Set up VS Code', H1))
story.append(bullet_list([
    'From the VS Code link above, choose the Windows download (usually x64).',
    'Open the downloaded file and click Next until Finish (defaults are fine).',
    'Open VS Code from the Start Menu (type <b>VS Code</b>).',
]))

story.append(Paragraph('Set up Python 3.13', H1))
story.append(bullet_list([
    'From the Python 3.13 link above, choose the Windows 64-bit download.',
    'Open the downloaded file.',
    '<b>Important:</b> check the box <b>Add python.exe to PATH</b>.',
]))
story.append(Paragraph('<b>Why PATH matters:</b> PATH is a list of places Windows searches for programs. If Python is on PATH, you can type <font face="Courier">python</font> in the terminal and Windows will find it.', Body))

story.append(Paragraph('Set up Git', H1))
story.append(bullet_list([
    'From the Git for Windows link above, choose the Windows download (usually x64).',
    'Open the downloaded file and accept the defaults.',
]))

story.append(Paragraph('Quick check (optional)', H1))
story.append(Paragraph('In any terminal you can type:', Body))
story.append(Spacer(1, 6))
story.append(code_block('''python --version\ngit --version'''))
story.append(Paragraph('You should see Python 3.13.x and a Git version number.', Body))

story.append(PageBreak())

# Page 2
story.append(Paragraph('Run the platformer', H1))
story.append(Paragraph('We will use VS Code to open the project folder and run a few commands.', Body))

steps = [
    ('1) Open a folder in VS Code', [
        'Open VS Code.',
        'Go to <b>File - Open Folder...</b>',
        'Choose (or create) a folder like <font face="Courier">Documents/coding</font>.',
    ]),
    ('2) Open the terminal in VS Code', None),
    ('3) Download the starter code', None),
    ('4) Go into the platformer folder', None),
    ('5) Run the game (first run usually shows an error)', None),
    ('6) Add the packages with pip', None),
    ('7) Run again', None),
]

for title, blist in steps:
    story.append(Paragraph(title, H2))
    if blist:
        story.append(bullet_list(blist, level=0))

# Step 2 body
story.insert(-6, Paragraph('A <b>terminal</b> is a place where you type short commands for the computer. In VS Code: <b>View - Terminal</b>.', Body))

# Step 3 body
story.insert(-5, Paragraph('In the VS Code terminal, type:', Body))
story.insert(-5, code_block('git clone https://github.com/Erotemic/cc_templates.git'))
story.insert(-5, Paragraph('This creates a folder named <font face="Courier">cc_templates</font>.', Body))

# Step 4 body
story.insert(-4, Paragraph('Type:', Body))
story.insert(-4, code_block('cd cc_templates/platformer'))
story.insert(-4, Paragraph('Tip: <font face="Courier">cd</font> means "change directory" (go into a folder).', BodySmall))

# Step 5 body
story.insert(-3, Paragraph('Type:', Body))
story.insert(-3, code_block('python main.py'))
story.insert(-3, Paragraph('If you see an error like "No module named ...", that means we need extra packages for this project.', Body))

# Step 6 body
story.insert(-2, Paragraph('Type:', Body))
story.insert(-2, code_block('python -m pip install ubelt pygame Pillow'))
story.insert(-2, Paragraph('Why <font face="Courier">python -m pip</font>: it makes sure the packages are added to the same Python you use to run the game.', BodySmall))

# Step 7 body
story.insert(-1, Paragraph('Type:', Body))
story.insert(-1, code_block('python main.py'))
story.insert(-1, Paragraph('The platformer window should open.', Body))


# Build

doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print('Wrote', OUT)
