
import pandas as pd
from collections import Counter


def secteur_dominant(df):
    secteur = df['secteur'].value_counts().index[0]
    nb = df['secteur'].value_counts().iloc[0]
    return {"secteur": secteur, "nb_offres": int(nb)}


def competence_top(df):
    toutes_competences = df['competences'].dropna()
    toutes_competences = toutes_competences[toutes_competences != "Non précisé"]
    compteur = Counter()
    for comp in toutes_competences:
        for c in comp.split(", "):
            compteur[c.strip()] += 1
    top = pd.Series(compteur).sort_values(ascending=False)
    return {"competence": top.index[0], "nb_offres": int(top.iloc[0])}


def ville_top(df):
    ville = df['ville'].value_counts().index[0]
    nb = df['ville'].value_counts().iloc[0]
    return {"ville": ville, "nb_offres": int(nb)} 

def contrat_dominant(df):
    contrat = df['contrat'].value_counts().index[0]
    nb = df['contrat'].value_counts().iloc[0]
    return {"contrat": contrat, "nb_offres": int(nb)}


def croissance_mensuelle(df):
    df['date_publication'] = pd.to_datetime(df['date_publication'])
    df['mois'] = df['date_publication'].dt.to_period('M')
    evolution = df.groupby('mois').size().sort_index()
    croissance = evolution.pct_change() * 100
    croissance = croissance.round(2)
    return croissance 