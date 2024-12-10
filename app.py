import base64
import streamlit as st
from streamlit_qrcode_scanner import qrcode_scanner
import pandas as pd
import requests

def print_offers(offers):
  data = []
  for offer in offers:
    data.append({
      "Offer ID": offer.get('offerId'),
      "Retailer ID": offer.get('retailerId'),
      "Country Code": offer.get('countryCode'),
      "Best Offer": 'Yes' if offer.get('bestOffer') else 'No',
      "Price (EUR)": offer.get('price'),
      "Fulfilment Method": offer.get('fulfilmentMethod'),
      "Condition": offer.get('condition'),
      "Ultimate Order Time": offer.get('ultimateOrderTime', 'N/A'),
      "Delivery Date": f"{offer.get('minDeliveryDate')} to {offer.get('maxDeliveryDate')}"
    })

  df = pd.DataFrame(data)
  return df

def retrieve_competing_offers(client_id, client_secret, ean_code):
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
      url = f"https://api.bol.com/retailer/products/{ean_code}/offers"

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
        print("Competing Offers Retrieved Successfully:")
        return print_offers(competing_offers['offers'])
      else:
        print("Failed to retrieve competing offers.")
        print(f"Status Code: {response.status_code}")
        print("Response:", response.text)

def create_offer(client_id, client_secret, ean_code):
  if not client_id or not client_secret:
    raise ValueError(
      "Missing client_id or client_secret. Please set BOL_CLIENT_ID and BOL_CLIENT_SECRET environment variables."
    )

  # Encode credentials in Base64
  credentials = f"{client_id}:{client_secret}"
  encoded_credentials = base64.b64encode(credentials.encode()).decode()

  # Request access token
  token_url = "https://login.bol.com/token"
  headers = {
    "Authorization": f"Basic {encoded_credentials}",
    "Accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded"
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
    # Define the API endpoint for the demo environment
    url = "https://api.bol.com/retailer-demo/offers"
    url = "https://api.bol.com/retailer/offers"

    # Payload for the API request
    payload = {
      "ean": ean_code,
      "economicOperatorId": "90bfddc5-a6d0-4986-9253-407b3a6850ca",
      "condition": {
        "name": "NEW",
        "category": "NEW"
      },
      "reference": "RefCode",
      "onHoldByRetailer": True,
      "unknownProductTitle": "Title",
      "pricing": {
        "bundlePrices": [{
          "quantity": 1,
          "unitPrice": 55.99
        }]
      },
      "stock": {
        "amount": 1,
        "managedByRetailer": False
      },
      "fulfilment": {
        "method": "FBR",
        "deliveryCode": "VVB"
      }
    }

    # Headers for the API request
    headers = {
      "Authorization": f"Bearer {access_token}",
      "Content-Type": "application/vnd.retailer.v10+json",
      "Accept": "application/vnd.retailer.v10+json"
    }

    # Send the POST request to the demo API endpoint
    response = requests.post(url, json=payload, headers=headers)

    # Check the response
    if response.status_code in (201, 202):  # HTTP 201 Created
      print("Offer successfully created!")
      print("Response:", response.json())
    else:
      print("Failed to create offer.")
      print(f"Status Code: {response.status_code}")
      print("Response:", response.text)



# Load bol.com banner image from the internet
bol_image = "https://media.licdn.com/dms/image/v2/C561BAQHOc6cmr7fNnw/company-background_10000/company-background_10000/0/1585427446497/bol_com_cover?e=1734451200&v=beta&t=M0KcxhqwUaBArc53ejJCfsfJaPU0OS9T_dubOQu47MY"
st.image(bol_image)

client_id = st.text_input("BOL CLIENT ID")
client_secret = st.text_input("BOL SECRET", type="password")
action = st.selectbox("Wat wil je doen?", ["Boek plaatsen", "Prijzen ophalen"])

show_scanner = st.checkbox("ACTIVEER SCANNER")

if show_scanner:
  qr_code = qrcode_scanner(key='qrcode_scanner')
  if qr_code:
    if action == "Prijzen ophalen":
      offers = retrieve_competing_offers(client_id, client_secret, qr_code)
      if offers is not None:
        st.write("Andere offerten:")
        st.dataframe(offers)
    else:
      create_offer(client_id, client_secret, qr_code)
