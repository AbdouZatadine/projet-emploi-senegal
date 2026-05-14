

import pandas as pd
import os

DOSSIER_BRUT = "data/brut/"


def fusionner():

    senjob = pd.read_csv(f"{DOSSIER_BRUT}offres_senjob.csv")
    goafrica = pd.read_csv(f"{DOSSIER_BRUT}offres_goafrica.csv")
    emploidakar = pd.read_csv(f"{DOSSIER_BRUT}offres_emploidakar.csv")
    emploisenegal = pd.read_csv(f"{DOSSIER_BRUT}offres_emploisenegal.csv")

    # --- Harmonisation des colonnes ---
    senjob = senjob.rename(columns={"localite": "ville"})
    emploisenegal = emploisenegal.rename(columns={"region": "ville"})

    # --- Colonnes à garder ---
    colonnes = ["titre", "entreprise", "categorie", "ville", "contrat", "date_publication", "description", "lien"]

    # --- Ajouter les colonnes manquantes avec N/A ---
    for df in [senjob, goafrica, emploidakar, emploisenegal]:
        for col in colonnes:
            if col not in df.columns:
                df[col] = "N/A"

    # --- Garder uniquement les colonnes voulues ---
    senjob = senjob[colonnes]
    goafrica = goafrica[colonnes]
    emploidakar = emploidakar[colonnes]
    emploisenegal = emploisenegal[colonnes]

    # --- Combinaison ---
    df_final = pd.concat([senjob, goafrica, emploidakar, emploisenegal], ignore_index=True)

    # --- Sauvegarde ---
    os.makedirs(DOSSIER_BRUT, exist_ok=True)
    df_final.to_csv(f"{DOSSIER_BRUT}offres_combinees.csv", index=False, encoding="utf-8-sig")

    print(f" Fichier combiné sauvegardé dans {DOSSIER_BRUT}")
    print(f" {df_final.shape[0]} offres | {df_final.shape[1]} colonnes")
    print(df_final.head(3))


if __name__ == "__main__":
    fusionner()