import os
from mistralai import Mistral

#choix du modèle
MODELE_DEFAUT = "voxtral-mini-latest"


def _charger_cle_api():
    try:
        import streamlit as st

        cle = st.secrets.get("MISTRAL_API_KEY", "")
        if cle:
            return cle
    except Exception:
        pass

    return os.environ.get("MISTRAL_API_KEY", "")


#envoi a mistral pour transcription
def transcrire(chemin_audio, modele=MODELE_DEFAUT):
    api_key = _charger_cle_api()
    if not api_key:
        raise ValueError(
            "API key introuvable"
        )

    client = Mistral(api_key=api_key)

    with open(chemin_audio, "rb") as f:
        reponse = client.audio.transcriptions.complete(
            model=modele,
            file={
                "content": f,
                "file_name": os.path.basename(chemin_audio),
            },
            diarize=True,
            timestamp_granularities=["segment"],
        )

    if getattr(reponse, "segments", None):
        return _formater_diarisation(reponse.segments)

    return reponse.text


#diarisation (attribution des voix)
def _formater_diarisation(segments):
    etiquettes = {}
    lignes = []
    for seg in segments:
        brut = getattr(seg, "speaker_id", None) or "?"
        if brut not in etiquettes:
            etiquettes[brut] = f"Personne {len(etiquettes) + 1}"
        personne = etiquettes[brut]
        texte = (seg.text or "").strip()
        if not texte:
            continue
        if lignes and lignes[-1][0] == personne:
            lignes[-1][1] += " " + texte
        else:
            lignes.append([personne, texte])

    return "\n".join(f"{loc} : {txt}" for loc, txt in lignes)
