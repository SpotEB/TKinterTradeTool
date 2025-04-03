import customtkinter as ctk
import tkinter as tk
import json
from PIL import Image
import requests
from io import BytesIO
from dm_main import get_last_sales as last_sales_dm, offers_by_title as offers_by_title_dm, listing_convert_universal_dm, get_customized_fees as get_reduced_fees_dm
from dm_methods import sales_convert_universal_dm
from csf_methods import last_sales_csf, sales_convert_universal_csf, search_skin, search_commodity, listing_convert_universal_csf, csf_list_item
from datetime import datetime, timezone
from dm_csf_combo_methods import filtered_inventory, filtered_listings



def offers_sorted(offers):
    offers.sort(key=lambda x: x["price"])
    return offers

def reduced_fees_fetch():
    return

def reduced_fees_load():
    with open("TKinterTradeTool/db/reduced_fees.json", "r") as file:
        return json.load(file)

inventory = filtered_inventory()
inventory = sorted(inventory, key=lambda x: x["market_hash_name"])

user_listings = filtered_listings()

empty_img = ctk.CTkImage(light_image=Image.new("RGBA", (1, 1)), size=(1, 1))


ctk.set_appearance_mode("dark")  # Modes: "system" (default), "dark", "light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue"

app = ctk.CTk()  # Create the main window
app.geometry("1000x1080")  # Set size
app.title("Trade Tool v1.0")  # Set title
app.iconbitmap("TKinterTradeTool/tradetool.ico")  # Set icon

tabview = ctk.CTkTabview(app, width=1000, height=1040)
tabview.pack(padx=5, pady=5)

tabview.add("Sell")  # add tab at the end
tabview.add("Buy")  # add tab at the end
tabview.add("Listings")
tabview.set("Sell")  # set currently visible tab

def search_items_sell(event=None):
    if search_entry_sell.get() == "":
        item_gen_button(inventory)
        return

    search_term = search_entry_sell.get().lower()
    filtered_inventory = [item for item in inventory if search_term in item["market_hash_name"].lower()]
    clear_tab(scroll_frame_sell)
    item_gen_button(filtered_inventory)
    


# Search Entry
search_entry_sell = ctk.CTkEntry(tabview.tab("Sell"), width=400, placeholder_text="Search for an item...")
search_entry_sell.grid(row=0, column=0, padx=(10, 0), pady=10, sticky="ew")

search_entry_listings = ctk.CTkEntry(tabview.tab("Listings"), width=400, placeholder_text="Search for an item...")
search_entry_listings.grid(row=0, column=0, padx=(10, 0), pady=10, sticky="ew")

# Search Button
search_button_sell = ctk.CTkButton(tabview.tab("Sell"), text="Search", width=100, command=search_items_sell)
search_button_sell.grid(row=0, column=1, padx=(0, 10), pady=10)
search_entry_sell.bind("<Return>", search_items_sell)  # Bind the Enter key to the search_items function

search_button_listings = ctk.CTkButton(tabview.tab("Listings"), text="Search", width=100, command=search_items_sell)
search_button_listings.grid(row=0, column=1, padx=(0, 10), pady=10)
search_entry_listings.bind("<Return>", search_items_sell)  # Bind the Enter key to the search_items function

# Configure grid to allow entry to expand
tabview.tab("Sell").grid_columnconfigure(0, weight=1)
tabview.tab("Listings").grid_columnconfigure(0, weight=1)



scroll_frame_sell = ctk.CTkScrollableFrame(tabview.tab("Sell"), width=950, height=900)
scroll_frame_sell.grid(row=2, column=0, padx=20, pady=20)


def clear_tab(tab):
    for widget in tab.winfo_children():
        widget.destroy()



def list_item_confirm(item, price, market):
    if price == "":
        return
    if market == "CSfloat":
        confirmation_window = ctk.CTkToplevel(app)
        confirmation_window.title("Confirmation")
        confirmation_label = ctk.CTkLabel(confirmation_window, text=f"Are you sure you want to list {item['market_hash_name']} for ${price} on CSFloat?", font=("Arial", 15))
        confirmation_label.pack(padx=10, pady=10)
        print(item["asset_id_csf"])
        print(price)
        confirm_button = ctk.CTkButton(confirmation_window, text="Confirm", command=lambda: (
            csf_list_item(item["asset_id_csf"], int(float(price) * 100)),
            confirmation_window.destroy(),
            inventory.remove(item),
            item_gen_button(inventory)
            ))
        confirm_button.pack(padx=10, pady=10)


wear_conditions = [
    [0.00, 0.07],
    [0.07, 0.15],
    [0.15, 0.38],
    [0.38, 0.45],
    [0.45, 0.99]
]

