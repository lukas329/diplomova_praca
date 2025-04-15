import json
from collections import defaultdict

# Cesty k súboru
input_file = "results_with_wordcount_and_humantime.json"

# Načítanie dát
with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# Slovníky na ukladanie výsledkov
prompt_times = defaultdict(list)
prompt_human_times = defaultdict(list)

# Prechod dát
for contract, results in data.items():
    for result in results:
        prompt = result["prompt"]
        llm_time = result["duration_sec"] / 60  # premena na minúty
        human_time = result["human_reading_time_min"]

        prompt_times[prompt].append(llm_time)
        prompt_human_times[prompt].append(human_time)

# Výpočet priemerov
averages = []
for prompt in prompt_times:
    avg_llm = sum(prompt_times[prompt]) / len(prompt_times[prompt])
    avg_human = sum(prompt_human_times[prompt]) / len(prompt_human_times[prompt])
    averages.append({
        "prompt": prompt,
        "avg_llm_time_min": round(avg_llm, 2),
        "avg_human_time_min": round(avg_human, 2)
    })

# Výpis výsledkov
for item in averages:
    print(f"Prompt: {item['prompt']}")
    print(f" - Priemerný čas LLM: {item['avg_llm_time_min']} min")
    print(f" - Priemerný čas človeka: {item['avg_human_time_min']} min\n")

# Uloženie do JSON (ak chceš)
with open("prompt_time_averages.json", "w", encoding="utf-8") as f:
    json.dump(averages, f, indent=2, ensure_ascii=False)

print("✅ Výsledky uložené do prompt_time_averages.json")
