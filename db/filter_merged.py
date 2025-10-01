import json

# Load the JSON file
with open("db/merged_inventory.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Filter out items where "item_image" starts with the unwanted prefix
filtered_data = [
    item for item in data
    if not item.get("item_image", "").startswith("https://steamcommunity-a.akamaihd.net/economy/image/6TMc")
]

# Save the filtered data back to a new JSON file
with open("db/merged_inventory_final.json", "w", encoding="utf-8") as file:
    json.dump(filtered_data, file, indent=4)

print(f"Filtered inventory saved to filtered_inventory.json ({len(filtered_data)} items remaining)")
