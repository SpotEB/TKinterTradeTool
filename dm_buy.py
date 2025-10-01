import json
from datetime import datetime
from nacl.signing import SigningKey
from nacl.bindings import crypto_sign
import requests
from keys import secret_key_dm as secret_key, public_key_dm as public_key

import threading
import time

def export_json_to_file(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
        return



# change url to prod
rootApiUrl = "https://api.dmarket.com"



offer1 = json.loads("""{
            "itemId": "d94bc63f-fac7-5c15-8466-5e0aed17c525",
            "type": "offer",
            "amount": 1,
            "classId": "188532885:4578724383",
            "gameId": "a8db",
            "gameType": "steam",
            "inMarket": true,
            "lockStatus": false,
            "title": "StatTrak\u2122 MP9 | Mount Fuji (Field-Tested)",
            "description": "",
            "image": "https://steamcommunity-a.akamaihd.net/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgpou6r8FAZh7P7YKAJE-da_q5CCmfzLPr7Vn35cppV1j-uQrd30jAfkrhdkNzz0LILGegBvZFvZqwTrkufrgpS7tciawHZ9-n51zQtuLa4",
            "slug": "mp9-mount-fuji",
            "owner": "a4ec4d29-1d42-4283-8b6f-3c021e10bb6b",
            "ownersBlockchainId": "c31ceb8a2f0c5b2daa8f7a6f9313c9bc8aff7ff9fdcc0c9f3a80fecce8939b35",
            "ownerDetails": {
                "id": "a4ec4d29-1d42-4283-8b6f-3c021e10bb6b",
                "avatar": "https://cdn-main.dmarket.com/default-images/avatar.svg",
                "wallet": "c31ceb8a2f0c5b2daa8f7a6f9313c9bc8aff7ff9fdcc0c9f3a80fecce8939b35"
            },
            "status": "active",
            "discount": 0,
            "price": {
                "DMC": "",
                "USD": "949"
            },
            "instantPrice": {
                "DMC": "",
                "USD": ""
            },
            "exchangePrice": {
                "DMC": "",
                "USD": ""
            },
            "instantTargetId": "",
            "suggestedPrice": {
                "DMC": "",
                "USD": "895"
            },
            "recommendedPrice": {
                "offerPrice": {
                    "DMC": "",
                    "USD": ""
                },
                "d3": {
                    "DMC": "",
                    "USD": ""
                },
                "d7": {
                    "DMC": "",
                    "USD": ""
                },
                "d7Plus": {
                    "DMC": "",
                    "USD": ""
                }
            },
            "extra": {
                "nameColor": "cf6a32",
                "backgroundColor": "8847ff",
                "tradable": false,
                "offerId": "17f3de98-30ac-4435-bed1-59e891d75237",
                "isNew": false,
                "gameId": "a8db",
                "name": "MP9 | Mount Fuji",
                "categoryPath": "smg/mp9",
                "viewAtSteam": "https://steamcommunity.com/profiles/76561199261963848/inventory/#730_2_41487034485",
                "groupId": "76561199261963848",
                "linkId": "af4250b6-9b24-5f73-9b7a-e5af24f38801",
                "exterior": "field-tested",
                "quality": "restricted",
                "category": "stattrak\u2122",
                "tradeLock": 2,
                "tradeLockDuration": 214266,
                "itemType": "smg",
                "floatValue": 0.3440370261669159,
                "floatPartValue": "FT-4",
                "paintIndex": 1094,
                "paintSeed": 257,
                "inspectInGame": "steam://rungame/730/76561202255233023/+csgo_econ_action_preview%20S76561199261963848A41487034485D3216696859736951350",
                "collection": [
                    "operation riptide"
                ],
                "saleRestricted": false,
                "inGameAssetID": "678fa7ab6013f80a545d217c",
                "emissionSerial": "678fa7ab6013f80a545d217c",
                "sagaAddress": "0x184a830B8C09c7D085e8074E33c5e239c3BadC27"
            },
            "createdAt": 1737509598,
            "deliveryStats": {
                "rate": "",
                "time": ""
            },
            "fees": {
                "f2f": {
                    "sell": {
                        "default": {
                            "percentage": "",
                            "minFee": {
                                "DMC": "",
                                "USD": ""
                            }
                        }
                    },
                    "instantSell": {
                        "default": {
                            "percentage": "",
                            "minFee": {
                                "DMC": "",
                                "USD": ""
                            }
                        }
                    },
                    "exchange": {
                        "default": {
                            "percentage": "",
                            "minFee": {
                                "DMC": "",
                                "USD": ""
                            }
                        }
                    }
                },
                "dmarket": {
                    "sell": {
                        "default": {
                            "percentage": "",
                            "minFee": {
                                "DMC": "",
                                "USD": ""
                            }
                        }
                    },
                    "instantSell": {
                        "default": {
                            "percentage": "",
                            "minFee": {
                                "DMC": "",
                                "USD": ""
                            }
                        }
                    },
                    "exchange": {
                        "default": {
                            "percentage": "",
                            "minFee": {
                                "DMC": "",
                                "USD": ""
                            }
                        }
                    }
                }
            },
            "discountPrice": {
                "DMC": "",
                "USD": ""
            },
            "productId": "a8db:31aee78d632ab1cc0b39bf67eb606caf",
            "favoriteFor": 0,
            "favoriteForUser": false,
            "favorite": {
                "count": 0,
                "forUser": false
            }
        }
""")

def build_target_body_from_offer(offer):
    return {"targets": [
        {"amount": 1, "gameId": offer["gameId"], "price": {"amount": "200", "currency": "USD"},
        "attributes": {"gameId": offer["gameId"],
                        "categoryPath": offer["extra"]["categoryPath"],
                        "title": offer["title"],
                        "name": offer["title"],
                        "image": offer["image"],
                        "ownerGets": {"amount": "1", "currency": "USD"}}}
    ]}

def build_buy_body_from_offers(offers):
    offers_list = []
    for i in offers:
        offers_list.append(
            {
            "offerId": i["extra"]["offerId"],
            "price": {
                "amount": i["price"]["USD"],
                "currency": "USD"
                },
            "type": "dmarket"
            })
    offers_body = {"offers": offers_list}
    return offers_body



def target_create(offer, price):
    nonce = str(round(datetime.now().timestamp()))
    api_url_path = "/exchange/v1/target/create"
    method = "POST"
    body = build_target_body_from_offer(offer)
    string_to_sign = method + api_url_path + json.dumps(body) + nonce
    signature_prefix = "dmar ed25519 "
    encoded = string_to_sign.encode('utf-8')
    signature_bytes = crypto_sign(encoded, bytes.fromhex(secret_key))
    signature = signature_bytes[:64].hex()
    headers = {
        "X-Api-Key": public_key,
        "X-Request-Sign": signature_prefix + signature,
        "X-Sign-Date": nonce
    }

    return requests.post(rootApiUrl + api_url_path, json=body, headers=headers)


def buy_item(offers):
    nonce = str(round(datetime.now().timestamp()))
    api_url_path = "/exchange/v1/offers-buy"
    method = "PATCH"
    body = build_buy_body_from_offers(offers)
    string_to_sign = method + api_url_path + json.dumps(body) + nonce
    signature_prefix = "dmar ed25519 "
    encoded = string_to_sign.encode('utf-8')
    signature_bytes = crypto_sign(encoded, bytes.fromhex(secret_key))
    signature = signature_bytes[:64].hex()
    headers = {
        "X-Api-Key": public_key,
        "X-Request-Sign": signature_prefix + signature,
        "X-Sign-Date": nonce
    }
    return requests.patch(rootApiUrl + api_url_path, json=body, headers=headers)



def deposit_assets(asset_ids):
    signature_prefix = "dmar ed25519 "
    """
    Transfers items from a third-party inventory (e.g., Steam) to the DMarket inventory.

    Args:
        asset_ids (list): A list of asset IDs to deposit.

    Returns:
        dict: The API response as a JSON object.
    """
    if not asset_ids or not isinstance(asset_ids, list):
        raise ValueError("asset_ids must be a non-empty list of strings.")

    api_url_path = "/marketplace-api/v1/deposit-assets"
    method = "POST"

    # Construct the request body
    body = {"GameID": "a8db", "AssetID": asset_ids}
    body_json = json.dumps(body)

    # Generate a nonce (timestamp)
    nonce = str(round(datetime.now().timestamp()))

    # Create the string to sign
    string_to_sign = method + api_url_path + body_json + nonce
    encoded = string_to_sign.encode("utf-8")

    # Decode the secret key and sign the string
    signature_bytes = crypto_sign(encoded, bytes.fromhex(secret_key))
    signature = signature_bytes[:64].hex()

    # Construct headers
    headers = {
        "X-Api-Key": public_key,
        "X-Request-Sign": signature_prefix + signature,
        "X-Sign-Date": nonce,
        "Content-Type": "application/json",
    }

    # Make the POST request
    response = requests.post(rootApiUrl + api_url_path, json=body, headers=headers)

    # Check if the request is successful
    if response.status_code != 200:
        raise Exception(f"Request failed: {response.status_code} {response.text}")

    # Return the API response
    return response.json()


def get_deposit_status(deposit_id):
    signature_prefix = "dmar ed25519 "
    """
    Get information about the current status of a deposit transfer.

    Args:
        deposit_id (str): The unique identifier of the deposit operation.

    Returns:
        dict: The API response as a JSON object.
    """
    if not deposit_id or not isinstance(deposit_id, str):
        raise ValueError("deposit_id must be a non-empty string.")

    api_url_path = f"/marketplace-api/v1/deposit-status/{deposit_id}"
    method = "GET"

    # Generate a nonce (timestamp)
    nonce = str(round(datetime.now().timestamp()))

    # Create the string to sign
    string_to_sign = method + api_url_path + nonce
    encoded = string_to_sign.encode("utf-8")

    # Decode the secret key and sign the string
    signature_bytes = crypto_sign(encoded, bytes.fromhex(secret_key))
    signature = signature_bytes[:64].hex()

    # Construct headers
    headers = {
        "X-Api-Key": public_key,
        "X-Request-Sign": signature_prefix + signature,
        "X-Sign-Date": nonce,
    }

    # Make the GET request
    print(string_to_sign)
    response = requests.get(rootApiUrl + api_url_path, headers=headers)
    
    # Check if the request is successful
    if response.status_code != 200:
        raise Exception(f"Request failed: {response.status_code} {response.text}")

    # Return the API response
    return response.json()

def format_for_listing(items):
    """
    Format items for listing on DMarket.
    
    Args:
    items (list): list of dicts containing "id" and "price" keys.
    """
    listings = []
    for i in range(len(items)):
        listing = {
            "AssetID": items[i]["id"],
            "Price": {
                "Amount": items[i]["price"],
                "Currency": "USD"
            }
        }
        listings.append(listing)
    return listings

def create_listings(items):
    signature_prefix = "dmar ed25519 "
    """
    Create listings for items in the DMarket inventory.
    You MUST use the format_for_listing function to format the items before calling this function.""
    """
    api_url_path = "/marketplace-api/v1/user-offers/create"
    method = "POST"
    nonce = str(round(datetime.now().timestamp()))
    body = {"Offers": items}
    body_json = json.dumps(body)
    string_to_sign = method + api_url_path + body_json + nonce
    encoded = string_to_sign.encode("utf-8")
    signature_bytes = crypto_sign(encoded, bytes.fromhex(secret_key))
    signature = signature_bytes[:64].hex()
    headers = {
        "X-Api-Key": public_key,
        "X-Request-Sign": signature_prefix + signature,
        "X-Sign-Date": nonce,
        "Content-Type": "application/json",
    }
    response = requests.post(rootApiUrl + api_url_path, json=body, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Request failed: {response.status_code} {response.text}")
    
    return response.json()

def edit_offers(items):
    signature_prefix = "dmar ed25519 "

    """
    Edit an existing offer by changing the price.

    Args:
        items (list): A list of items to edit. Each item should be a dictionary with the following keys
            - OfferID (str): The unique identifier of the offer.
            - AssetID (str): The unique identifier of the asset.
            - Price (float): The new price of the offer USD.
    
    Returns:
        dict: The API response as a JSON object.
    """
    http_method = "POST"
    api_url_path = "/marketplace-api/v1/user-offers/edit"
    nonce = str(round(datetime.now().timestamp()))
    body = {"Offers": [{"OfferID": item["OfferID"], "AssetID": item["AssetID"], "Price": {"Amount": item["Price"], "Currency": "USD"}} for item in items]}
    body_json = json.dumps(body)
    string_to_sign = http_method + api_url_path + body_json + nonce
    encoded = string_to_sign.encode("utf-8")

    signature_bytes = crypto_sign(encoded, bytes.fromhex(secret_key))
    signature = signature_bytes[:64].hex()

    headers = {
        "X-Api-Key": public_key,
        "X-Request-Sign": signature_prefix + signature,
        "X-Sign-Date": nonce,
        "Content-Type": "application/json",
    }

    response = requests.post(rootApiUrl + api_url_path, json=body, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Request failed: {response.status_code} {response.text}")

    return response.json()

def create_listings_from_inventory(items, callback=None):
    """
    Deposit items to the marketplace and list them once transfer is successful.

    Args:
        items (list): List of dicts with keys "id" and "price".
        callback (function): Optional callback to call with the result of `create_listings()`.

    Returns:
        None (runs asynchronously in background thread)
    """

    item_inventory_ids = [item["id"] for item in items]

    # Step 1: Deposit
    deposit_response = deposit_assets(item_inventory_ids)
    deposit_id = deposit_response["DepositID"]
    print(f"[{time.strftime('%X')}] Deposit initiated: {deposit_id}")

    def poll_deposit_status():
        while True:
            status = get_deposit_status(deposit_id)
            print(f"[{time.strftime('%X')}] Status: {status['Status']}")

            if status["Status"] == "TransferStatusPending":
                time.sleep(20)
                continue

            if status["Status"] == "TransferStatusSuccess":
                print(f"[{time.strftime('%X')}] Transfer complete.")
                print("Assets:", status["Assets"])

                # Step 2: Match deposited items to original items
                # Force both to string and print for debug
                asset_map = {str(a["InGameAssetID"]).strip(): a["DmarketAssetID"] for a in status["Assets"]}
                listings = []

                print("🔍 Matching debug:")
                print("Original items:")
                for item in items:
                    print(f"  item['id']: {repr(item['id'])} ({type(item['id'])})")

                print("Returned asset keys:")
                for key in asset_map:
                    print(f"  asset_map key: {repr(key)}")

                for item in items:
                    original_id = str(item["id"]).strip()  # Force string & strip whitespace
                    price = item["price"]
                    dmarket_id = asset_map.get(original_id)

                    print(f"Matching {original_id} → {dmarket_id}")

                    if dmarket_id:
                        listings.append({"id": dmarket_id, "price": price})


                # Step 3: Format and list the items
                if listings:
                    formatted = format_for_listing(listings)
                    listing_result = create_listings(formatted)
                    print(f"[{time.strftime('%X')}] ✅ Listings created.")

                    if callback:
                        callback(listing_result)  # Pass the listing result back
                    return

                print(f"[{time.strftime('%X')}] ❌ No matching assets found. Nothing listed.")
                if callback:
                    callback(None)
                return

            if status["Error"]:
                print(f"[{time.strftime('%X')}] Deposit error: {status['Error']}")
                if callback:
                    callback(None)
                return

            print(f"[{time.strftime('%X')}] Unexpected status: {status['Status']}")
            if callback:
                callback(None)
            return

    # Launch background thread
    thread = threading.Thread(target=poll_deposit_status, daemon=True)
    thread.start()


# create_listings_from_inventory([
#     {"id": "480085569:469480270:41472727309:730", "price": 2.5}
#     ])

# try:
#     while True:
#         time.sleep(1)
# except KeyboardInterrupt:
#     print("Exiting...")
#     exit(0)