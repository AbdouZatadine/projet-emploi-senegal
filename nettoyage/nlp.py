

import pandas as pd
import re

# --- Liste des compétences ---
competences_list = {
    "Informatique": ["python", "java", "javascript", "sql", "excel", "word", "powerpoint",
                     "react", "django", "flask", "php", "html", "css", "node.js",
                     "machine learning", "data science", "power bi", "tableau",
                     "spring boot", "vue.js", "api rest", "microservices", "docker",
                     "kubernetes", "ci/cd", "nosql", "agile", "scrum", "git",
                     "wordpress", "canva", "sage", "odoo", "autocad", "dropbox",
                     "pack office", "ms project", "photoshop", "illustrator"],

    "Soft Skills": ["communication", "leadership", "travail en équipe", "autonomie",
                    "rigueur", "organisation", "ponctualité", "dynamisme", "résilience",
                    "négociation", "adaptabilité", "créativité", "proactivité",
                    "flexibilité", "discrétion", "intégrité", "esprit d'initiative",
                    "esprit d'équipe", "sens des responsabilités", "aisance relationnelle"],

    "Langues": ["anglais", "français", "arabe", "espagnol", "allemand",
                "wolof", "poular", "mandingue"],

    "Gestion": ["gestion de projet", "comptabilité", "finance", "audit", "marketing",
                "ressources humaines", "logistique", "supply chain", "management",
                "budget", "reporting", "analyse", "comptabilité générale",
                "déclarations fiscales", "paie", "facturation"],

    "Réseaux sociaux": ["facebook", "instagram", "tiktok", "linkedin", "twitter"]
}


# --- Extraction du contrat ---
def extraire_contrat(description):
    description = str(description).lower()

    if re.search(r'\bcdi\b', description):
        return "CDI"
    elif re.search(r'\bcdd\b', description):
        return "CDD"
    elif any(x in description for x in ["stage", "stagiaire", "internship"]):
        return "Stage"
    elif any(x in description for x in ["freelance"]):
        return "Freelance"
    elif any(x in description for x in ["intérim", "interim"]):
        return "Intérim"
    elif any(x in description for x in ["alternance"]):
        return "Alternance"
    else:
        return "Non précisé"


# --- Extraction de l'expérience ---
def extraire_experience(description):
    description = str(description).lower()

    if any(x in description for x in ["débutant", "junior", "jeune diplômé", "sans expérience"]):
        return "Débutant"
    elif re.search(r'(\d+)\s*an', description):
        ans = re.search(r'(\d+)\s*an', description)
        nb = int(ans.group(1))
        if nb <= 2:
            return "0-2 ans"
        elif nb <= 5:
            return "2-5 ans"
        elif nb <= 10:
            return "5-10 ans"
        else:
            return "10+ ans"
    elif any(x in description for x in ["senior", "confirmé", "expérimenté"]):
        return "Senior"
    else:
        return "Non précisé"


# --- Extraction des compétences ---
def extraire_competences(description):
    description = str(description).lower()
    trouvees = []

    for categorie, competences in competences_list.items():
        for comp in competences:
            if comp.lower() in description:
                trouvees.append(comp)

    if len(trouvees) == 0:
        return "Non précisé"
    else:
        return ", ".join(trouvees)


# --- Extraction du secteur ---
def extraire_secteur(description):
    description = str(description).lower()

    if any(x in description for x in ["informatique", "développeur", "data", "logiciel", "digital", "web", "software"]):
        return "Informatique"
    elif any(x in description for x in ["comptabilité", "finance", "audit", "fiscalité", "trésorerie"]):
        return "Finance/Comptabilité"
    elif any(x in description for x in ["commercial", "vente", "marketing", "prospection"]):
        return "Commercial/Marketing"
    elif any(x in description for x in ["ressources humaines", "recrutement", "rh", "paie"]):
        return "Ressources Humaines"
    elif any(x in description for x in ["logistique", "supply chain", "transport"]):
        return "Logistique"
    elif any(x in description for x in ["santé", "médecin", "infirmier", "pharmacie"]):
        return "Santé"
    elif any(x in description for x in ["btp", "construction", "génie civil"]):
        return "BTP"
    else:
        return "Non précisé"


# --- Application sur le dataset ---
df = pd.read_csv("data/propre/offres_nettoyees.csv")

mask = df['contrat'] == "Non précisé"
df.loc[mask, 'contrat'] = df.loc[mask, 'description'].apply(extraire_contrat)

df['experience'] = df['description'].apply(extraire_experience)
df['competences'] = df['description'].apply(extraire_competences)



df = df.drop(columns=['description'])

df = df.drop(columns=['experience'])
# --- Sauvegarde ---
df.to_csv("data/propre/offres_finales.csv", index=False, encoding="utf-8-sig")

print(f"Fichier offres_finales.csv sauvegardé !")
print(f" {df.shape[0]} offres | {df.shape[1]} colonnes")
print(f"Colonnes : {df.columns.tolist()}")