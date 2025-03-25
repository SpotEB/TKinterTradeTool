from keys import secret_key, public_key
import requests
import time
from nacl.bindings import crypto_sign
import json
from urllib.parse import urlencode
import dm_buy as dm_buy
from dm_methods import item_convert_universal_dm


# f"{http_method}{route_path_query}{body_string}{timestamp}"
secret_bytes = bytes.fromhex(secret_key)
signature_prefix = "dmar ed25519 "


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




def balance():
    time_str = str(int(time.time()))

    string_to_sign = f"GET/account/v1/balance{time_str}"
    encoded = string_to_sign.encode('utf-8')
    signature_bytes = crypto_sign(encoded, secret_bytes)
    signature = signature_bytes[:64].hex()


    
    
    headers = {"X-Api-Key": public_key, "X-Sign-Date": time_str,
        "X-Request-Sign": signature_prefix + signature}

    response = requests.get("https://api.dmarket.com/account/v1/balance", headers=headers)
    return response.json().get("usd")

def user_inventory():
    base_url = "https://api.dmarket.com/marketplace-api/v1/user-inventory"
    params = {"Limit": 100,
              "GameID": "a8db"
            #   ,
            # "BasicFilters.InMarket": "true"
            }  # Start with the limit of 100
    full_inventory = []  # List to store all inventory items
    next_cursor = None  # Cursor for pagination

    while True:
        # Generate the current timestamp
        time_str = str(int(time.time()))

        # Update params to include the cursor if available
        if next_cursor:
            params["Cursor"] = next_cursor

        # Construct the query string from params
        query_string = "&".join(f"{key}={value}" for key, value in params.items())
        route_with_query = f"/marketplace-api/v1/user-inventory?{query_string}"

        # Construct the unsigned string including params
        string_to_sign = f"GET{route_with_query}{time_str}"
        encoded = string_to_sign.encode('utf-8')

        # Sign the string
        signature_bytes = crypto_sign(encoded, secret_bytes)
        signature = signature_bytes[:64].hex()

        # Headers with the signature
        headers = {
            "X-Api-Key": public_key,
            "X-Sign-Date": time_str,
            "X-Request-Sign": signature_prefix + signature
        }

        # Make the API request
        response = requests.get(base_url, headers=headers, params=params)

        # Check if the request is successful
        if response.status_code != 200:
            raise Exception(f"Request failed: {response.status_code} {response.text}")

        # Parse the JSON response
        data = response.json()

        # Add items to the full inventory
        full_inventory.extend(data.get("Items", []))  # Replace 'items' with the actual key in the response

        # Check for the next cursor
        next_cursor = data.get("Cursor")
        if not next_cursor:
            break  # No more pages, exit the loop
            
    return full_inventory

def get_customized_fees():
    base_url = "https://api.dmarket.com/exchange/v1/customized-fees"
    params = {
        "gameId": "a8db",  # CS:GO gameId
        "offerType": "dmarket",  # Use "dmarket" as the offer type
        "Limit": "100000"
    }

    # Generate the current timestamp
    time_str = str(int(time.time()))

    # Construct the query string from params
    query_string = "&".join(f"{key}={value}" for key, value in params.items())
    route_with_query = f"/exchange/v1/customized-fees?{query_string}"

    # Construct the unsigned string including params
    string_to_sign = f"GET{route_with_query}{time_str}"
    encoded = string_to_sign.encode('utf-8')

    # Sign the string
    signature_bytes = crypto_sign(encoded, secret_bytes)
    signature = signature_bytes[:64].hex()

    # Headers with the signature
    headers = {
        "X-Api-Key": public_key,
        "X-Sign-Date": time_str,
        "X-Request-Sign": signature_prefix + signature
    }

    # Make the API request
    response = requests.get(base_url, headers=headers, params=params)

    # Check if the request is successful
    if response.status_code != 200:
        raise Exception(f"Request failed: {response.status_code} {response.text}")

    # Return the JSON response
    return response.json()

# reduced_fees = get_customized_fees()

# export_json_to_file(reduced_fees, "reduced_fees.json")

def listing_convert_universal_dm(item):
    """Convert a 'dm' market listing to the universal format."""
    return {
        "market": "dm",
        "price": float(item["price"]["USD"]) / 100 if item["price"]["USD"] else None,  # Convert cents to dollars
        "float_value": item["extra"].get("floatValue", None),
        "stickers": [s["name"] for s in item["extra"].get("stickers", [])],  # Extract sticker names
        "trade_lock": item["extra"].get("tradeLockDuration", 0),
    }


