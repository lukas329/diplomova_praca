import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM
from sklearn.metrics.pairwise import cosine_similarity
import torch
import time
from tqdm import tqdm

model_id = "CohereForAI/c4ai-command-r7b-12-2024"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.float16, device_map="auto")

our_products = pd.read_csv("our.csv", delimiter=",")  # Očakáva: our_id, name
market_products = pd.read_csv("imported.csv", delimiter=",")  # Očakáva: market_id, market_name

embed_model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

names = our_products["name"].astype(str).tolist()
our_embeddings = embed_model.encode(names, convert_to_numpy=True)

results = []


def get_top_candidates(market_name, our_df, our_embeddings, threshold=0.5, top_k=10):
    market_embedding = embed_model.encode([market_name], convert_to_numpy=True)
    similarities = cosine_similarity(market_embedding, our_embeddings)[0]

    # indexy nad prah
    indices_above_threshold = np.where(similarities > threshold)[0]

    if len(indices_above_threshold) == 0:
        return None

    # zoradenie týchto indexov podľa similarity zostupne
    sorted_indices = indices_above_threshold[np.argsort(similarities[indices_above_threshold])[::-1][:top_k]]

    candidates = our_df.iloc[sorted_indices].copy()
    candidates["similarity"] = similarities[sorted_indices]

    return candidates


for _, row in tqdm(market_products.iterrows(), total=len(market_products), desc="🔄 Spracovanie produktov"):
    market_id = row["market_id"]
    market_name = row["market_name"]
    candidates = get_top_candidates(market_name, our_products, our_embeddings)

    if candidates is None or candidates.empty:
        results.append({"market_id": market_id, "our_id": "NULL"})
        continue

    product_list = "\n".join([f"- {row['our_id']}: {row['name']}" for _, row in candidates.iterrows()])
    prompt = f"""Select the correct ID (our_id) for the given market product.

    Market product: "{market_name}"

    Selection options:
    {product_list}

    Rules:
    - If a suitable product exists, respond with ONLY the **our_id number**.
    - If no product is suitable, respond with **exactly**: NULL.
    - Do not write anything else! No explanations, just the answer.

    Answer:
    """

    tokenized_prompt = tokenizer(prompt, return_tensors="pt")  # Tokenizácia promptu
    num_tokens = tokenized_prompt["input_ids"].shape[1]

    messages = [{"role": "user", "content": prompt}]
    input_ids = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True,
                                              return_tensors="pt").to(model.device)

    start_time = time.time()
    gen_tokens = model.generate(
        input_ids,
        max_new_tokens=5,
        do_sample=False,
    )
    end_time = time.time()
    elapsed_time = end_time - start_time

    gen_text = tokenizer.decode(gen_tokens[0], skip_special_tokens=True).strip()
    gen_text = gen_text.replace("<|START_OF_TURN_TOKEN|>", "").replace("<|CHATBOT_TOKEN|>", "").replace(
        "<|SYSTEM_TOKEN|>", "").replace("<|USER_TOKEN|>", "").strip()

    gen_text = gen_text.replace("Answer:", "").strip()

    gen_text = gen_text.split("\n")[-1].strip()  # Berieme len posledný riadok (kde by malo byť ID)

    if gen_text.isdigit() and int(gen_text) in our_products["our_id"].values:
        our_id = int(gen_text)
        our_name = our_products[our_products["our_id"] == our_id]["name"].values[0]
        results.append({"market_id": market_id, "our_id": our_id})
    else:
        results.append({"market_id": market_id, "our_id": "NULL"})

results_df = pd.DataFrame(results)
results_df.to_csv("matched_products.csv", index=False)
print("\n✅ Výsledky uložené do 'matched_products.csv'")