def item_call(item):
    item_window.deiconify()
    item_window.lift()
    
    
    item_title.configure(text=f"{item['market_hash_name']}")
    item_float.configure(text=f"Item Float: {item['float_value']}")
    item_list_price_button.configure(command=lambda: list_item_confirm(item, item_list_price_input.get(), item_list_market_choice.get()))

    item_stickers = "Stickers: "
    if item["stickers"].__len__() > 0:
        for dict in item["stickers"]:
            for key, value in dict.items():
                item_stickers += f"\n{key}: {value}"
            item_stickers += "\n"
    else:
        item_stickers = "Stickers: None"
    
    item_stickers_label.configure(text=f"{item_stickers}")

    item_keychain = item["keychain"]
    if item_keychain == "":
        item_keychain = "Keychain: None"
    else:
        item_keychain = f"Keychain: {item_keychain}"
    item_keychain_label.configure(text=f"{item_keychain}")


    try: # Try to load the image
        image = requests.get(item["item_image"]).content
        loaded_image = Image.open(BytesIO(image)).resize((256, 192))
        item_image_label.configure(image=ctk.CTkImage(light_image=loaded_image, dark_image=loaded_image, size=(256, 192)))
    except Exception as e: # If it fails, load a placeholder image
        print(f"Failed to load image: {e}")
        placeholder_image = Image.open("TKinterTradeTool/db/placeholder_icon.webp").resize((256, 192))
        item_image_label.configure(image=ctk.CTkImage(light_image=placeholder_image, size=(256, 192)))

    clear_tab(item_last_sales_tabview.tab("CSfloat"))

    for sale in last_sales_csf(item["market_hash_name"]):
        sale = sales_convert_universal_csf(sale)   
        sale_label = ctk.CTkLabel(item_last_sales_tabview.tab("CSfloat"), text=f"{sale['price']} | {str(sale['float_value'])[:6]} | {datetime.fromtimestamp(int(sale["date"]), tz=timezone.utc).strftime("%d/%m")}", bg_color="#383737")
        sale_label.pack(padx=5, pady=1, fill="x")


    clear_tab(item_current_listings_tabview.tab("CSfloat"))


    if item["paint_index"] == 0 and item["market_hash_name"].startswith("Charm"):
        pass
    
    elif item["paint_index"] == 0:
        for listing in search_commodity(item["def_index"], limit=20):
            if listing["type"] == "buy_now": 
                listing_label = ctk.CTkLabel(item_current_listings_tabview.tab("CSfloat"), text=f"{listing['price']/100}", bg_color="#383737")
                listing_label.pack(padx=5, pady=1, fill="x")

    else:
        item_max_float = None
        item_min_float = None
        for wear in wear_conditions:
            if item["float_value"] < wear[1]:
                item_max_float = wear[1]
                item_min_float = wear[0]
                break

        if item["is_stattrak"]:
            item_category = 2
        elif item["is_souvenir"]:
            item_category = 3
        else:
            item_category = 1

        for listing in search_skin(item["def_index"], item["paint_index"], min_float=item_min_float, max_float=item_max_float, category=item_category, limit=20):
            listing = listing_convert_universal_csf(listing)
            if listing["listing_type"] == "buy_now": 
                listing_label = ctk.CTkLabel(item_current_listings_tabview.tab("CSfloat"), text=f"{listing['price']} | {str(listing['float_value'])[:6]}", bg_color="#383737")
                listing_label.pack(padx=5, pady=1, fill="x")



    clear_tab(item_last_sales_tabview.tab("Dmarket"))

    for sale in last_sales_dm(item["market_hash_name"])[0:20]:
        sale = sales_convert_universal_dm(sale)
        sale_label = ctk.CTkLabel(item_last_sales_tabview.tab("Dmarket"), text=f"{sale['price']} | {str(sale['float_value'])[:6]} | {datetime.fromtimestamp(int(sale["date"]), tz=timezone.utc).strftime("%d/%m")}", bg_color="#383737")
        sale_label.pack(padx=5, pady=1, fill="x")


    clear_tab(item_current_listings_tabview.tab("Dmarket"))

    offers_universal = [listing_convert_universal_dm(offer) for offer in offers_by_title_dm(item["market_hash_name"], limit=100)]
    for offer in offers_sorted(offers_universal)[0:20]:
        listing_label = ctk.CTkLabel(item_current_listings_tabview.tab("Dmarket"), text=f"{offer['price']} | {str(offer['float_value'])[:6]}", bg_color="#383737")
        listing_label.pack(padx=5, pady=1, fill="x")


def item_gen_button(list):
    for widget in scroll_frame_sell.winfo_children():
        widget.destroy()
    for i, item in enumerate(list):
        item_text = f"{item['market_hash_name']} | {str(item['float_value'])[:6]} |"
        button = ctk.CTkButton(scroll_frame_sell, text=item_text, font=("Arial", 15),
                               compound="left", width=600, height=20,
                               anchor="w", fg_color="#1f6aa5", text_color="white",
                               corner_radius=0,
                               command=lambda item=item: item_call(item))  # Pass item directly
        button.grid(row=i + 1, column=0, padx=20, pady=0, sticky="w")