def offers_by_title(title, limit=20):
    base_url = "https://api.dmarket.com/exchange/v1/offers-by-title"
    params = {
        "Title": title,  # The item name on the market
        "Limit": limit,
        "order_by": "price",
        "order_dir": "asc"
    }

    # Generate the current timestamp
    time_str = str(int(time.time()))

    # Construct the query string from params
    query_string = "&".join(f"{key}={value}" for key, value in params.items())
    route_with_query = f"/exchange/v1/offers-by-title?{query_string}"

    # Construct the unsigned string including params
    string_to_sign = f"GET{route_with_query}{time_str}"
    encoded = string_to_sign.encode('utf-8')

    # Sign the string
    signature_bytes = crypto_sign(encoded, secret_bytes)
    signature = signature_bytes[:64].hex()

    # Headers with the signature
    headers = {
        "X-Api-Key": public_key,
        "X-Sign-Date": time_str,
        "X-Request-Sign": signature_prefix + signature
    }

    # Make the API request
    response = requests.get(base_url, headers=headers, params=params)

    # Check if the request is successful
    if response.status_code != 200:
        raise Exception(f"Request failed: {response.status_code} {response.text}")

    # Return the JSON response
    return response.json()["objects"]

def get_aggregated_prices(titles):
    """
    Get the best market prices grouped by item market title.

    Args:
        titles (list): A list of item titles to query.

    Returns:
        dict: JSON response with aggregated prices.
    """
    base_url = "https://api.dmarket.com/price-aggregator/v1/aggregated-prices"
    
    # Prepare query parameters (URL-encoded)
    params = [("Titles", title) for title in titles]  # List of tuples for multiple Titles
    query_string = urlencode(params)  # Encode the parameters
    full_url = f"{base_url}?{query_string}"

    # Generate the current timestamp
    time_str = str(int(time.time()))

    # Construct the unsigned string (include the query string in the signature)
    route_with_query = f"/price-aggregator/v1/aggregated-prices?{query_string}"
    string_to_sign = f"GET{route_with_query}{time_str}"
    encoded = string_to_sign.encode('utf-8')

    # Sign the string
    signature_bytes = crypto_sign(encoded, secret_bytes)
    signature = signature_bytes[:64].hex()

    # Headers with the signature
    headers = {
        "X-Api-Key": public_key,
        "X-Sign-Date": time_str,
        "X-Request-Sign": signature_prefix + signature
    }

    # Make the API request
    response = requests.get(full_url, headers=headers)

    # Check if the request is successful
    if response.status_code != 200:
        raise Exception(f"Request failed: {response.status_code} {response.text}")

    # Return the JSON response
    return response.json()

def get_targets_by_title(title):
    """
    Fetch targets by title for the specified game ID (a8db).

    Args:
        title (str): The title of the item.

    Returns:
        dict: JSON response with targets by title.
    """
    base_url = "https://api.dmarket.com/marketplace-api/v1/targets-by-title"
    game_id = "a8db"  # CS:GO game ID
    endpoint = f"{base_url}/{game_id}/{title}"

    # Generate the current timestamp
    time_str = str(int(time.time()))

    # Construct the unsigned string
    route_with_query = f"/marketplace-api/v1/targets-by-title/{game_id}/{title}"
    string_to_sign = f"GET{route_with_query}{time_str}"
    encoded = string_to_sign.encode('utf-8')

    # Sign the string
    signature_bytes = crypto_sign(encoded, secret_bytes)
    signature = signature_bytes[:64].hex()

    # Headers with the signature
    headers = {
        "X-Api-Key": public_key,
        "X-Sign-Date": time_str,
        "X-Request-Sign": signature_prefix + signature
    }

    # Make the API request
    response = requests.get(endpoint, headers=headers)

    # Check if the request is successful
    if response.status_code != 200:
        raise Exception(f"Request failed: {response.status_code} {response.text}")
    print(response.text)

    # Return the JSON response
    return response.json()

