import requests

# Define the API endpoint for the demo environment
url = "https://api.bol.com/retailer-demo/offers"

# Replace this with your actual demo access token
access_token = "YOUR_DEMO_ACCESS_TOKEN"

# Payload for the API request
payload = {
    "ean": "9789083168906",  # Replace with your book's ISBN
    "condition": "SECOND_HAND",
    "conditionCategory": "GOOD",  # Options: AS_NEW, GOOD, REASONABLE, MODERATE
    "conditionComment": "Some minor scratches, all pages intact.",
    "reference": "DEMO_BOOK12345",  # Optional reference for your own records
    "onHoldByRetailer": False,
    "unknownProductTitle": None,  # Optional: If product is unknown, provide a title
    "unknownProductSubtitle": None,  # Optional
    "quantity": 1,  # Quantity of the item
    "price": {
        "currency": "EUR",
        "value": 12.50  # Set your selling price
    },
    "deliveryCode": "1-2d",  # Expected delivery time, e.g., 1-2 days
    "fulfilment": {
        "method": "FBR"  # FBR: Fulfilled by Retailer; use "FBB" for Fulfillment by bol.com
    }
}

# Headers for the API request
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

# Send the POST request to the demo API endpoint
response = requests.post(url, json=payload, headers=headers)

# Check the response
if response.status_code == 201:  # HTTP 201 Created
    print("Offer successfully created in demo environment!")
    print("Response:", response.json())
else:
    print("Failed to create offer.")
    print(f"Status Code: {response.status_code}")
    print("Response:", response.text)
