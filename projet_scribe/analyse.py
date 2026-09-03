from mistralai import Mistral
from transcription import _charger_cle_api

MODELE_ANALYSE = "open-mistral-nemo"

#prompt envoyé a mistral lors de l'analyse
INSTRUCTION_ANALYSE = (
    "Tu es un assistant qui analyse la transcription d'une réunion.\n"
    "À partir du texte fourni, rédige un compte rendu clair en français.\n"
    "Commence par indiquer très grossièrement de quoi a traité cette réunion.\n"
    "Créé ensuite plusieurs catégories, une par thème abordé lors de la réunion, indique bien dans chaque catégorie quel intervenant a présenté quelle partie.\n"
    "Créé un avant-dernier paragraphe dans lequel tu indiques quelles décisions ont été prises dans la réunion et qui doit effectuer quelle action.\n"
    "Tu es libre d'ajouter des notes à la fin si tu en vois le besoin."
)


def analyser(transcription):
    api_key = _charger_cle_api()
    if not api_key:
        raise ValueError(
            "Clé api manquante!"
        )

    client = Mistral(api_key=api_key)

    #fusion du prompt et de la transcription pour en faire le prompt complet
    messages = [
        {"role": "system", "content": INSTRUCTION_ANALYSE},
        {"role": "user", "content": transcription},
    ]

    reponse = client.chat.complete(
        model=MODELE_ANALYSE,
        messages=messages,
        temperature=0.3,
    )

    return reponse.choices[0].message.content