def get_market_items(
    title=None,
    game_id="a8db",  # Default to CS:GO
    currency="USD",
    limit=50,
    offset=0,
    order_by="title",
    order_dir="desc",
    tree_filters=None,
    price_from=0,
    price_to=0,
    types=None,
    cursor=None
):
    """
    Fetch a list of items available for purchase on DMarket.

    Args:
        game_id (str): The game ID (default is "a8db" for CS:GO).
        currency (str): Currency (default is "USD").
        title (str): Filter by item title.
        limit (int): Maximum number of items to return (default: 50).
        offset (int): Starting point for results (default: 0).
        order_by (str): Field to order results by (default: "title").
        order_dir (str): Direction to order results (default: "desc").
        tree_filters (str): Filter by specific tree.
        price_from (int): Minimum price in cents (default: 0).
        price_to (int): Maximum price in cents (default: 0).
        types (str): Comma-separated list of item types.
        cursor (str): Cursor for pagination.

    Returns:
        dict: JSON response with the market items.
    """
    base_url = "https://api.dmarket.com/exchange/v1/market/items"
    params = {
        "gameId": game_id,
        "currency": currency,
        "limit": limit,
        "offset": offset,
        "orderBy": order_by,
        "orderDir": order_dir,
    }

    # Add optional parameters if provided
    if title:
        params["title"] = title
    if tree_filters:
        params["treeFilters"] = tree_filters
    if price_from > 0:
        params["priceFrom"] = price_from
    if price_to > 0:
        params["priceTo"] = price_to
    if types:
        params["types"] = types
    if cursor:
        params["cursor"] = cursor

    # Generate the current timestamp
    time_str = str(int(time.time()))

    # Encode the parameters into a query string
    query_string = urlencode(params)
    route_with_query = f"/exchange/v1/market/items?{query_string}"

    # Construct the unsigned string
    string_to_sign = f"GET{route_with_query}{time_str}"
    encoded = string_to_sign.encode('utf-8')

    # Sign the string
    signature_bytes = crypto_sign(encoded, secret_bytes)
    signature = signature_bytes[:64].hex()

    # Headers with the signature
    headers = {
        "X-Api-Key": public_key,
        "X-Sign-Date": time_str,
        "X-Request-Sign": signature_prefix + signature
    }

    # Make the API request
    response = requests.get(base_url, headers=headers, params=params)

    # Check if the request is successful
    if response.status_code != 200:
        raise Exception(f"Request failed: {response.status_code} {response.text}")

    # Return the JSON response
    return response.json()

