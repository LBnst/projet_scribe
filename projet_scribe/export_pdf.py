from fpdf import FPDF
from fpdf.enums import XPos, YPos

#formatage de certains caractères speciaux
_REMPLACEMENTS = {
    "’": "'", "‘": "'", "“": '"', "”": '"', "–": "-", "—": "-", "…": "...", " ": " ", "•": "-", "œ": "oe", "Œ": "OE",
}

def _latin1(texte):
    texte = texte or ""
    for source, cible in _REMPLACEMENTS.items():
        texte = texte.replace(source, cible)
    return texte.encode("latin-1", "replace").decode("latin-1")



def _paragraphe(pdf, hauteur, texte):
    pdf.multi_cell(0, hauteur, texte, new_x=XPos.LMARGIN, new_y=YPos.NEXT)


def construire_pdf(entree):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 16)
    _paragraphe(pdf, 10, _latin1(entree.get("nom") or "Enregistrement"))
    pdf.ln(2)

    pdf.set_font("Helvetica", "B", 13)
    _paragraphe(pdf, 8, "Transcription")
    pdf.set_font("Helvetica", "", 11)
    _paragraphe(pdf, 6, _latin1(entree.get("transcription")) or "-")
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 13)
    _paragraphe(pdf, 8, "Compte rendu")
    pdf.set_font("Helvetica", "", 11)
    _paragraphe(pdf, 6, _latin1(entree.get("compte_rendu")) or "-")

    return bytes(pdf.output())
