import os
import json

# Cesty
TXT_FOLDER = "txts"
OUTPUT_FILE = "contract_word_counts.json"

# Výsledky
word_counts = {}

all_words = 0
count = 0

# Prechod cez všetky TXT súbory
for filename in os.listdir(TXT_FOLDER):
    if filename.endswith(".txt"):
        file_path = os.path.join(TXT_FOLDER, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
            word_count = len(text.split())
            count += 1
            all_words += word_count
            print(word_count)
            word_counts[filename] = word_count

# Uloženie výsledkov do JSON
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(word_counts, f, ensure_ascii=False, indent=2)

print(f"✅ Výsledky uložené v {OUTPUT_FILE}")

print(f"PRIEMER: {all_words/count}")
