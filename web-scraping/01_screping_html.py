import requests

url = "https://www.magicbricks.com/property-for-sale/residential-real-estate?bedroom=1,2,3,4,5,%3E5&proptype=Multistorey-Apartment,Builder-Floor-Apartment,Penthouse,Studio-Apartment,Residential-House,Villa&cityName=Bangalore"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

try:
    r = requests.get(url, headers=headers, timeout=20)
    r.raise_for_status()  # Raises an HTTPError for bad responses
    
    with open("file.html", "w", encoding="utf-8") as f:
        f.write(r.text)
    print("File saved successfully!")
    
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")