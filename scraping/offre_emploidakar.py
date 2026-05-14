

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
URL_API = "https://www.emploidakar.com/jm-ajax/get_listings/"
DOSSIER_SAUVEGARDE = "data/brut/"


# --- Scraping d'une page ---
def scraper_page(page):
    data = {
        "lang": "",
        "search_keywords": "",
        "search_location": "",
        "filter_job_type[]": ["cdd", "cdi", "prestation-de-services", "stage"],
        "per_page": 17,
        "orderby": "featured",
        "featured_first": "false",
        "order": "DESC",
        "page": page,
        "show_pagination": "true"
    }
    rep = requests.post(URL_API, data=data, headers=HEADERS)
    return rep.json()


# --- Scraping des détails d'une offre ---
def scraper_details(url):
    try:
        rep = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(rep.content, "html.parser")
        desc_tag = soup.find("div", class_="job_description")
        return desc_tag.get_text(strip=True) if desc_tag else "N/A"
    except:
        return "N/A"


# --- Fonction principale ---
def main():
    toutes_offres = []

    print("🔍 Collecte des offres en cours...")
    for page in range(0, 23):
        print(f" Page {page}/22 ...", end="\r")

        result = scraper_page(page)
        html = result["html"]
        soup = BeautifulSoup(html, "html.parser")
        offres = soup.find_all("li", class_="job_listing")

        for offre in offres:
            titre = offre.find("h3")
            entreprise = offre.find("div", class_="company")
            ville = offre.find("div", class_="location")
            contrat = offre.find("li", class_="job-type")
            date = offre.find("time")
            lien = offre.find("a")

            toutes_offres.append({
                "titre": titre.get_text(strip=True) if titre else "N/A",
                "entreprise": entreprise.get_text(strip=True) if entreprise else "N/A",
                "ville": ville.get_text(strip=True) if ville else "N/A",
                "contrat": contrat.get_text(strip=True) if contrat else "N/A",
                "date_publication": date["datetime"] if date else "N/A",
                "lien": lien["href"] if lien else "N/A"
            })

        time.sleep(0.5)

    print(f"\n {len(toutes_offres)} offres collectées !")

    # Scraping des détails
    print(f"\n🔍 Scraping des détails pour {len(toutes_offres)} offres...")
    for i, offre in enumerate(toutes_offres):
        offre["description"] = scraper_details(offre["lien"])
        offre["categorie"] = "N/A"

        if (i + 1) % 50 == 0:
            print(f" {i + 1}/{len(toutes_offres)} offres traitées...")

        time.sleep(0.3)

    print("\n🎉 Scraping terminé !")

    # Sauvegarde
    df = pd.DataFrame(toutes_offres)
    df = df[['titre', 'entreprise', 'ville', 'contrat',
             'date_publication', 'categorie', 'description', 'lien']]

    os.makedirs(DOSSIER_SAUVEGARDE, exist_ok=True)
    df.to_csv(f"{DOSSIER_SAUVEGARDE}offres_emploidakar.csv", index=False, encoding="utf-8-sig")

    print(f"\nFichier sauvegardé dans {DOSSIER_SAUVEGARDE}")
    print(f" {df.shape[0]} offres | {df.shape[1]} colonnes")
    print(df.head(3))


if __name__ == "__main__":
    
    main()