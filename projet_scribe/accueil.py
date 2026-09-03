import atexit
import os
import streamlit as st
import stockage
from analyse import analyser
from enregistrement import Enregistreur
from transcription import transcrire, MODELE_DEFAUT

DOSSIER = os.path.dirname(__file__)
FICHIER_AUDIO = os.path.join(DOSSIER, "enregistrement.wav")
FORMATS_AUDIO = ["wav", "mp3", "m4a", "ogg", "flac", "webm", "mp4"]


#override l'ancier fichier audio
def supprimer_wav():
    try:
        os.remove(FICHIER_AUDIO)
    except OSError:
        pass


def transcrire_et_stocker(chemin):
    with st.spinner("Transcription en cours"):
        try:
            texte = transcrire(chemin, modele=MODELE_DEFAUT)
        except Exception as exc:
            st.session_state.erreur = str(exc)
            return False
    entree = stockage.ajouter(texte)
    st.session_state.transcript = texte
    st.session_state.nom = entree["nom"]
    st.session_state.pop("erreur", None)
    st.session_state.pop("analyse", None)
    st.session_state.pop("analyse_erreur", None)
    return True


def analyse(nom, transcription):
    with st.spinner("Analyse en cours"):
        try:
            compte_rendu = analyser(transcription)
        except Exception as exc:
            st.session_state.analyse_erreur = str(exc)
            return False
    stockage.definir_compte_rendu(nom, compte_rendu)
    st.session_state.analyse = compte_rendu
    st.session_state.pop("analyse_erreur", None)
    return True


#supprime l'audio si l'app est arrêtée
atexit.register(supprimer_wav)

st.set_page_config(page_title="Voix vers texte", layout="centered")
st.title("Voix vers texte")

#empêche le reset de l'enregistrement lorsque l'on fait une autre action sur l'app
if "enregistreur" not in st.session_state:
    st.session_state.enregistreur = Enregistreur()
enr = st.session_state.enregistreur

source = st.radio("Source", ["Enregistrer", "Importer un fichier"], horizontal=True)

#enregistrement audio
if source == "Enregistrer":
    if not enr.en_cours:
        if st.button("Démarrer l'enregistrement", type="primary"):
            for cle in ("transcript", "nom", "erreur", "analyse", "analyse_erreur"):
                st.session_state.pop(cle, None)
            supprimer_wav()
            enr.demarrer()
            st.rerun()
    else:
        st.write("Enregistrement en cours")
        if st.button("Arrêter"):
            enr.arreter(FICHIER_AUDIO)
            st.rerun()

    if os.path.exists(FICHIER_AUDIO) and not enr.en_cours:
        st.audio(FICHIER_AUDIO)
        if st.button("Transcrire", type="primary"):
            if transcrire_et_stocker(FICHIER_AUDIO):
                supprimer_wav()
            st.rerun()

#importer manuellement le fichier audio
else:
    fichier = st.file_uploader("Fichier audio", type=FORMATS_AUDIO)
    if fichier is not None:
        st.audio(fichier)
        if st.button("Transcrire", type="primary"):
            chemin = os.path.join(DOSSIER, "import_" + fichier.name)
            with open(chemin, "wb") as f:
                f.write(fichier.getbuffer())
            try:
                transcrire_et_stocker(chemin)
            finally:
                try:
                    os.remove(chemin)
                except OSError:
                    pass
            st.rerun()

#résultat/erreur
if st.session_state.get("erreur"):
    st.error(f"Erreur : {st.session_state.erreur}")

if st.session_state.get("transcript"):
    st.write(f"Enregistré sous {st.session_state.nom}")
    st.text_area("Transcription", st.session_state.transcript, height=250)
    st.download_button(
        "Télécharger le .txt",
        st.session_state.transcript,
        file_name="transcription.txt",
        mime="text/plain",
    )

    #analyse ia
    if st.button("Compte rendu IA", type="primary"):
        if analyse(st.session_state.nom, st.session_state.transcript):
            st.rerun()

    if st.session_state.get("analyse_erreur"):
        st.error(f"Erreur dans l'analyse {st.session_state.analyse_erreur}")

    if st.session_state.get("analyse"):
        st.subheader("Compte rendu")
        st.markdown(st.session_state.analyse)
