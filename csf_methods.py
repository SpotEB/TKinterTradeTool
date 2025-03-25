from keys import secret_csf, user_id_csf
import requests
import json
from datetime import datetime

keychain_index_dict = {
    1: "Lil' Ava",
    2: "That's Bananas",
    3: "Lil' Whiskers",
    4: "Lil' Sandy",
    5: "Chicken Lil'",
    6: "Lil' Crass",
    7: "Hot Howl",
    8: "Big Kev",
    9: "Lil' Monster",
    10: "Hot Sauce",
    11: "Diamond Dog",
    12: "Pinch O' Salt",
    13: "Diner Dog",
    14: "Lil' Teacup",
    15: "Lil' SAS",
    16: "Hot Wurst",
    17: "Baby's AK",
    18: "Die-cast AK",
    19: "Pocket AWP",
    20: "Titeenium AWP",
    21: "Baby Karat CT",
    22: "Whittle Knife",
    23: "POP Art",
    24: "Lil' Squirt",
    25: "Disco MAC",
    26: "Backsplash",
    27: "Lil' Cap Gun",
    28: "Hot Hands",
    29: "Semi-Precious",
    30: "Baby Karat T",
    31: "Glamour Shot",
    32: "Stitch-Loaded",
    33: "Lil' Squatch"
}


def export_json_to_file(data, filename="output.json"):
    """
    Exports a JSON object to a file in the same directory.

    Args:
        data (dict): The JSON data to export.
        filename (str): Name of the file to save (default: "output.json").
    """
    with open(filename, "w") as json_file:
        json.dump(data, json_file, indent=4)
    print(f"JSON data has been exported to {filename}")

def str_to_bool(value):
    return value.lower() == "true"

base_url = "https://csfloat.com/api/v1/"

def csf_list_item(asset_id, price):
    url = "https://csfloat.com/api/v1/listings"
    headers = {
        "Authorization": f"{secret_csf}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    data = {
        "asset_id": asset_id,
        "price": price,
        "type": "buy_now"
    }

    response = requests.post(url, json=data, headers=headers)
    return response.json()  # Return the API response

def get_user_stall(limit=1000, user_id=user_id_csf):
    url = f"https://csfloat.com/api/v1/users/{user_id}/stall"
    headers = {
        "Authorization": f"{secret_csf}",
        "Accept": "application/json"
    }
    params = {
        "limit": limit
    }

    response = requests.get(url, headers=headers, params=params)
    return response.json()  # Return the API response

def stall_export():
    export_json_to_file(get_user_stall(), "stall_total.json")

def get_inventory():
    url = "https://csfloat.com/api/v1/me/inventory"
    headers = {
        "Authorization": f"{secret_csf}",
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers)
    return response.json()  # Return the API response as JSON

def inventory_export():
    export_json_to_file(get_inventory(), "inventory_total.json")

