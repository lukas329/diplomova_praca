import pandas as pd

# Načítanie CSV súborov
paired_df = pd.read_csv("paired.csv")
matched_df = pd.read_csv("matched_products.csv")

# Vyčistenie matched_df od NULL our_id
null_our_id_df = matched_df[matched_df["our_id"].isnull()]
null_our_id_df[["market_id"]].to_csv("null_our_ids.csv", index=False)
matched_df = matched_df.dropna(subset=["our_id"])

# Pretypovanie na int pre merge
paired_df["articleid"] = paired_df["articleid"].astype(int)
paired_df["articleMarketId"] = paired_df["articleMarketId"].astype(str)
matched_df["our_id"] = matched_df["our_id"].astype(int)
matched_df["market_id"] = matched_df["market_id"].astype(str)

# Merge podľa our_id == articleid
merged_df = matched_df.merge(paired_df, left_on="our_id", right_on="articleid", how="left")

# Porovnanie market_id
merged_df["match"] = merged_df["market_id"] == merged_df["articleMarketId"]

# Výpis výsledkov
correct_matches = merged_df["match"].sum()
incorrect_matches = (~merged_df["match"]).sum()

print(f"Počet správnych priradení: {correct_matches}")
print(f"Počet nesprávnych priradení: {incorrect_matches}")

# Uloženie výsledkov
merged_df[["our_id", "market_id", "articleid", "articleMarketId", "match"]].to_csv("match_results.csv", index=False)