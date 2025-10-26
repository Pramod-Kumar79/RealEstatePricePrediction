from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time, re, json
from datetime import datetime

# ===============================
# 1️⃣ Chrome Setup
# ===============================
options = Options()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# ===============================
# 2️⃣ Target URL
# ===============================
url = ("https://www.magicbricks.com/property-for-sale/residential-real-estate?bedroom=1,2,3,4,5,%3E5&proptype=Multistorey-Apartment,Builder-Floor-Apartment,Penthouse,Studio-Apartment,Residential-House,Villa&cityName=Bangalore")

driver.get(url)
time.sleep(6)

# ===============================
# 3️⃣ Controlled Scroll (works)
# ===============================
scroll_pause = 4
max_scrolls = 150 # ✅ You can change this limit

print(f"⚙️ Scrolling {max_scrolls} times to load more listings...")
for i in range(max_scrolls):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(scroll_pause)
    print(f"Scrolled {i+1}/{max_scrolls}")

print("✅ Finished scrolling.")
html = driver.page_source
driver.quit()

# ===============================
# 4️⃣ Parse Listings
# ===============================
print("🔍 Parsing property cards...")
soup = BeautifulSoup(html, "html.parser")
cards = soup.find_all("div", class_=re.compile(r"mb-srp__card"))
print(f"Found {len(cards)} property cards!")

data = []
for card in cards:
    try:
        # Title
        title_tag = card.find("h2") or card.find("h3")
        title = title_tag.get_text(strip=True) if title_tag else None

        # Price & per sqft
        price_tag = card.find("div", class_=re.compile(r"price"))
        price_text = price_tag.get_text(strip=True) if price_tag else ""
        total_price = re.search(r'₹[\d,.\s]+(?:Cr|Crore|Lakh|Lac)?', price_text)
        price_val = total_price.group(0) if total_price else None
        per_sqft = re.search(r'₹[\d,.\s]+ per sqft', price_text)
        price_per_sqft = per_sqft.group(0) if per_sqft else None

        # Locality
        loc_tag = card.find("div", class_=re.compile(r"location"))
        locality = loc_tag.get_text(strip=True) if loc_tag else None

        # Society name
        society_tag = card.find(["a", "span"], class_="mb-srp__card__society--name")
        society_name = society_tag.get_text(strip=True) if society_tag else None

        # Area, BHK, Bathroom
        details_text = card.get_text(" | ", strip=True)
        area = re.search(r'\d+[.,]?\d*\s*(sqft|sq\.ft)', details_text, re.I)
        bhk = re.search(r'\b\d+\s*BHK\b', details_text, re.I)
        bathroom = re.search(r'Bathroom\s*\|\s*(\d+)', details_text)

        # Furnishing
        furnishing = re.search(r'Furnish(?:ing|ed)\s*\|\s*([\w\s]+)', details_text)
        furnishing_status = furnishing.group(1).strip() if furnishing else None

        # ✅ Robust Floor & Transaction extraction
        floor = transaction = None
        summary_blocks = card.find_all("div", class_=re.compile("mb-srp__card__summary"))

        for block in summary_blocks:
            label = block.find(["div", "span"], class_=re.compile("(label|name)"))
            value = block.find(["div", "span"], class_=re.compile("(value|info)"))
            if label and value:
                label_text = label.get_text(strip=True).lower()
                value_text = value.get_text(strip=True)
                if "floor" in label_text:
                    floor = value_text
                elif "transaction" in label_text:
                    transaction = value_text

        # Property Type
        property_type = re.search(r'Apartment|Villa|House|Plot|Penthouse|Studio', details_text, re.I)

        # Property ID
        property_id = None
        card_html = str(card)
        pid = re.search(r'propertyDetails/[^"\s]*?[?&]id=([A-Za-z0-9]+)', card_html)
        if pid:
            property_id = pid.group(1)

        # Geo from structured data blob
        latitude = longitude = None
        ld_script = card.find("script", type="application/ld+json")
        if ld_script:
            script_content = ld_script.string or ld_script.get_text(strip=True)
            if script_content:
                try:
                    ld_payload = json.loads(script_content)
                    payloads = ld_payload if isinstance(ld_payload, list) else [ld_payload]
                    for item in payloads:
                        if not isinstance(item, dict):
                            continue
                        geo = item.get("geo") or {}
                        latitude = latitude or geo.get("latitude")
                        longitude = longitude or geo.get("longitude")
                        if not property_id:
                            url_source = item.get("url") or item.get("@id")
                            if url_source:
                                match = re.search(r'id=([^"&]+)', url_source)
                                if match:
                                    property_id = match.group(1)
                        if latitude and longitude and property_id:
                            break
                except json.JSONDecodeError:
                    pass

        # ✅ Append Data
        data.append({
            "property_id": property_id,
            "title": title,
            "price": price_val,
            "price_per_sqft": price_per_sqft,
            "bhk_count": bhk.group(0) if bhk else None,
            "super_area": area.group(0) if area else None,
            "locality": locality,
            "society_name": society_name,
            "floor": floor,
            "transaction": transaction,
            "furnishing_status": furnishing_status,
            "bathroom_count": bathroom.group(1) if bathroom else None,
            "property_type": property_type.group(0) if property_type else None,
            "latitude": latitude,
            "longitude": longitude,
            "city": "Bangalore",
            "scraped_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    except Exception as e:
        print("Error parsing card:", e)

# ===============================
# 5️⃣ Save to CSV
# ===============================
df = pd.DataFrame(data)
output = f"magicbricks_bangalore_clean_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
df.to_csv(output, index=False, encoding="utf-8")
print(f"\n✅ Successfully scraped {len(df)} properties & saved to {output}")
