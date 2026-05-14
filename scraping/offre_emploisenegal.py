

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

# --- Configuration ---
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "fr-FR,fr;q=0.9",
    "Referer": "https://www.google.com/"
}
URL_BASE = "https://www.emploisenegal.com/recherche-jobs-senegal"
DOSSIER_SAUVEGARDE = "data/brut/"


# --- Scraping de la catégorie depuis la page détail ---
def scraper_categorie(url):
    try:
        rep = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(rep.content, "html.parser")

        for li in soup.find_all("li"):
            if li.find("strong") and "Métier" in li.find("strong").get_text():
                categorie = li.get_text(strip=True).replace("Métier:", "").strip()
                return categorie
        return "N/A"
    except:
        return "N/A"


# --- Scraping de toutes les pages ---
def scraper_offres():
    toutes_offres = []

    for page in range(0, 10):
        print(f"Page {page+1}/10...", end="\r")

        url_page = f"{URL_BASE}?page={page}"
        rep = requests.get(url_page, headers=HEADERS)
        soup = BeautifulSoup(rep.content, "html.parser")

        offres = soup.find_all("div", class_="card card-job")

        for offre in offres:
            titre_tag = offre.find("h3")
            entreprise_tag = offre.find("a", class_="card-job-company")
            time_tag = offre.find("time")
            desc_tag = offre.find("div", class_="card-job-description")
            items = offre.find_all("li")

            titre = titre_tag.get_text(strip=True) if titre_tag else "N/A"
            entreprise = entreprise_tag.get_text(strip=True) if entreprise_tag else "N/A"
            lien = "https://www.emploisenegal.com" + titre_tag.find("a")["href"] if titre_tag else "N/A"
            contrat = items[2].find("strong").get_text(strip=True) if len(items) > 2 else "N/A"
            region = items[3].find("strong").get_text(strip=True) if len(items) > 3 else "N/A"
            competences = items[4].find("strong").get_text(strip=True) if len(items) > 4 else "N/A"
            date = time_tag["datetime"] if time_tag else "N/A"
            description = desc_tag.find("p").get_text(strip=True) if desc_tag else "N/A"
            categorie = scraper_categorie(lien)

            toutes_offres.append({
                "titre": titre,
                "entreprise": entreprise,
                "categorie": categorie,
                "contrat": contrat,
                "region": region,
                "competences": competences,
                "date_publication": date,
                "description": description,
                "lien": lien
            })

            time.sleep(0.3)

        time.sleep(0.5)

    print(f"\n {len(toutes_offres)} offres collectées !")
    return toutes_offres


# --- Fonction principale ---
def main():
    toutes_offres = scraper_offres()

    df = pd.DataFrame(toutes_offres)
    df = df[['titre', 'entreprise', 'categorie', 'contrat', 'region',
             'competences', 'date_publication', 'description', 'lien']]

    os.makedirs(DOSSIER_SAUVEGARDE, exist_ok=True)
    df.to_csv(f"{DOSSIER_SAUVEGARDE}offres_emploisenegal.csv", index=False, encoding="utf-8-sig")

    print(f"\n Fichier sauvegardé dans {DOSSIER_SAUVEGARDE}")
    print(f" {df.shape[0]} offres | {df.shape[1]} colonnes")
    print(df.head(3))


if __name__ == "__main__":
    main()