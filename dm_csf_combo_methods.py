from csf_methods import get_inventory as user_inventory_csf, item_convert_universal_csf, get_user_stall as user_listings_csf
from dm_main import user_inventory as user_inventory_dm, get_user_offers as user_listings_dm
from dm_methods import item_convert_universal_dm
import json
import re


def filtered_inventory():
    dmarket_inventory = []

    for item in user_inventory_dm():
        dm_item_u = item_convert_universal_dm(item)
        dmarket_inventory.append(dm_item_u)

    json.dump(dmarket_inventory, open("dmarket_inventory.json", "w"), indent=4)

    csfloat_inventory = []

    for item in user_inventory_csf():
        csf_item_u = item_convert_universal_csf(item)
        csfloat_inventory.append(csf_item_u)

    json.dump(csfloat_inventory, open("csfloat_inventory.json", "w"), indent=4)

    # Extract unique market_hash_names from both inventories
    csfloat_names = {item["market_hash_name"] for item in csfloat_inventory}
    dmarket_names = {item["market_hash_name"] for item in dmarket_inventory}

    # Find common items
    common_names = csfloat_names & dmarket_names

    # Filter both inventories to keep only common items
    filtered_csfloat = [item for item in csfloat_inventory if item["market_hash_name"] in common_names]
    filtered_dmarket = [item for item in dmarket_inventory if item["market_hash_name"] in common_names]

    filtered_final = []

    # sample_asset_id = "6278491400:310778847:41447471628:730"


    # print(dm_id_to_csf_id(sample_asset_id))

    for item in filtered_csfloat:
        for item2 in filtered_dmarket:
            if item["asset_id_csf"] in item2["asset_id_dm"]:
                item["asset_id_dm"] = item2["asset_id_dm"]
                
                if item["is_listed"] == True or item2["is_listed"] == True:
                    item["is_listed"] = True
                else:
                    item["is_listed"] = False
                    filtered_final.append(item)



    json.dump(filtered_final, open("TKinterTradeTool/db/filtered_final.json", "w"), indent=4)
    return filtered_final

def filtered_listings():
    return

def extract_stickers_from_dmarket(attr):
    stickers = []
    raw = attr.get("modifications", "")
    match = re.search(r'slots:map\[(.*?)\]$', raw)
    if not match:
        return stickers

    slot_str = match.group(1)
    slot_entries = re.findall(r'(\d+):map\[([^\]]+)\]', slot_str)

    for slot, entry in slot_entries:
        name_match = re.search(r'name:([^\s\]]+.*?)(?=\s|$)', entry)
        image_match = re.search(r'image:(https?://[^\s]+)', entry)

        if name_match and image_match:
            stickers.append({
                "name": name_match.group(1),
                "slot": int(slot),
                "icon_url": image_match.group(1)
            })

    return stickers

def parse_dmarket_to_universal(item):
    attr = {a["Name"]: a["Value"] for a in item.get("Attributes", [])}

    # ✅ Extract stickers from Go-style modification string
    stickers = extract_stickers_from_dmarket(attr)

    offer = item.get("Offer", {})
    price_info = offer.get("Price", {"Amount": 0, "Currency": "USD"})

    return {
        "market": "Dmarket",
        "listing_id_dm": item.get("AssetID", ""),
        "offer_id_dm": offer.get("OfferID", ""),
        "listing_id_csf": "",
        "def_index": 0,
        "paint_index": int(attr.get("paintIndex", 0)),
        "float_value": float(attr.get("floatValue", 0)) if "floatValue" in attr else 0.0,
        "is_stattrak": False,
        "is_souvenir": False,
        "keychain": attr.get("charmPattern", ""),
        "market_hash_name": attr.get("title", item.get("Title", "")),
        "stickers": stickers,
        "item_image": attr.get("image", item.get("ImageURL", "")),
        "price": float(price_info.get("Amount", 0)),
        "currency": price_info.get("Currency", "USD")
    }


def parse_csfloat_to_universal(listing):
    item = listing["item"]
    stickers = []
    for s in item.get("stickers", []):
        stickers.append({
            "name": s.get("name", ""),
            "slot": s.get("slot", 0),
            "icon_url": s.get("icon_url", "")
        })

    return {
        "market": "CSfloat",
        "listing_id_dm": "",
        "offer_id_dm": "",
        "listing_id_csf": listing["id"],
        "def_index": item["def_index"],
        "paint_index": item.get("paint_index", 0),
        "float_value": item.get("float_value", 0.0),
        "is_stattrak": item.get("is_stattrak", False),
        "is_souvenir": item.get("is_souvenir", False),
        "keychain": "",
        "market_hash_name": item["market_hash_name"],
        "stickers": stickers,
        "item_image": "https://steamcommunity-a.akamaihd.net/economy/image/" + item["icon_url"],
        "price": float(listing.get("price", 0)) / 100,  # ✅ Normalize price
        "currency": "USD"
    }

def all_listings_universal():
    csfloat_listings_native = user_listings_csf()["data"]
    dmarket_listings_native = user_listings_dm()["Items"]

    csfloat_listings = []
    dmarket_listings = []
    for item in csfloat_listings_native:
        try:
            csfloat_listings.append(parse_csfloat_to_universal(item))
        except Exception as e:
            print(parse_csfloat_to_universal(item))
            return
    for item in dmarket_listings_native:
        dmarket_listings.append(parse_dmarket_to_universal(item))
    
    all_listings = csfloat_listings + dmarket_listings
    # json.dump(all_listings, open("TKinterTradeTool/db/all_listings.json", "w"), indent=4)
    return all_listings

# all_listings_universal()