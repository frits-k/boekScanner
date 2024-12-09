import base64
import requests
import os
from dotenv import load_dotenv

def print_offers(offers):
    print("Competing Offers:")
    print("-" * 80)
    for offer in offers:
        print(f"Offer ID          : {offer.get('offerId')}")
        print(f"Retailer ID       : {offer.get('retailerId')}")
        print(f"Country Code      : {offer.get('countryCode')}")
        print(f"Best Offer        : {'Yes' if offer.get('bestOffer') else 'No'}")
        print(f"Price             : {offer.get('price')} EUR")
        print(f"Fulfilment Method : {offer.get('fulfilmentMethod')}")
        print(f"Condition         : {offer.get('condition')}")
        print(f"Ultimate Order Time: {offer.get('ultimateOrderTime', 'N/A')}")
        print(f"Delivery Date     : {offer.get('minDeliveryDate')} to {offer.get('maxDeliveryDate')}")
        print("-" * 80)

# Load environment variables from .env file
load_dotenv()

# Load client credentials from environment variables
client_id = os.getenv("BOL_CLIENT_ID")
client_secret = os.getenv("BOL_CLIENT_SECRET")

if not client_id or not client_secret:
    raise ValueError(
        "Missing client_id or client_secret. Please set BOL_CLIENT_ID and BOL_CLIENT_SECRET in the .env file."
    )

# Encode credentials in Base64
credentials = f"{client_id}:{client_secret}"
encoded_credentials = base64.b64encode(credentials.encode()).decode()

# Request access token
token_url = "https://login.bol.com/token"
headers = {
    "Authorization": f"Basic {encoded_credentials}",
    "Accept": "application/vnd.retailer.v10+json",
    "Content-Type": "application/x-www-form-urlencoded",
}

# Add the required grant type as data
data = {"grant_type": "client_credentials"}

response = requests.post(token_url, headers=headers, data=data)

# Handle response
if response.status_code == 200:
    access_token = response.json().get("access_token")
    print("Access Token:", access_token)
else:
    print("Failed to retrieve access token")
    print("Status Code:", response.status_code)
    print("Response:", response.text)
    access_token = None

if access_token:
    # Define the API endpoint for retrieving competing offers
    ean = "9789402710236"  # Product EAN
    url = f"https://api.bol.com/retailer/products/{ean}/offers"

    # Headers for the API request
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.retailer.v10+json",
    }

    # Send the GET request to the competing offers API endpoint
    response = requests.get(url, headers=headers)

    # Check the response
    if response.status_code == 200:
        competing_offers = response.json()
        print("competing_offers:", competing_offers)
        print("Competing Offers Retrieved Successfully:")
        print_offers(competing_offers['offers'])
    else:
        print("Failed to retrieve competing offers.")
        print(f"Status Code: {response.status_code}")
        print("Response:", response.text)