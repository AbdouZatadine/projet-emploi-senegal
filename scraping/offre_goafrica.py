
import requests
import pandas as pd
import time
import os

# --- Configuration ---
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "fr-FR,fr;q=0.9",
    "Referer": "https://www.google.com/"
}
DOSSIER_SAUVEGARDE = "data/brut/"


# --- Collecte de tous les liens des offres ---
def collecter_liens():
    tous_liens = []
    print("🔍 Collecte des liens en cours...")

    for page in range(1, 140):
        print(f"📄 Page {page}/139 ...", end="\r")

        url_page = f"https://www.goafricaonline.com/sn/emploi/__data.json?page={page}"
        rep = requests.get(url_page, headers=HEADERS)

        if rep.status_code != 200:
            print(f"\n Erreur page {page}")
            continue

        data = rep.json()
        node = data["nodes"][2]["data"]
        liens = [item for item in node if isinstance(item, str) and "goafricaonline.com/sn/emploi/job-" in str(item)]
        tous_liens.extend(liens)

        time.sleep(0.3)

    print(f"\nTotal liens collectés : {len(tous_liens)}")
    return tous_liens


# --- Extraction des détails d'une offre ---
def extraire_offre(url_offre):
    try:
        url_data = url_offre + "/__data.json"
        rep = requests.get(url_data, headers=HEADERS)
        data = rep.json()

        node2 = data["nodes"][2]["data"]

        page_job = None
        for item in node2:
            if isinstance(item, dict) and "jobOffer" in item:
                page_job = item
                break

        if not page_job:
            return None

        job = node2[page_job["jobOffer"]]

        titre = node2[job["title"]] if "title" in job else "N/A"
        date_pub = node2[job["publishDate"]] if "publishDate" in job else "N/A"
        url = node2[job["url"]] if "url" in job else "N/A"
        description = node2[job["description"]] if "description" in job else "N/A"

        adresse = node2[job["address"]]
        ville = node2[adresse["city"]] if isinstance(adresse, dict) and "city" in adresse else "N/A"

        cat_data = node2[job["category"]]
        categorie = node2[cat_data["name"]] if isinstance(cat_data, dict) and "name" in cat_data else "N/A"

        ent_data = node2[job["company"]]
        entreprise = node2[ent_data["name"]] if isinstance(ent_data, dict) and "name" in ent_data else "N/A"

        contrat_list = node2[job["contractTypes"]]
        contrat = node2[contrat_list[0]] if isinstance(contrat_list, list) and len(contrat_list) > 0 else "N/A"

        return {
            "titre": titre,
            "entreprise": entreprise,
            "ville": ville,
            "categorie": categorie,
            "contrat": contrat,
            "date_publication": date_pub,
            "description": description,
            "lien": url
        }

    except:
        return None


# --- Fonction principale ---
def main():
    tous_liens = collecter_liens()

    toutes_offres = []
    print(f"\n🔍 Scraping de {len(tous_liens)} offres...")
    print("---")

    for i, lien in enumerate(tous_liens):
        offre = extraire_offre(lien)

        if offre:
            toutes_offres.append(offre)

        if (i + 1) % 100 == 0:
            print(f"{i + 1}/{len(tous_liens)} offres traitées...")

        time.sleep(0.1)

    print(f"\n🎉 Scraping terminé ! {len(toutes_offres)} offres collectées !")

    df = pd.DataFrame(toutes_offres)

    os.makedirs(DOSSIER_SAUVEGARDE, exist_ok=True)
    df.to_csv(f"{DOSSIER_SAUVEGARDE}offres_goafrica.csv", index=False, encoding="utf-8-sig")

    print(f"\nFichier sauvegardé dans {DOSSIER_SAUVEGARDE}")
    print(f" {df.shape[0]} offres | {df.shape[1]} colonnes")
    print(df.head(3))


if __name__ == "__main__":
    main()