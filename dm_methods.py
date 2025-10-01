import json
import re

def extract_sticker_names(value):
    # Use regex to find all occurrences of name:<sticker_name>
    return re.findall(r'name:([^ ]+)', value)

def convert_title_def_index(title):
    with open("db/dmarket_def_index.json", "r") as f:
        def_indexes = json.load(f)

    # Normalize title: lowercase and remove skin/wear details
    title = title.lower()
    base_title = re.split(r"\s*\|", title)[0].strip()  # Get only the weapon name

    # Look for the weapon name in the def_indexes dictionary
    for key in def_indexes:
        if key.lower() == base_title:
            return def_indexes[key]
    
    return ""

def extract_attr(attributes, name):
    for attr in attributes:
        if attr.get("Name") == name:
            return attr.get("Value", "")
    return ""


def sales_convert_universal_dm(sale):
    universal_sale = {
        "price": float(sale["price"]),
        "date": sale["date"],
        "float_value": 0
    }

    try:
        universal_sale["float_value"] = sale["offerAttributes"]["floatValue"]
    except:
        pass

    try:
        if sale["txOperationType"] == "Offer":
            universal_sale["is_buyorder"] = False
        else:
            universal_sale["is_buyorder"] = True
    except:
        universal_sale["is_buyorder"] = False
    
    return universal_sale


def has_charms(attributes):
    for attr in attributes:
        if attr.get("Name") == "charms":
            return True
    return False

def extract_charm_name(charms_string):
    # Using regex to find the name pattern
    match = re.search(r'name:([^ ]+ [^ ]+)', charms_string)
    if match:
        return match.group(1)
    return None


def item_convert_universal_dm(item):

    universal_item = {
        "asset_id_dm": item["AssetID"],
        "asset_id_csf": "",
        "def_index": convert_title_def_index(item["Title"]),
        "paint_index": extract_attr(item["Attributes"], "paintIndex"),
        "float_value": extract_attr(item["Attributes"], "floatValue"),
        "keychain": "",
        "market_hash_name": item["Title"],
        "item_image": item["ImageURL"]
    }
    
    if universal_item["paint_index"] == "":
        pass
    else:
        universal_item["paint_index"] = int(universal_item["paint_index"])

    if universal_item["float_value"] == "":
        universal_item["float_value"] = 0
    else:
        universal_item["float_value"] = float(universal_item["float_value"])

    stickers_count = extract_attr(item["Attributes"], "stickersCount")
    if stickers_count.isdigit() and int(stickers_count) > 0:
        sticker_list = extract_sticker_names(extract_attr(item["Attributes"], "stickers"))
        universal_item["stickers"] = [{"name": name, "price": False} for name in sticker_list]
    else:
        universal_item["stickers"] = []
    
    category = extract_attr(item["Attributes"], "category")

    if category == "normal":
        universal_item["is_stattrak"] = False
        universal_item["is_souvenir"] = False
    elif category == "souvenir":
        universal_item["is_stattrak"] = False
        universal_item["is_souvenir"] = True
    elif category == "stattrak\u2122":
        universal_item["is_stattrak"] = True
        universal_item["is_souvenir"] = False
    
    if has_charms(item["Attributes"]):
        charm_name = extract_charm_name(extract_attr(item["Attributes"], "charms"))
        universal_item["keychain"] = charm_name
    else:
        universal_item["keychain"] = ""

    universal_item["is_listed"] = False

    return universal_item

    


