import os
import json
import time
import requests

# URL na ktorú posielame formulár
URL = "http://142.93.164.173"  # hlavná stránka
UPLOAD_ENDPOINT = "http://142.93.164.173/api/process"  # zmeň ak máš inú route!

# Zložka so zmluvami
ZMLUVY_FOLDER = "./zmluvy"

# Prompty
prompts = [
    "Identifikuj zmluvné strany (názvy spoločností, adresy, IČO, DIČ) z extrahovaného textu a prezentuj ich v štruktúrovanej forme.",
    "Nájdi dátum uzavretia zmluvy a uveď ho v tvare YYYY-MM-DD.",
    "Extrahuj a zhrň predmet zmluvy.",
    "Z extrahovaného textu získaj cenu zmluvy, platobné podmienky a IBAN na úhradu.",
    "Nájdi v zmluve dodacie podmienky – termíny dodania a podmienky odovzdania diela.",
    "Získaj informácie o záručnej dobe a podmienkach poskytovania servisu po dodaní.",
    "Vypíš všetky sankcie uvedené v zmluve pre omeškanie s platbou alebo oneskorené dodanie softvéru.",
    "Nájdi podmienky ukončenia zmluvy – v akých situáciách môže byť zmluva zrušená?",
    "Zisti, akými zákonmi sa riadi táto zmluva a kde sú uvedené právne ustanovenia.",
    "Zhrň celú zmluvu do 5 viet, pričom zdôrazni hlavné povinnosti objednávateľa a dodávateľa."
]

# Výstupný súbor
output_file = "final_test_results_requests.json"
results = {}

headers = {
    "User-Agent": "LLM-Testing-Agent"
}

# Spustenie testovania
for filename in os.listdir(ZMLUVY_FOLDER):
    if filename.endswith(".pdf"):
        filepath = os.path.join(ZMLUVY_FOLDER, filename)
        print(f"\n📄 Spracovávam zmluvu: {filename}")
        results[filename] = []

        for prompt in prompts:
            print(f"➡️ Prompt: {prompt[:60]}...")

            with open(filepath, "rb") as pdf_file:
                files = {
                    "file": (filename, pdf_file, "application/pdf"),
                }
                data = {
                    "prompt": prompt
                }

                start_time = time.time()

                try:
                    response = requests.post(URL, files=files, data=data, headers=headers, timeout=1000)
                    end_time = time.time()
                    duration = round(end_time - start_time, 2)

                    if response.status_code == 200:
                        response_text = response.text.strip()
                        print("✅ Odpoveď prijatá.")
                    else:
                        response_text = f"Chyba: {response.status_code}"
                        print(f"❌ Chyba pri spracovaní: {response.status_code}")
                except Exception as e:
                    response_text = f"Error: {str(e)}"
                    duration = -1
                    print("💥 Výnimka počas requestu:", e)

                results[filename].append({
                    "prompt": prompt,
                    "response": response_text,
                    "time_taken": duration
                })

                # Uloženie po každom kroku
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)

                time.sleep(1)  # krátka pauza

print(f"\n✅ HOTOVO! Výsledky uložené do: {output_file}")
