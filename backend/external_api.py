import requests

def fetch_product_by_barcode(barcode: str) -> dict:
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == 1:
                product = data.get("product", {})
                return {
                    "product_name": product.get("product_name", "Unknown Product"),
                    "image_url": product.get("image_url", ""),
                    "ingredients_text": product.get("ingredients_text_en") or product.get("ingredients_text", ""),
                    "nutriments": product.get("nutriments", {})
                }
    except Exception as e:
        print(f"Error fetching barcode data: {e}")
    return {}
