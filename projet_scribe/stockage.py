import json
import os

#création du fichier json pour stocker l'historique des transcriptions/analyses
FICHIER_STOCKAGE = os.path.join(os.path.dirname(__file__), "stockage.json")


#chargement du fichier de stockage préexistant
def charger():
    #en créé un nouveau si aucun fichier existe
    if not os.path.exists(FICHIER_STOCKAGE):
        return []
    try:
        with open(FICHIER_STOCKAGE, "r", encoding="utf-8") as f:
            contenu = f.read()
        if not contenu.strip():
            return []
        return json.loads(contenu)
    #solution de secours, transforme le fichier json s'il est corrompu pour qu'on puisse en créer un nouveau
    except (UnicodeDecodeError, ValueError) as exc:
        sauvegarde = FICHIER_STOCKAGE + ".corrompu"
        os.replace(FICHIER_STOCKAGE, sauvegarde)
        raise RuntimeError(
            f"Fichier de stockage illisible et mis de côté. Recréez-en un"
        ) from exc


#attribue un nom + numéro automatiquement aux nouveaux enregistrements
def _nom_suivant(entrees):
    numeros = []
    for e in entrees:
        nom = e.get("nom", "")
        if nom.startswith("enregistrement_"):
            suffixe = nom.removeprefix("enregistrement_")
            if suffixe.isdigit():
                numeros.append(int(suffixe))
    prochain_num = max(numeros, default=0) + 1
    return f"enregistrement_{prochain_num}"



#entrée des données dans le fichier de stockage
def _ecrire(entrees):
    #créé un fichier temporaire en cas de corruption
    temp = FICHIER_STOCKAGE + ".tmp"
    with open(temp, "w", encoding="utf-8") as f:
        json.dump(entrees, f, ensure_ascii=False, indent=2)
    os.replace(temp, FICHIER_STOCKAGE)


#écriture de la transcription dans la ligne
def ajouter(transcription):
    entrees = charger()
    entree = {
        "nom": _nom_suivant(entrees),
        "transcription": transcription,
        "compte_rendu": "",
    }
    entrees.append(entree)
    _ecrire(entrees)
    return entree


#écriture du compte rendu dans la ligne
def definir_compte_rendu(nom, compte_rendu):
    """Enregistre le compte rendu d'analyse pour l'entrée portant ce nom."""
    entrees = charger()
    for e in entrees:
        if e.get("nom") == nom:
            e["compte_rendu"] = compte_rendu
            break
    _ecrire(entrees)


#fonction pour renommer un enregistrement
def renommer(ancien_nom, nouveau_nom):
    entrees = charger()
    for e in entrees:
        if e.get("nom") == ancien_nom:
            e["nom"] = nouveau_nom
            break
    _ecrire(entrees)


#fonction pour supprimer comme son nom l'indique une entrée unique
def supprimer(nom):
    entrees = [e for e in charger() if e.get("nom") != nom]
    _ecrire(entrees)


#pour effacer l'ensemble du fichier de stockage
def effacer():
    try:
        os.remove(FICHIER_STOCKAGE)
    except OSError:
        pass