item_gen_button(inventory)



app.grid_columnconfigure(0, weight=1)  # Entry expands
app.grid_columnconfigure(1, weight=0)  # Button stays fixed
app.grid_rowconfigure(1, weight=1)  # Scrollable frame expands


item_window = ctk.CTkToplevel(app)
item_window.title("Item Info (Trade Tool v1.0)")
item_window.iconbitmap("TKinterTradeTool/tradetool.ico")
item_window.geometry("685x970")




item_name = "Item Name (Item Condition)"
item_float = "0.000000"
item_stickers = "Stickers: "





item_info_frame = ctk.CTkFrame(item_window, width=800, height=200)
item_info_frame.grid(row=0, column=0, padx=10, pady=10, sticky="w")

item_title = ctk.CTkLabel(item_info_frame, text=f"{item_name}", font=("Arial", 20))
item_title.grid(row=0, column=0, padx=20, pady=10, sticky="w")

item_float = ctk.CTkLabel(item_info_frame, text=f"Item Float: {item_float}", font=("Arial", 15))
item_float.grid(row=1, column=0, padx=20, pady=5, sticky="w")

item_stickers_label = ctk.CTkLabel(item_info_frame, text=f"{item_stickers}", font=("Arial", 15))
item_stickers_label.grid(row=2, column=0, padx=20, pady=5, sticky="w")

item_keychain_label = ctk.CTkLabel(item_info_frame, text="Keychain: None", font=("Arial", 15))
item_keychain_label.grid(row=3, column=0, padx=20, pady=5, sticky="w")

item_list_frame = ctk.CTkFrame(item_window, width=600, height=200)
item_list_frame.grid(row=2, column=0, padx=10, pady=10, sticky="w")

item_list_price_input = ctk.CTkEntry(item_list_frame, width=140, placeholder_text="Price (USD)")
item_list_price_input.grid(row=0, column=0, padx=10, pady=10, sticky="w")

item_list_price_button = ctk.CTkButton(item_list_frame, text="List Item", width=10,)
item_list_price_button.grid(row=0, column=1, padx=10, pady=10)

def select_list_market(value):
    pass

item_list_market_choice = ctk.CTkSegmentedButton(item_list_frame, values=["CSfloat", "Dmarket"], command=select_list_market)
item_list_market_choice.grid(row=1, column=0, padx=10, pady=10, sticky="w")

marketplace_info_frame = ctk.CTkFrame(item_window, width=900, height=400)   
marketplace_info_frame.grid(row=3, column=0, padx=10, pady=10, sticky="w")


item_last_sales_frame = ctk.CTkScrollableFrame(marketplace_info_frame, width=290, height=385)
item_last_sales_frame.grid(row=2, column=0, padx=10, pady=10, sticky="w")

item_last_sales_title = ctk.CTkLabel(item_last_sales_frame, text="Last Sales", font=("Arial", 15))
item_last_sales_title.pack(padx=5, pady=0, fill="x")

item_last_sales_tabview = ctk.CTkTabview(item_last_sales_frame, width=280, height=350)
item_last_sales_tabview.pack(padx=5, pady=0)

item_last_sales_tabview.add("CSfloat")  # add tab at the end
item_last_sales_tabview.add("Dmarket")  # add tab at the end
item_last_sales_tabview.set("CSfloat")  # set currently visible tab



item_current_listings_frame = ctk.CTkScrollableFrame(marketplace_info_frame, width=290, height=385)
item_current_listings_frame.grid(row=2, column=1, padx=10, pady=10, sticky="w")

item_current_listings_title = ctk.CTkLabel(item_current_listings_frame, text="Current Listings", font=("Arial", 15))
item_current_listings_title.pack(padx=5, pady=0, fill="x")

item_current_listings_tabview = ctk.CTkTabview(item_current_listings_frame, width=280, height=350)
item_current_listings_tabview.pack(padx=5, pady=0)

item_current_listings_tabview.add("CSfloat")  # add tab at the end
item_current_listings_tabview.add("Dmarket")  # add tab at the end
item_current_listings_tabview.set("CSfloat")  # set currently visible tab



item_image = ctk.CTkImage(light_image=Image.open("TKinterTradeTool/db/placeholder_icon.webp"), dark_image=Image.open("TKinterTradeTool/db/placeholder_icon.webp"), size=(256, 192))
item_image_label = ctk.CTkLabel(item_info_frame, image=item_image, text="")
item_image_label.grid(row=2, column=1, padx=10, pady=10, sticky="w")  # Added sticky="w"



app.mainloop()