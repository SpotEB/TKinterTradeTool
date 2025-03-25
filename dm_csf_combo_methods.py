from csf_methods import get_inventory as user_inventory_csf, item_convert_universal_csf
from dm_main import user_inventory as user_inventory_dm
from dm_methods import item_convert_universal_dm
import json


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