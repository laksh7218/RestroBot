"""
Restaurant Menu Processing Module
"""

import pandas as pd
import re
import json
from pathlib import Path
import csv
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
GEMINI_TOKEN = os.getenv("gemini_token")

def clean_text(text):
    if pd.isna(text):
        return "unknown"
    text = str(text).lower()
    text = re.sub(r"[^a-zA-Z0-9\s.,-]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def normalize_price(price):
    if pd.isna(price):
        return "0"
    price = re.sub(r"[^0-9.]", "", str(price))
    return price if price else "0"

def apply_synonyms(text):
    synonyms = {
        r"\bnon-veg\b": "non vegetarian",
        r"\bnonveg\b": "non vegetarian",
        r"\bveg\b": "vegetarian",
        r"\bpizza'?s\b": "pizzas",
        r"\bcombo\b": "meal",
        r"\bspicy\b": "hot"
    }
    for pattern, replacement in synonyms.items():
        text = re.sub(pattern, replacement, text)
    return text

def load_and_clean_menus_from_json(folder_path="menu"):
    documents = []
    for file in Path(folder_path).glob("*.json"):
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)

        restaurant_name = clean_text(data.get("restaurant", {}).get("name", ""))
        location = clean_text(data.get("restaurant", {}).get("location", ""))
        contact = clean_text(data.get("restaurant", {}).get("contact", ""))

        genai.configure(api_key=GEMINI_TOKEN)
        model = genai.GenerativeModel("gemma-3-27b-it")

        prompt = f"""Please provide only the information asked in the given prompt and in the format specified: Provide brief and main information about {restaurant_name}, the restaurant, in Roorkee Locality, and give its operational hours and the name of the cuisines it serves.
format of the response should be:
Main Information: ...
Cuisines: ...
Operational Hours: 8 AM to 11 PM"""

        response = model.generate_content(prompt).text

        main_information = "unknown"
        cuisines = "various cuisines"
        operational_hours = "regular hours"

        for line in response.split("\n"):
            line = line.strip()
            if line.lower().startswith("main information:"):
                main_information = line.split(":", 1)[1].strip()
            elif line.lower().startswith("cuisines:"):
                cuisines = line.split(":", 1)[1].strip()
            elif line.lower().startswith("operational hours:"):
                operational_hours = line.split(":", 1)[1].strip()

        resto_info = f"""{restaurant_name} is at {location}.
{main_information}
their contact number is {contact}.
{restaurant_name} serves {cuisines} and is open from {operational_hours}.
"""
        documents.append(resto_info)

        for category_block in data.get("menu", []):
            category_name = clean_text(category_block.get("category", ""))
            for item in category_block.get("items", []):
                item_name = clean_text(item.get("name", ""))
                description = apply_synonyms(clean_text(item.get("description", "")))
                price = normalize_price(item.get("price", ""))
                veg = clean_text(item.get("veg_nonveg", ""))
                spice = clean_text(item.get("spice_level", ""))

                full_text = f"""{restaurant_name} offers {item_name} in the category '{category_name}'.
{item_name} is {description} for price {price} and type: {veg} with spice level: {spice}."""

                documents.append(full_text)

    with open("database.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Item"])
        for doc in documents:
            writer.writerow([doc])

    return documents
