

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
import os

# --- Configuration ---
URL_BASE = "https://senjob.com/sn/offres-d-emploi.php"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "fr-FR,fr;q=0.9",
    "Referer": "https://www.google.com/"
}
DOSSIER_SAUVEGARDE = "data/brut/"


# --- Scraping des offres sur toutes les pages ---
def scraper_offres():
    toutes_offres = []

    for page in range(0, 10):
        print(f"Scraping page {page}/10...")

        url_page = f"{URL_BASE}?page={page}"
        rep = requests.get(url_page, headers=HEADERS)
        rep.encoding = "utf-8"
        soup = BeautifulSoup(rep.content, "html.parser")

        lignes_tr = soup.find_all("tr", style=lambda s: s and "height:70px" in s)
        lignes_li = soup.find_all("li", style=lambda s: s and "height:50px" in s)
        toutes_lignes = lignes_tr + lignes_li

        for ligne in toutes_lignes:
            lien_tag = ligne.find("a", href=lambda h: h and "jobseekers" in h)
            if not lien_tag:
                continue

            titre = lien_tag.get_text(strip=True)
            lien = lien_tag["href"]

            localite_tag = ligne.find("span", class_="glyphicon-map-marker")
            localite = localite_tag.parent.get_text(strip=True) if localite_tag else "N/A"

            dates = ligne.find_all("span", style=lambda s: s and "display:none" in s)
            date_pub = dates[0].get_text(strip=True) if len(dates) > 0 else "N/A"
            date_exp = dates[1].get_text(strip=True) if len(dates) > 1 else "N/A"

            toutes_offres.append({
                "titre": titre,
                "localite": localite,
                "date_publication": date_pub,
                "date_expiration": date_exp,
                "lien": lien
            })

        time.sleep(1)

    print(f"\n{len(toutes_offres)} offres collectées !")
    return toutes_offres


# --- Scraping des détails de chaque offre ---
def scraper_details_offre(url):
    try:
        rep = requests.get(url, headers=HEADERS)
        rep.encoding = "utf-8"
        soup = BeautifulSoup(rep.content, "html.parser")

        desc_tag = soup.find("div", id="articlebi")
        description = desc_tag.get_text(strip=True) if desc_tag else "N/A"

        cats = soup.find_all("a", href=lambda h: h and ("Category" in h or "Secteur" in h))
        categorie = " | ".join([c.get_text(strip=True) for c in cats]) if cats else "N/A"

        emails = re.findall(r'[\w\.-]+@[\w\.-]+', rep.text)
        emails_valides = [e for e in emails if "@" in e and "wght" not in e]
        email = emails_valides[0] if emails_valides else "N/A"
        entreprise = email.split("@")[1].split(".")[0] if email != "N/A" else "N/A"

        return description, categorie, email, entreprise

    except:
        return "N/A", "N/A", "N/A", "N/A"


# --- Fonction principale ---
def main():
    # Scraper les offres
    toutes_offres = scraper_offres()

    # Scraper les détails
    print(f"\n🔍 Scraping des détails pour {len(toutes_offres)} offres...")
    for i, offre in enumerate(toutes_offres):
        desc, cat, email, entreprise = scraper_details_offre(offre["lien"])
        offre["description"] = desc
        offre["categorie"] = cat
        offre["email"] = email
        offre["entreprise"] = entreprise

        if (i + 1) % 10 == 0:
            print(f"{i + 1}/{len(toutes_offres)} offres traitées...")

        time.sleep(0.5)

    # Sauvegarde en CSV dans data/brut/
    df = pd.DataFrame(toutes_offres)
    df = df[['titre', 'entreprise', 'localite', 'categorie',
             'date_publication', 'date_expiration',
             'description', 'email', 'lien']]

    os.makedirs(DOSSIER_SAUVEGARDE, exist_ok=True)
    df.to_csv(f"{DOSSIER_SAUVEGARDE}offres_senjob.csv", index=False, encoding="utf-8-sig")

    print(f"\n Fichier sauvegardé dans {DOSSIER_SAUVEGARDE}")
    print(f" {df.shape[0]} offres | {df.shape[1]} colonnes")
    print(df.head(3))


if __name__ == "__main__":
    main()