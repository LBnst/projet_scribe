import streamlit as st
import stockage
from export_pdf import construire_pdf

#format visuel du tableau
APERCU_LONGUEUR = 110
COLONNES = [1, 2, 4, 4]



def apercu(texte):
    texte = " ".join((texte or "").split())
    if not texte:
        return "—"
    if len(texte) <= APERCU_LONGUEUR:
        return texte
    return texte[:APERCU_LONGUEUR].rstrip() + "…"


@st.dialog("Détail de l'enregistrement", width="large")
def afficher_detail(entree):
    st.subheader(entree.get("nom", "—"))

    with st.expander("Transcription complète", expanded=False):
        st.write(entree.get("transcription") or "—")

    with st.expander("Compte rendu complet", expanded=False):
        st.write(entree.get("compte_rendu") or "—")


@st.dialog("Effacer l'historique ?")
def confirmer_effacement():
    st.write("Tous les enregistrements de stockage.json seront supprimés. Action irréversible.")
    gauche, droite = st.columns(2)
    if gauche.button("Annuler", use_container_width=True):
        st.rerun()
    if droite.button("Effacer définitivement", type="primary", use_container_width=True):
        stockage.effacer()
        st.rerun()


@st.dialog("Gérer l'enregistrement")
def gerer_entree(entree):
    nom_actuel = entree.get("nom", "")
    st.caption(f"Enregistrement : {nom_actuel}")

    nouveau_nom = st.text_input("Nouveau nom", value=nom_actuel)
    if st.button("Renommer", use_container_width=True):
        nom = nouveau_nom.strip()
        noms_existants = {e.get("nom") for e in stockage.charger()} - {nom_actuel}
        if not nom:
            st.warning("Le nom ne peut pas être vide.")
        elif nom in noms_existants:
            st.warning("Ce nom est déjà utilisé.")
        else:
            stockage.renommer(nom_actuel, nom)
            st.rerun()

    st.divider()

    st.download_button(
        "Exporter en PDF",
        data=construire_pdf(entree),
        file_name=f"{nom_actuel or 'enregistrement'}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

    st.divider()

    confirmer = st.checkbox("Confirmer la suppression définitive")
    if st.button("Supprimer", type="primary", disabled=not confirmer,
                 use_container_width=True):
        stockage.supprimer(nom_actuel)
        st.rerun()


st.set_page_config(page_title="Historique", layout="wide")
st.title("Historique")

try:
    entrees = stockage.charger()
except RuntimeError as exc:
    st.error(str(exc))
    st.stop()

_, haut_droite = st.columns([3, 1])
if haut_droite.button("Effacer l'historique", type="primary", use_container_width=True,
                      disabled=not entrees):
    confirmer_effacement()

if not entrees:
    st.info("Aucun enregistrement pour le moment.")
    st.stop()

st.caption(
    f"{len(entrees)} enregistrement(s) — cliquez sur un champ pour le détail, "
    "« Gérer » pour renommer ou supprimer"
)

#visuel du tableau
st.markdown(
    """
    <style>
    [class*="st-key-histrow-"] { margin-bottom: .5rem; }
    [class*="st-key-histrow-"] [data-testid="stHorizontalBlock"] { align-items: stretch; }
    [class*="st-key-histrow-"] [data-testid="stColumn"] {
        display: flex; flex-direction: column; justify-content: center;
    }
    [class*="st-key-histrow-"] [data-testid="stColumn"]:not(:first-child) {
        border-left: 1px solid rgba(128, 128, 128, .35);
        padding-left: .9rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

#filtre de recherche
recherche = st.text_input(
    "Rechercher par nom",
    placeholder="Filtrer les enregistrements par nom",
).strip().lower()

affichees = [e for e in reversed(entrees) if recherche in e.get("nom", "").lower()]

if not affichees:
    st.info("Aucun enregistrement ne correspond à la recherche.")
    st.stop()

with st.container(border=True, key="histrow-head"):
    entete = st.columns(COLONNES)
    entete[0].markdown("**Gérer**")
    entete[1].markdown("**Nom**")
    entete[2].markdown("**Transcription (début)**")
    entete[3].markdown("**Compte rendu (début)**")

a_ouvrir = None
a_gerer = None
for i, entree in enumerate(affichees):
    with st.container(border=True, key=f"histrow-{i}"):
        ligne = st.columns(COLONNES)

        if ligne[0].button("Gérer", key=f"gerer_{i}", use_container_width=True):
            a_gerer = entree

        champs = (
            entree.get("nom", "—"),
            apercu(entree.get("transcription")),
            apercu(entree.get("compte_rendu")),
        )
        for col, texte, cle in zip(ligne[1:], champs, ("nom", "tr", "cr")):
            if col.button(texte, key=f"{cle}_{i}", type="tertiary", use_container_width=True):
                a_ouvrir = entree

if a_gerer is not None:
    gerer_entree(a_gerer)
elif a_ouvrir is not None:
    afficher_detail(a_ouvrir)
