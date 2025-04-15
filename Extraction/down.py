import os
import requests
from bs4 import BeautifulSoup

# Základná URL adresa
BASE_URL = "https://www.crz.gov.sk"
START_URL = "https://www.crz.gov.sk/2171273-sk/centralny-register-zmluv/?art_datum_zverejnene_od=01.01.2024&art_datum_zverejnene_do=31.01.2025"

# Adresár na uloženie zmlúv
DOWNLOAD_DIR = "zmluvy"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def get_contract_links(page_url):
    """Získa zoznam odkazov na detailné stránky zmlúv zo zoznamu."""
    response = requests.get(page_url)
    soup = BeautifulSoup(response.text, "html.parser")

    links = []
    for a_tag in soup.select("a[href^='/zmluva/']"):  # Vyhľadá odkazy na zmluvy
        contract_link = BASE_URL + a_tag["href"]
        links.append(contract_link)

    return links

def download_contract_pdf(contract_url):
    """Načíta stránku zmluvy, nájde a stiahne PDF."""
    response = requests.get(contract_url)
    soup = BeautifulSoup(response.text, "html.parser")

    pdf_link = soup.select_one("a[href$='.pdf']")
    if pdf_link:
        pdf_url = BASE_URL + pdf_link["href"]
        pdf_name = pdf_url.split("/")[-1]

        pdf_response = requests.get(pdf_url)
        pdf_path = os.path.join(DOWNLOAD_DIR, pdf_name)

        with open(pdf_path, "wb") as f:
            f.write(pdf_response.content)
        
        print(f"✅ Stiahnuté: {pdf_name}")
    else:
        print(f"⚠️ PDF nebolo nájdené na: {contract_url}")

# Iterácia cez stránky od 0 po 41
for page in range(0, 42):  # od 0 do 41
    page_url = f"{START_URL}&page={page}"
    print(f"🔍 Spracovávam stránku {page}...")

    contract_links = get_contract_links(page_url)

    for contract in contract_links:
        download_contract_pdf(contract)

print("✅ Všetky dostupné zmluvy boli stiahnuté!")

