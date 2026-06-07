import fitz  # PyMuPDF
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE
from pathlib import Path

PDF_PATH = Path(r"c:\Hackathon\Idea Submission Template _ Redrob.pdf")
OUT_PPTX = Path(r"c:\Hackathon\hackathon_solution\India_Runs_Presentation_from_template.pptx")
IMG_DIR = Path(r"c:\Hackathon\hackathon_solution\template_pages")
IMG_DIR.mkdir(parents=True, exist_ok=True)

# Slide texts (from presentation_outline.md)
slides_text = [
    ("Intelligent Candidate Discovery & Ranking", "Solo, 2026 fresher\nIndia Runs Data & AI Challenge"),
    ("Problem Statement", "Rank candidates for opportunities using profile and platform signals.\nGoal: produce a top-100 ranked list that follows the submission rules."),
    ("Data Used", "Candidate profile data from candidates.jsonl\nKey signals: completeness, experience, skills, recruiter response, GitHub, views, connections"),
    ("Solution Approach", "Baseline heuristic ranking using feature weights\nLightGBM model trained on heuristic scores as pseudo-targets\nFinal ensemble by averaging baseline + model scores"),
    ("Validation", "Used the provided validator rules\nEnsured exactly 100 rows, valid candidate IDs, unique ranks, and tie-break by candidate ID"),
    ("Results", "Final submission file: submission_final.csv\nDemo top-20 file: top20.json\nReproducible scripts included in hackathon_solution/"),
    ("Demo", "Open demo.html to show top candidates\nExplain why the top profiles are ranked higher"),
    ("Why This Works", "Heuristic captures obvious signals\nModel learns non-linear interactions\nEnsemble improves stability and ranking quality"),
    ("Future Improvements", "Train a pairwise ranker with label feedback\nAdd NLP features from summaries and job history\nAdd more robust validation and model tuning"),
    ("Closing", "Final deliverable: submission_final.csv\nGitHub repo: https://github.com/Ayeshasiddiqa789/india-runs-hackathon"),
]


def render_pdf_pages(pdf_path, out_dir):
    doc = fitz.open(str(pdf_path))
    images = []
    for i, page in enumerate(doc):
        mat = fitz.Matrix(2, 2)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        out = out_dir / f"page_{i+1}.png"
        pix.save(str(out))
        images.append(out)
    return images


def build_pptx(images, texts, out_pptx):
    prs = Presentation()
    prs.slide_height = Inches(7.5)
    prs.slide_width = Inches(10)
    # For each desired slide, use the corresponding template image as background
    for idx, (img, txt) in enumerate(zip(images, texts)):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        pic = slide.shapes.add_picture(str(img), 0, 0, width=prs.slide_width, height=prs.slide_height)
        # add a semi-transparent textbox for legibility
        left = Inches(0.6)
        top = Inches(1.0)
        width = Inches(8.8)
        height = Inches(4.5)
        txBox = slide.shapes.add_textbox(left, top, width, height)
        tf = txBox.text_frame
        tf.clear()
        title, body = txt
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(28)
        p.font.bold = True
        p.space_after = Pt(14)
        for line in body.split('\n'):
            p = tf.add_paragraph()
            p.text = line
            p.level = 0
            p.font.size = Pt(18)

    prs.save(str(out_pptx))


def main():
    images = render_pdf_pages(PDF_PATH, IMG_DIR)
    # Ensure we have at least as many images as our slide texts; if more, take first N
    if len(images) < len(slides_text):
        # reuse last image for remaining slides
        while len(images) < len(slides_text):
            images.append(images[-1])
    images = images[: len(slides_text)]
    build_pptx(images, slides_text, OUT_PPTX)
    print(f"Created PPTX: {OUT_PPTX}")


if __name__ == '__main__':
    main()