def update_listing_price(listing_id: str, price: int):
    """
    Updates the price of a listing on CSFloat.

    :param listing_id: The ID of the listing to update.
    :param price: The new price to set.
    :return: The JSON response from the API.
    """
    url = f"https://csfloat.com/api/v1/listings/{listing_id}"
    headers = {
        "Authorization": f"{secret_csf}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {"price": price}

    try:
        response = requests.patch(url, json=payload, headers=headers)
        response.raise_for_status()  # Raises an error for HTTP codes 4xx/5xx
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


import requests


def search_commodity(def_index, sort_by="lowest_price", limit=40):
    """
    Searches for a specific commodity on CSFloat API.
    
    :param auth_token: Your CSFloat API Authorization token.
    :param def_index: The item's def_index.
    :param sort_by: Sorting order, e.g., "lowest_price" (default: "lowest_price").
    :param limit: Number of results to fetch (default: 40).
    :return: JSON response from the API.
    """
    url = "https://csfloat.com/api/v1/listings"
    params = {
        "limit": limit,
        "sort_by": sort_by,
        "def_index": def_index
    }
    headers = {
        "Authorization": f"{secret_csf}",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code == 200:
        return response.json()["data"]
    else:
        return {"error": f"Request failed with status code {response.status_code}", "details": response.text}





def search_skin(def_index, paint_index, min_float=0, max_float=0.55, limit=40, category=1, sort_by="lowest_price"):
    """
    Searches for a specific item on CSFloat API with additional filtering options.
    
    :param auth_token: Your CSFloat API Authorization token.
    :param def_index: The item's def_index.
    :param paint_index: The item's paint_index.
    :param max_float: The maximum float value to filter by (default: 0.55).
    :param limit: Number of results to fetch (default: 40).
    :param category: The category of the item (default: 1).
    :param sort_by: Sorting order, e.g., "lowest_price" (default: "lowest_price").
    :return: JSON response from the API.
    """
    url = "https://csfloat.com/api/v1/listings"
    params = {
        "limit": limit,
        "category": category,
        "sort_by": sort_by,
        "min_float": min_float,
        "max_float": max_float,
        "def_index": def_index,
        "paint_index": paint_index
    }
    headers = {
        "Authorization": f"{secret_csf}",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code == 200:
        return response.json()["data"]
    else:
        return {"error": f"Request failed with status code {response.status_code}", "details": response.text}





def search_charm(keychain_index):
    """
    Searches for a keychain item on CSFloat API and returns the full JSON response.
    
    :param keychain_index: The keychain index to search for.
    :return: The full JSON response from the API.
    """
    url = "https://csfloat.com/api/v1/listings"
    params = {
        "limit": 40,
        "sort_by": "lowest_price",
        "keychain_index": keychain_index
    }
    headers = {
        "Authorization": f"{secret_csf}",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code == 200:
        return response.json()["data"]
    else:
        return {"error": f"Request failed with status code {response.status_code}", "details": response.text}


def item_convert_universal_csf(item):
    universal_item = {
        "asset_id_dm": "",
        "asset_id_csf": item["asset_id"],
        "def_index": item["def_index"],
        "paint_index": item.get("paint_index", 0),
        "float_value": item.get("float_value", 0),
        "is_stattrak": item.get("is_stattrak", False),
        "is_souvenir": item.get("is_souvenir", False),
        "keychain": "",
        "market_hash_name": item["market_hash_name"],
        "stickers": [],
        "item_image": "https://steamcommunity-a.akamaihd.net/economy/image/" + item["icon_url"]
    }
    


    for sticker in item.get("stickers", []):
        try:
            sticker["name"] = sticker["name"].replace("Sticker | ", "")
            universal_item["stickers"].append({"name": sticker["name"], "price": sticker["reference"]["price"]})
        except:
            universal_item["stickers"].append({"name": sticker["name"], "price": 100000})

    if "keychains" in item:
        universal_item["keychain"] = item["keychains"][0]["name"]


    if "listing_id" in item:
        universal_item["is_listed"] = True
        universal_item["listing_id"] = item["listing_id"]
    else:
        universal_item["is_listed"] = False

    return universal_item


def export_inventory():
    inventory = []
    for item in json.load(open("CSfloat/inventory_total.json")):
        inventory.append(item_convert_universal_csf(item))
    return inventory



def last_sales_csf(item_name):
    """Fetch the last sales history from CSFloat API.

    Args:
        secret_csf (str): The API key for authorization.
        item_name (str): The name of the item (e.g., "AK-47 | Slate (Field-Tested)").
        limit (int, optional): The number of sales to fetch. Default is 10.

    Returns:
        dict: JSON response from the API or an error message.
    """
    # Encode item name for URL
    encoded_item = requests.utils.quote(item_name)

    # API URL
    url = f"https://csfloat.com/api/v1/history/{encoded_item}/sales"

    # Headers (including Authorization)
    headers = {
        "Authorization": f"{secret_csf}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
        return response.json()  # Return JSON response
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}



# export_json_to_file(get_user_stall())
# inventory_export()


def sales_convert_universal_csf(sale):

    universal_sale = {
        "price": sale["price"]/100,
        "float_value": 0
    }
    iso_time = sale["sold_at"]
    sold_dt = datetime.strptime(iso_time, "%Y-%m-%dT%H:%M:%S.%fZ")
    universal_sale["date"] = int(sold_dt.timestamp())

    created_dt = datetime.strptime(sale["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ")

    try:
        universal_sale["float_value"] = sale["item"]["float_value"]
    except:
        pass

    try:
        if (sold_dt - created_dt) < datetime.timedelta(minutes=10):
            universal_sale["is_buyorder"] = True
        else:
            universal_sale["is_buyorder"] = False
    except:
        universal_sale["is_buyorder"] = False
        
    return universal_sale


def listing_convert_universal_csf(item):
    """Convert a 'csf' market listing to the universal format."""
    return {
        "market": "csf",
        "listing_type": item["type"],
        "price": float(item["price"]) / 100,  # Convert cents to dollars
        "float_value": item["item"]["float_value"],
        "stickers": [s["name"] for s in item["item"].get("stickers", [])],  # Extract sticker names
        "trade_lock": None,  # No trade lock info in this market
    }

# print(last_sales_csf("AK-47 | Slate (Field-Tested)"))

# export_json_to_file(get_inventory(), "inventory_total_csf.json")