# RestroBot
A powerful, AI-driven assistant specialized in restaurant information and menu queries. Leveraging advanced natural language processing capabilities, it provides users with accurate and concise responses about various restaurants, their menus, pricing, and locations.

# Directory Structure
```bash
Zomato-Gen-AI/
├── menu/
│   ├── baap_of_rolls_menu.json
│   ├── desi_tadka_menu.json
│   ├── dominos_menu.json
│   ├── foodbay_menu.json
│   ├── kfc_menu.json
│   ├── patiala_lassi_menu.json
│   ├── pizza_hut_menu.json
│   ├── prakash_hotel_menu.json
│   └── waffle_by_nature_menu.json
├── README.md
├── app.py
├── data_cleaning.py
├── data_scraper.py
├── database.csv
├── rag.py
├── requirements.txt
└── scraper_runner.py
```

# Setup
Config (.env)
```bash
hf_token = "YOUR-API-KEY"
gemini_token = "PUBLIC-API-KEY"
```
Environment
```bash
conda create -n myenv python=3.10
conda activate myenv
pip install -r requirements.txt
```

# System Architecture
```bash
             +----------------+             +--------------------+             
             | scraper_runner | --------->  |    scraper.py      |             
             +----------------+             +--------------------+             
                                                    |                          
                                                    v                          
                                        +------------------------+             
                                        |   JSON menu files in   |             
                                        |      /menu folder      |             
                                        +------------------------+             
                                                    |                          
                                                    v                          
                                        +------------------------+             
                                        |  data_cleaning.py      |             
                                        | - Cleaning & formatting|             
                                        | - Gemini restaurant info|            
                                        +------------------------+             
                                                    |                          
                                                    v                          
                                        +------------------------+             
                                        |   rag.py               |             
                                        | - Embeddings via SBERT |             
                                        | - FAISS Vector Store   |             
                                        | - Gemini/LLaMA model   |             
                                        +------------------------+             
                                                    |                          
                                                    v                          
                                        +------------------------+             
                                        |  Streamlit App (Local) |             
                                        | - Hosted in browser    |             
                                        | - User inputs/query UI |             
                                        +------------------------+
```

# Implementation Details & Design Decisions
### Module: `scraper_runner.py`
- Acts as the **driver script** to initiate scraping across multiple Zomato URLs.
- Maps restaurant names to their respective URLs and invokes `scrape_zomato()` from `scraper.py`.

### Module: `scraper.py`
Scrapes restaurant information and menu data from a Zomato restaurant page and saves it in structured JSON format.
- Uses **Selenium WebDriver** (headless Chrome) to render and interact with the dynamic content of Zomato pages.
- Clicks all "Read more" buttons to expand hidden descriptions.
- Parses restaurant name, location, contact, menu categories, and items using **BeautifulSoup**.
- Each menu item includes:
  - Name, Price, Description
  - Vegetarian/Non-Vegetarian type
  - Estimated spice level (based on keywords in description)
- Automatically saves the scraped data to a JSON file in the `/menu` folder.
