import google.generativeai as genai
from flask import Flask, render_template, request, jsonify
import pandas as pd
import json
import sys

sys.path.append('../analyse')
from eda import offres_par_secteur, top10_competences, repartition_geographique, evolution_mensuelle
from kpis import secteur_dominant, competence_top, ville_top, contrat_dominant

genai.configure(api_key="AIzaSyB3ncCnBS9AAaTopud_oyW8UIrmXbDyPxM")

app = Flask(__name__)

CHEMIN_BRUT = "../data/brut/offres_combinees.csv"
CHEMIN_PROPRE = "../data/propre/offres_finales.csv"

@app.route('/')
def accueil():
    df_brut = pd.read_csv(CHEMIN_BRUT)
    df_propre = pd.read_csv(CHEMIN_PROPRE)

    stats_avant = {
        "lignes": df_brut.shape[0],
        "colonnes": df_brut.shape[1],
        "doublons": df_brut.duplicated().sum(),
        "valeurs_manquantes": int(df_brut.isnull().sum().sum())
    }

    stats_apres = {
        "lignes": df_propre.shape[0],
        "colonnes": df_propre.shape[1],
        "doublons": df_propre.duplicated().sum(),
        "valeurs_manquantes": int(df_propre.isnull().sum().sum())
    }

    tableau = df_propre.head().to_dict(orient='records')
    colonnes = df_propre.columns.tolist()
    contrats_normalises = int((df_propre['contrat'] != 'Non précisé').sum())
    competences_extraites = int((df_propre['competences'] != 'Non précisé').sum())

    return render_template('accueil.html',
                           stats_avant=stats_avant,
                           stats_apres=stats_apres,
                           tableau=tableau,
                           colonnes=colonnes,
                           contrats_normalises=contrats_normalises,
                           competences_extraites=competences_extraites)

@app.route('/analyse')
def analyse():
    df = pd.read_csv(CHEMIN_PROPRE)
    df['date_publication'] = pd.to_datetime(df['date_publication'])

    kpi_secteur = secteur_dominant(df)
    kpi_competence = competence_top(df)
    kpi_ville = ville_top(df)
    kpi_contrat = contrat_dominant(df)

    secteurs = offres_par_secteur(df).sort_values()
    competences = top10_competences(df).sort_values(ascending=False)
    villes = repartition_geographique(df).sort_values()
    contrats = df['contrat'].value_counts()
    evolution = evolution_mensuelle(df)
    evolution.index = evolution.index.astype(str)

    data_secteurs = {"labels": secteurs.index.tolist(), "values": [int(v) for v in secteurs.values.tolist()]}
    data_competences = {"labels": competences.index.tolist(), "values": [int(v) for v in competences.values.tolist()]}
    data_villes = {"labels": villes.index.tolist(), "values": [int(v) for v in villes.values.tolist()]}
    data_contrats = {"labels": contrats.index.tolist(), "values": [int(v) for v in contrats.values.tolist()]}
    data_evolution = {"labels": evolution.index.tolist(), "values": [int(v) for v in evolution.values.tolist()]}

    return render_template('analyse.html',
                           kpi_secteur=kpi_secteur,
                           kpi_competence=kpi_competence,
                           kpi_ville=kpi_ville,
                           kpi_contrat=kpi_contrat,
                           data_secteurs=json.dumps(data_secteurs),
                           data_competences=json.dumps(data_competences),
                           data_villes=json.dumps(data_villes),
                           data_contrats=json.dumps(data_contrats),
                           data_evolution=json.dumps(data_evolution))

@app.route('/ia')
def ia():
    return render_template('ia.html')

@app.route('/chat', methods=['POST'])
def chat():
    question = request.json.get('message', '')

    df = pd.read_csv(CHEMIN_PROPRE)

    contexte = f"""
    Tu es un assistant spécialisé dans l'analyse des offres d'emploi au Sénégal.
    Réponds uniquement aux questions sur les données d'emploi au Sénégal.
    Si la question n'est pas liée, dis poliment que tu ne peux répondre qu'aux questions sur l'emploi au Sénégal.
    Réponds toujours en français.

    Voici les données clés :
    - Total offres : {len(df)}
    - Secteur dominant : Agences de recrutement (521 offres)
    - Ville dominante : Dakar (95.82% des offres)
    - Compétence top : Excel (1802 offres)
    - Contrat dominant : CDD (2579 offres)
    - Villes couvertes : {df['ville'].nunique()} villes
    """

    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content(contexte + "\n\nQuestion : " + question)

    return jsonify({"response": response.text})

@app.route('/parametres')
def parametres():
    return render_template('parametres.html')

if __name__ == '__main__':
    app.run(debug=True)