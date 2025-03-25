import json
from datetime import datetime
from nacl.signing import SigningKey
from nacl.bindings import crypto_sign
import requests

def export_json_to_file(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
        return



# replace with your api keys
secret_key = "693e56289b71bfdeaab7786e5424fdfa09b90f48c3ce0dc509298d23cc61305a7b7bc834646ff0d47c601a0581e3efc8fb526a06d57a1a1c09881ea511f35aab"
public_key = "7b7bc834646ff0d47c601a0581e3efc8fb526a06d57a1a1c09881ea511f35aab"

# change url to prod
rootApiUrl = "https://api.dmarket.com"


# def get_offer_from_market():
#     market_response = requests.get(rootApiUrl + "/exchange/v1/market/items?gameId=a8db&limit=1&currency=USD")
#     offers = json.loads(market_response.text)["objects"]
#     print(offers[0])
#     return offers[0]



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

    print(encoded)
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
    response = requests.get(rootApiUrl + api_url_path, headers=headers)

    # Check if the request is successful
    if response.status_code != 200:
        raise Exception(f"Request failed: {response.status_code} {response.text}")

    # Return the API response
    return response.json()

def dmarket_inventory_create_offers(asset_id, price):
    signature_prefix =  "dmar ed25519 "
    """
    Create a new offer to sell an item in the DMarket inventory.

    Args:
        asset_id (str): The unique identifier of the asset to sell.
        price (float): The price of the offer in USD.
    
    Returns:
        dict: The API response as a JSON object.
    """
    api_url_path = "/marketplace-api/v1/user-offers/create"
    method = "POST" 
    body = {
        "Offers": [
            {
                "AssetID": asset_id,
                "Price": {
                    "Amount": price,
                    "Currency": "USD"
                }
            }
        ]
    }
    body_json = json.dumps(body)
    nonce = str(round(datetime.now().timestamp()))
    string_to_sign = method + api_url_path + body_json + nonce
    encoded = string_to_sign.encode("utf-8")
    print(encoded)
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


def user_offers():
    signature_prefix = "dmar ed25519 "
    """
    Get information about the current listings by user.

    Returns:
        list: The API response as a list of dicts.
    """

    params= {
        "GameID": "a8db"
    }

    query_string = "&".join(f"{key}={value}" for key, value in params.items())
    api_url_path = f"/marketplace-api/v1/user-offers?{query_string}"
    method = "GET"

    # Generate a nonce (timestamp)
    nonce = str(round(datetime.now().timestamp()))
    string_to_sign = method + api_url_path + nonce
    encoded = string_to_sign.encode("utf-8")

    # Sign the string
    signature_bytes = crypto_sign(encoded, bytes.fromhex(secret_key))
    signature = signature_bytes[:64].hex()

    # Construct headers
    headers = {
        "X-Api-Key": public_key,
        "X-Request-Sign": signature_prefix + signature,
        "X-Sign-Date": nonce,
    }

    print(rootApiUrl + api_url_path)
    # Make the GET request
    response = requests.get(rootApiUrl + api_url_path, headers=headers)

    # Check if the request is successful
    if response.status_code != 200:
        raise Exception(f"Request failed: {response.status_code} {response.text}")
    
    return response.json()["Items"]

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