def filter_by_median_float(data):
    """
    Filters a list of dictionaries to retain only those with a floatValue
    greater than or equal to the median floatValue.

    Args:
        data (list): A list of dictionaries, each containing "offerAttributes" with "floatValue".

    Returns:
        list: A filtered list of dictionaries with floatValue >= median.
    """
    if not data:
        return []

    # Extract all floatValue values
    float_values = [item["offerAttributes"]["floatValue"] for item in data]

    # Sort the float values to find the median
    float_values.sort()
    n = len(float_values)

    if n % 2 == 0:
        # Median for even number of elements
        median = (float_values[n // 2 - 1] + float_values[n // 2]) / 2
    else:
        # Median for odd number of elements
        median = float_values[n // 2]

    # Filter the list of dictionaries to include only those with floatValue >= median
    filtered_data = [item for item in data if item["offerAttributes"]["floatValue"] >= median]

    return filtered_data

def get_last_sales(
    title=None,  # Required: title of the item
    game_id="a8db",  # Default to CS:GO
    filters=None,
    tx_operation_type=None,
    limit=500,
    offset=0
):
    """
    Fetch the item sales history from the DMarket API.

    Args:
        game_id (str): The game ID (default: "a8db" for CS:GO).
        title (str): The title of the item (required).
        filters (str): Filters for the query (e.g., "exterior[]=factory new").
        tx_operation_type (str): Transaction type (e.g., "Target", "Offer").
        limit (int): Maximum number of sales to return (min: 1, max: 500).
        offset (int): The starting point for results (default: 0).

    Returns:
        dict: JSON response with sales history.
    """
    if not title:
        raise ValueError("Title is required.")

    base_url = "https://api.dmarket.com/trade-aggregator/v1/last-sales"
    params = {
        "gameId": game_id,
        "title": title,
        "limit": limit,
        "offset": offset
    }

    # Add optional parameters if provided
    if filters:
        params["filters"] = filters
    if tx_operation_type:
        params["txOperationType"] = tx_operation_type

    # Generate the current timestamp
    time_str = str(int(time.time()))

    # Encode the parameters into a query string
    query_string = urlencode(params)
    route_with_query = f"/trade-aggregator/v1/last-sales?{query_string}"

    # Construct the unsigned string
    string_to_sign = f"GET{route_with_query}{time_str}"
    encoded = string_to_sign.encode('utf-8')

    # Sign the string
    signature_bytes = crypto_sign(encoded, secret_bytes)
    signature = signature_bytes[:64].hex()

    # Headers with the signature
    headers = {
        "X-Api-Key": public_key,
        "X-Sign-Date": time_str,
        "X-Request-Sign": signature_prefix + signature
    }

    # Make the API request
    full_url = f"{base_url}?{query_string}"
    response = requests.get(full_url, headers=headers)

    # Check if the request is successful
    if response.status_code != 200:
        raise Exception(f"Request failed: {response.status_code} {response.text}")

    # raw_sales = response.json()
    # float_above_median = filter_by_median_float(raw_sales)

    # recent_sale_generic = 0


    # Return the JSON response
    return response.json()["sales"]

def get_user_offers(
    game_id="a8db",  # Default to CS:GO
    status=None,  # Offer status
    sort_type="UserOffersSortTypeDefault",  # Default sorting type
    price_from=None,  # Minimum price filter
    price_to=None,  # Maximum price filter
    currency=None,  # Currency for price filtering
    limit=10,  # Max number of results (default: 10)
    offset=0,  # Offset for pagination
    cursor=None  # Pagination cursor
):
    """
    Fetch user offers from the DMarket API.

    Args:
        game_id (str): The game ID (default: "a8db" for CS:GO).
        status (str): Offer status filter.
        sort_type (str): Sorting type (default: UserOffersSortTypeDefault).
        price_from (float): Minimum price filter.
        price_to (float): Maximum price filter.
        currency (str): Currency filter.
        limit (int): Max number of results to return (default: 10).
        offset (int): Offset for pagination (default: 0).
        cursor (str): Cursor for paginated requests.

    Returns:
        dict: JSON response with user offers.
    """
    base_url = "https://api.dmarket.com/marketplace-api/v1/user-offers"
    params = {
        "gameId": game_id,
        "limit": limit,
        "offset": offset,
    }

    # Add optional parameters if provided
    if status:
        params["Status"] = status
    if sort_type:
        params["SortType"] = sort_type
    if price_from:
        params["BasicFilters.PriceFrom"] = price_from
    if price_to:
        params["BasicFilters.PriceTo"] = price_to
    if currency:
        params["BasicFilters.Currency"] = currency
    if cursor:
        params["Cursor"] = cursor

    # Generate the current timestamp
    time_str = str(int(time.time()))

    # time_str = "1739156035"

    # Encode the parameters into a query string
    query_string = urlencode(params)
    route_with_query = f"/marketplace-api/v1/user-offers?{query_string}"

    # Construct the unsigned string
    string_to_sign = f"GET{route_with_query}{time_str}"
    encoded = string_to_sign.encode('utf-8')

    # Sign the string
    signature_bytes = crypto_sign(encoded, secret_bytes)
    signature = signature_bytes[:64].hex()

    # Headers with the signature
    headers = {
        "X-Api-Key": public_key,
        "X-Sign-Date": time_str,
        "X-Request-Sign": signature_prefix + signature
    }

    # Make the API request
    full_url = f"{base_url}?{query_string}"
    response = requests.get(full_url, headers=headers)

    # Check if the request is successful
    if response.status_code != 200:
        raise Exception(f"Request failed: {response.status_code} {response.text}")

    # Return the JSON response
    return response.json()






# export_json_to_file(user_inventory(), "inventory.json")
# # response = get_user_offers(
# #     game_id="a8db",
# #     sort_type="UserOffersSortTypeDateNewestFirst",
# #     limit=1000
# # )
# print(get_user_offers())

# last_sales = get_last_sales(title="AK-47 | Redline (Field-Tested)")
# print(last_sales)
# export_json_to_file(last_sales, "last_sales.json")

# export_json_to_file(response, "user_offers.json")
# # export_json_to_file(offers_by_title("M4A4 | Turbine (Minimal Wear)"), "offers_by_title.json")

# export_list = []
# for offer in offers_by_title("AWP | Phobos (Minimal Wear)"):
#     offer = listing_convert_universal_dm(offer)
#     export_list.append(offer)

# export_json_to_file(export_list, "offers_by_title.json")

# export_json_to_file(get_aggregated_prices(["AWP | Phobos (Minimal Wear)"]))

# export_json_to_file(get_last_sales("Dual Berettas | Hydro Strike (Factory New)"), "last_sales_sample.json")