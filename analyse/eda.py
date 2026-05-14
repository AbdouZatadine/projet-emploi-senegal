

import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter


def charger_donnees():
    df = pd.read_csv("data/propre/offres_finales.csv")
    df['date_publication'] = pd.to_datetime(df['date_publication'])
    return df


def offres_par_secteur(df):
    secteurs = df['secteur'].value_counts().head(10)
    return secteurs


def top10_competences(df):
    toutes_competences = df['competences'].dropna()
    toutes_competences = toutes_competences[toutes_competences != "Non précisé"]
    compteur = Counter()
    for comp in toutes_competences:
        for c in comp.split(", "):
            compteur[c.strip()] += 1
    top10 = pd.Series(compteur).sort_values(ascending=False).head(10)
    return top10


def repartition_geographique(df):
    villes = df['ville'].value_counts().head(10)
    return villes


def evolution_mensuelle(df):
    df['mois'] = df['date_publication'].dt.to_period('M')
    evolution = df.groupby('mois').size().sort_index()
    return evolution