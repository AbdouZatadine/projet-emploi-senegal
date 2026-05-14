import pandas as pd
import os

df = pd.read_csv("data/brut/offres_combinees.csv")
df_new = pd.read_csv("data/brut/offres_combinees.csv")

def gerer_valeurs_manquantes(df_new):
    df_new['entreprise'] = df_new['entreprise'].fillna('Confidentiel')
    df_new['categorie'] = df_new['categorie'].fillna('Non précisé')
    df_new['contrat'] = df_new['contrat'].fillna('Non précisé')
    df_new['date_publication'] = df_new['date_publication'].fillna('Inconnue')
    df_new['description'] = df_new['description'].fillna('Non disponible')
    print("Valeurs manquantes gérées !")
    return df_new

df_new = gerer_valeurs_manquantes(df_new)
print(df_new.isnull().sum())

def supprimer_doublons(df_new):
    avant = df_new.shape[0]
    df_new = df_new.drop_duplicates()
    apres = df_new.shape[0]
    print(f"Doublons supprimés : {avant - apres} doublons supprimés !")
    return df_new

df_new = supprimer_doublons(df_new)
print(df_new.shape)

def normaliser_ville(ville):
    ville = str(ville).strip()
    
    if any(x in ville.lower() for x in ["dakar", "yoff", "plateau", "almadies", "sacré", "liberté", "grand-yoff", "parcelles", "hlm", "keur massar", "mbao", "malika", "pikine", "guédiawaye", "point e", "liberté 6", "keur gorgui", "liberte"]):
        return "Dakar"
    elif any(x in ville.lower() for x in ["thiès", "thies"]):
        return "Thiès"
    elif any(x in ville.lower() for x in ["saint-louis", "st louis", "st-louis", "saint louis"]):
        return "Saint-Louis"
    elif any(x in ville.lower() for x in ["abidjan", "niamey", "lomé", "bamako", "conakry", "international", "hors sénégal"]):
        return "Hors Sénégal"
    elif any(x in ville.lower() for x in ["saly", "mbour", "m'bour", "somone"]):
        return "Mbour"
    elif any(x in ville.lower() for x in ["zone rural", "zone industrielle"]):
        return "Zone Rurale"
    elif any(x in ville.lower() for x in ["diamniadio"]):
        return "Diamniadio"
    elif any(x in ville.lower() for x in ["kaolack"]):
        return "Kaolack"
    elif any(x in ville.lower() for x in ["kédougou", "kedougou"]):
        return "Kédougou"
    elif any(x in ville.lower() for x in ["tambacounda"]):
        return "Tambacounda"
    elif any(x in ville.lower() for x in ["kaffrine"]):
        return "Kaffrine"
    elif any(x in ville.lower() for x in ["matam"]):
        return "Matam"
    elif any(x in ville.lower() for x in ["cap skirring", "bignona", "ziguinchor"]):
        return "Ziguinchor"
    elif any(x in ville.lower() for x in ["sénégal", "senegal", "télétravail"]):
        return "Non précisé"
    elif "linguere" in ville.lower():
        return "Linguère"
    else:
        return ville.title()

df_new["ville"] = df_new["ville"].apply(normaliser_ville)
print(df_new["ville"].value_counts())


def standardiser_contrat(df_new):
    def normaliser_contrat(contrat):
        contrat = str(contrat).strip().lower()
        
        if contrat == "non précisé":
            return "Non précisé"
        elif "cdi" in contrat and "cdd" not in contrat:
            return "CDI"
        elif "cdd" in contrat and "cdi" not in contrat:
            return "CDD"
        elif "cdi" in contrat and "cdd" in contrat:
            return "CDI/CDD"
        elif any(x in contrat for x in ["stage", "internship"]):
            return "Stage"
        elif any(x in contrat for x in ["freelance"]):
            return "Freelance"
        elif any(x in contrat for x in ["intérim", "interim"]):
            return "Intérim"
        elif any(x in contrat for x in ["alternance", "apprenticeship"]):
            return "Alternance"
        elif any(x in contrat for x in ["temps partiel"]):
            return "Temps partiel"
        elif any(x in contrat for x in ["prestation"]):
            return "Prestation de services"
        else:
            return "Non précisé"
    
    df_new['contrat'] = df_new['contrat'].apply(normaliser_contrat)
    print(" Contrat standardisé !")
    return df_new

df_new = standardiser_contrat(df_new)
print(df_new['contrat'].value_counts())

def renommer_categorie(df_new):
    df_new = df_new.rename(columns={"categorie": "secteur"})
    print(" Colonne 'categorie' renommée en 'secteur' !")
    return df_new

df_new = renommer_categorie(df_new)
print(df_new.columns.tolist())

df_new["date_publication"] = pd.to_datetime(df_new["date_publication"], errors='coerce')
print("Type après conversion :", df_new["date_publication"].dtype)
print("Valeurs manquantes :", df_new["date_publication"].isnull().sum())
df_new = df_new.dropna(subset=['date_publication'])

import numpy as np

# Proportions des contrats connus (sans Non précisé)
proportions = {
    'CDD': 0.497,
    'CDI': 0.215,
    'Stage': 0.182,
    'CDI/CDD': 0.035,
    'Freelance': 0.032,
    'Intérim': 0.019,
    'Prestation de services': 0.014,
    'Alternance': 0.003,
    'Temps partiel': 0.003
}

# Remplacer les "Non précisé"
masque = df_new['contrat'] == 'Non précisé'
nb_a_remplacer = masque.sum()
nouvelles_valeurs = np.random.choice(
    list(proportions.keys()),
    size=nb_a_remplacer,
    p=list(proportions.values())
)
df_new.loc[masque, 'contrat'] = nouvelles_valeurs

print("✅ Répartition terminée")
print(df_new['contrat'].value_counts())

os.makedirs("data/propre/", exist_ok=True)
df_new.to_csv("data/propre/offres_nettoyees.csv", index=False, encoding="utf-8-sig")
print(f" Fichier sauvegardé !")
print(f" {df_new.shape[0]} offres | {df_new.shape[1]} colonnes")