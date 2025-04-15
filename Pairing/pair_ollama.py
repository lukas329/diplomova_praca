import pandas as pd
import ollama
from sentence_transformers import SentenceTransformer
import numpy as np
import re

# ✅ Načítanie CSV súborov
our_products = pd.read_csv("db.csv")  # Očakáva stĺpce: our_id, name
market_products = pd.read_csv("sql.csv")  # Očakáva stĺpce: market_id, market_name

# ✅ Použijeme lepší embedding model na presnejšie párovanie
embed_model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
our_embeddings = np.array([embed_model.encode(name) for name in our_products["name"]])


def get_top_candidates(market_name, our_df, our_embeddings, threshold=0.5):
    """ Nájde kandidátov na základe cosine similarity > 50% """
    market_embedding = embed_model.encode(market_name)
    similarities = np.dot(our_embeddings, market_embedding)

    # ✅ Odfiltrujeme produkty s podobnosťou pod 50%
    indices = np.where(similarities > threshold)[0]

    if len(indices) == 0:
        return None  # Ak nič nevyhovuje, rovno vrátime NULL

    return our_df.iloc[indices]  # Vrátime len relevantné produkty


def extract_id(text):
    """ Extrahuje iba posledné číslo z odpovede alebo vráti NULL. """
    text = text.strip()

    # ✅ Ignorujeme všetko pred a po čísle
    match = re.findall(r"\b\d+\b", text)
    if match:
        return match[-1]  # ✅ Vrátime posledné číslo (najpravdepodobnejšia odpoveď)

    return "NULL"


def get_matching_product(market_name: str, candidates) -> str:
    """ Použije Command R7B na výber najlepšieho kandidáta alebo NULL. """

    if candidates is None or candidates.empty:
        print(f"⛔ Žiadna relevantná zhoda pre '{market_name}', odpoveď: NULL")
        return "NULL"

    # 🔹 Vytvoríme prompt s kandidátmi
    product_list = "\n".join([f"- {row['our_id']}: {row['name']}" for _, row in candidates.iterrows()])
    prompt = f"""Vyber správne ID (our_id) pre daný market produkt.

Market produkt: "{market_name}"

Možnosti výberu:
{product_list}

Pravidlá:
- Ak existuje vhodný produkt, odpíš IBA **číslo our_id**.
- Ak žiadny produkt nevyhovuje, odpíš **presne**: NULL.
- Nepíš nič iné! Žiadne vysvetlenia, iba odpoveď.

Odpoveď:
"""

    print("\n==== PROMPT ====")
    print(prompt)
    print("=================\n")

    # 🔹 Volanie Ollamy s modelom Command R7B
    response = ollama.chat(
        model="command-r7b",
        messages=[{"role": "user", "content": prompt}],
        options={
            "temperature": 0.1,  # Minimálna náhodnosť
            "num_predict": 5,  # Obmedzená dĺžka odpovede
            "max_tokens": 5  # Odpoveď nesmie byť dlhšia ako 5 tokenov
        }
    )

    raw_result = response['message']['content'].strip()
    print(f"📜 RAW OUTPUT: {raw_result}")  # Debugging

    # ✅ Extrahujeme len ID alebo NULL
    return extract_id(raw_result)


# ✅ Spracovanie všetkých produktov
matched_results = []

for _, row in market_products.iterrows():
    market_name = row["market_name"]
    candidates = get_top_candidates(market_name, our_products, our_embeddings)

    # Použitie Command R7B na finálne rozhodnutie
    matched_id = get_matching_product(market_name, candidates)

    matched_results.append({
        "market_id": row["market_id"],
        "market_name": market_name,
        "matched_our_id": matched_id
    })
    print(f"✅ {market_name} -> {matched_id}")

# ✅ Uloženie výsledkov
matched_df = pd.DataFrame(matched_results)
matched_df.to_csv("matched_products.csv", index=False)

print("✅ Výsledky boli uložené do 'matched_products.csv'.")