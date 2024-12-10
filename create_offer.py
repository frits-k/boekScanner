import base64
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load client credentials from environment variables
client_id = os.getenv("BOL_CLIENT_ID")
client_secret = os.getenv("BOL_CLIENT_SECRET")

if not client_id or not client_secret:
    raise ValueError(
        "Missing client_id or client_secret. Please set BOL_CLIENT_ID and BOL_CLIENT_SECRET environment variables.")

# Encode credentials in Base64
credentials = f"{client_id}:{client_secret}"
encoded_credentials = base64.b64encode(credentials.encode()).decode()

# Request access token
token_url = "https://login.bol.com/token"
headers = {
    "Authorization": f"Basic {encoded_credentials}",
    "Accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded"  # Ensure the Content-Type is set for form submission
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
  "ean" : "9789056701680",
  "economicOperatorId" : "90bfddc5-a6d0-4986-9253-407b3a6850ca",
  "condition" : {
    "name" : "NEW",
    "category" : "NEW"
  },
  "reference" : "RefCode",
  "onHoldByRetailer" : True,
  "unknownProductTitle" : "Title",
  "pricing" : {
    "bundlePrices" : [ {
      "quantity" : 1,
      "unitPrice" : 55.99}]
  },
  "stock" : {
    "amount" : 1,
    "managedByRetailer" : False
  },
  "fulfilment" : {
    "method" : "FBR",
    "deliveryCode" : "VVB"
  }
}

    # Headers for the API request
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/vnd.retailer.v10+json",  # Use the specific media type expected by bol.com
        "Accept": "application/vnd.retailer.v10+json"  # Match the API version
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
