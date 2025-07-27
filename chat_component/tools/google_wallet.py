import base64
from typing import Dict, List
import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.auth.transport.requests import Request
from google.oauth2 import service_account
import google.auth
import requests
import json
import os
from cryptography.hazmat.primitives import serialization
import jwt
import datetime

# tool/google_wallet_tool.py
# Load credentials from environment or Secret Manager
import os

def get_credentials_from_secret_manager():
    """Get credentials from Google Secret Manager (for production)"""
    try:
        from google.cloud import secretmanager
        import json

        project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "gen-lang-client-0670800402")
        secret_name = "google-wallet-service-account"

        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"

        response = client.access_secret_version(request={"name": name})
        secret_value = response.payload.data.decode("UTF-8")

        service_account_info = json.loads(secret_value)
        return service_account.Credentials.from_service_account_info(
            service_account_info, scopes=SCOPES
        )
    except Exception as e:
        print(f"Failed to get credentials from Secret Manager: {e}")
        return None

# Get service account info from environment variables
GOOGLE_WALLET_SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_WALLET_SERVICE_ACCOUNT_JSON")
GOOGLE_WALLET_SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_WALLET_SERVICE_ACCOUNT_FILE")
GOOGLE_WALLET_ISSUER_ID = os.getenv("GOOGLE_WALLET_ISSUER_ID", "3388000000022966378")

# Set proper scopes
SCOPES = ["https://www.googleapis.com/auth/wallet_object.issuer"]

# Load credentials - try multiple methods (prioritize local development)
credentials = None

# Method 1: Development - try local file first (for local development)
default_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'wallet-integration-466509-e4057ed46eeb.json'))
if os.path.exists(default_path):
    credentials = service_account.Credentials.from_service_account_file(
        default_path, scopes=SCOPES
    )
    print("Using Google Wallet credentials from local file")

if not credentials and GOOGLE_WALLET_SERVICE_ACCOUNT_FILE and os.path.exists(GOOGLE_WALLET_SERVICE_ACCOUNT_FILE):
    # Method 2: Use file path from environment variable
    credentials = service_account.Credentials.from_service_account_file(
        GOOGLE_WALLET_SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    print("Using Google Wallet credentials from environment file path")

if not credentials and GOOGLE_WALLET_SERVICE_ACCOUNT_JSON:
    # Method 3: Use JSON string from environment variable
    import json
    service_account_info = json.loads(GOOGLE_WALLET_SERVICE_ACCOUNT_JSON)
    credentials = service_account.Credentials.from_service_account_info(
        service_account_info, scopes=SCOPES
    )
    print("Using Google Wallet credentials from environment JSON")

if not credentials:
    # Method 4: Try Secret Manager (for production)
    credentials = get_credentials_from_secret_manager()
    if credentials:
        print("Using Google Wallet credentials from Secret Manager")

if not credentials:
    print("WARNING: Google Wallet service account credentials not found. Google Wallet features will be disabled.")
    print("To enable Google Wallet:")
    print("1. Create secret: gcloud secrets create google-wallet-service-account --data-file=path/to/your/file.json")
    print("2. Or set GOOGLE_WALLET_SERVICE_ACCOUNT_JSON environment variable")
    print("3. Or set GOOGLE_WALLET_SERVICE_ACCOUNT_FILE environment variable")
    # Don't raise an error, just continue without credentials

# Initialize session and refresh credentials only if they exist
session = requests.Session()
if credentials:
    credentials.refresh(Request())

class WalletRequest(BaseModel):
    user_id: str
    receipt_summary: str
    transaction_amount: float

def create_save_url_with_jwt(object_id: str):
    if not credentials:
        print("WARNING: Cannot create save URL - Google Wallet credentials not available")
        return None

    claims = {
        'iss': credentials.service_account_email,
        'aud': 'google',
        'typ': 'savetowallet',
        'iat': int(datetime.datetime.now(datetime.timezone.utc).timestamp()),
        'payload': {
            'genericObjects': [{
                'id': object_id
            }]
        }
    }

    private_key = credentials._signer._key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    token = jwt.encode(claims, private_key, algorithm='RS256')
    return f'https://pay.google.com/gp/v/save/{token}'

from google.adk.tools import ToolContext

def create_google_wallet_pass(text_module_headers: List[str], text_module_bodies: List[str],
                              pass_type:str,pass_name:str,
                              short_description:str,
                              tool_context: ToolContext):
    """
    Creates a Google Wallet pass payload using the provided user data and text modules.

    Constructs the wallet object payload including title, header, hero image, dynamic text modules,
    barcode, and optional links. This payload can be sent to the Google Wallet API for issuance.

    Args:
        text_module_headers (List[str]): A list of str, with all headers for the receipt.
        text_module_bodies (List[str]): A list of str, with all body for the receipt.
        pass_type (str): The type/category of the receipt (e.g., "Grocery Receipt", "Travel Receipt").
        pass_name (str): The name of the pass to be given based on receipt uploaded with date (merchant name, store name, vendor name etc)
        short_description (str): Shortened description of the pass with all important details.
    Returns:
        dict: A fully structured payload conforming to the Google Wallet object specification.
    """
    print(tool_context)

    # Check if credentials are available
    if not credentials:
        print("WARNING: Google Wallet credentials not available. Cannot create wallet pass.")
        return {"error": "Google Wallet service not available", "Details": "Credentials not configured"}
    # image_bytes = base64.b64decode(image_base64)
    # output_file_path = "output_image.png"
    # try:
    #     with open(output_file_path, "wb") as f:
    #         f.write(image_bytes)
    #     print(f"Image successfully written to {output_file_path}")
    # except IOError as e:
    #     print(f"Error writing image to file: {e}")


    #TODO: use ToolContext to find the userID or username
    text_modules = [
        {"header": h, "body": b}
        for h, b in zip(text_module_headers, text_module_bodies)
    ]
    user_id = "1"
    print(f"------------\n{user_id}--------------")
    print(f"------------\n{text_modules}--------------")
    GENERIC_CLASS_ID = f"{GOOGLE_WALLET_ISSUER_ID}.receipt_class"  # Make sure this class exists in Google Wallet Console

    sanitized_user_id = user_id.replace('@', '_').replace('.', '_')
    generic_object_id = f"{GOOGLE_WALLET_ISSUER_ID}.{sanitized_user_id+str(uuid.uuid4())[:4]}"

    # Check if object already exists to avoid 404 or 409
    object_url = f"https://walletobjects.googleapis.com/walletobjects/v1/genericObject/{generic_object_id}"
    headers = {"Authorization": f"Bearer {credentials.token}"}

    existing_check = session.get(object_url, headers=headers)
    if existing_check.status_code != 200:
        object_payload = {
            "id": generic_object_id,
            "classId": GENERIC_CLASS_ID,
            "state": "ACTIVE",
            "cardTitle": {
                "defaultValue": {"language": "en-US", "value": pass_type}
            },
            "header": {
                "defaultValue": {"language": "en-US", "value": pass_name}
            },
            "heroImage": {
                "sourceUri": {
                    "uri": "https://img.icons8.com/ios-filled/500/wallet--v1.png",
                    "description": "Receipt Thumbnail"
                }
            },
            "textModulesData": text_modules,
            "barcode": {
                "type": "QR_CODE",
                "value": short_description,  # use total or last value
                "alternateText": "Detail"
            },
            "linksModuleData": {
                "uris": [
                    {"uri": "https://simple.com", "description": "View Details"}
                ]
            }
        }

        object_response = session.post(
                    "https://walletobjects.googleapis.com/walletobjects/v1/genericObject",
                    headers=headers,
                    json=object_payload
                )

    if object_response.status_code >= 400:
        raise HTTPException(status_code=object_response.status_code, detail=object_response.text)

    save_url = create_save_url_with_jwt(generic_object_id)
    tool_context.state['wallet_url'] = save_url
    print(f"**************\n{save_url}\n******")
    print(f"**************\n{text_modules}\n******")
    return {"URL_TO_SEND_TO_USER": save_url, "Details":text_modules}

 
def create_google_wallet_pass_working(req: WalletRequest):
    try:
        # Check if credentials are available
        if not credentials:
            raise HTTPException(status_code=503, detail="Google Wallet service not available - credentials not configured")

        GENERIC_CLASS_ID = f"{GOOGLE_WALLET_ISSUER_ID}.receipt_class"  # Make sure this class exists in Google Wallet Console

        sanitized_user_id = req.user_id.replace('@', '_').replace('.', '_')
        generic_object_id = f"{GOOGLE_WALLET_ISSUER_ID}.{sanitized_user_id}"

        # Check if object already exists to avoid 404 or 409
        object_url = f"https://walletobjects.googleapis.com/walletobjects/v1/genericObject/{generic_object_id}"
        headers = {"Authorization": f"Bearer {credentials.token}"}

        existing_check = session.get(object_url, headers=headers)
        if existing_check.status_code != 200:
            object_payload = {
                "id": generic_object_id,
                "classId": GENERIC_CLASS_ID,
                "state": "ACTIVE",
                "cardTitle": {
                    "defaultValue": {
                        "language": "en-US",
                        "value": "Receipt Summary"
                    }
                },
                "header": {
                    "defaultValue": {
                        "language": "en-US",
                        "value": "Your Purchase Details"
                    }
                },
                "heroImage": {
                    "sourceUri": {
                        "uri": "https://img.icons8.com/ios-filled/500/wallet--v1.png",
                        "description": "Receipt Thumbnail"
                    }
                },
                "textModulesData": [
                    {
                        "header": "Receipt Summary",
                        "body": req.receipt_summary
                    },
                    {
                        "header": "Total Amount",
                        "body": f"INR {req.transaction_amount:.2f}"
                    }
                ],
                "barcode": {
                    "type": "QR_CODE",
                    "value": f"{req.user_id}_{req.transaction_amount}",
                    "alternateText": "Scan at checkout"
                },
                "linksModuleData": {
                    "uris": [
                        {
                            "uri": "https://yourapp.com",
                            "description": "View Details"
                        }
                    ]
                }
            }

            object_response = session.post(
                "https://walletobjects.googleapis.com/walletobjects/v1/genericObject",
                headers=headers,
                json=object_payload
            )

            if object_response.status_code >= 400:
                raise HTTPException(status_code=object_response.status_code, detail=object_response.text)

        save_url = create_save_url_with_jwt(generic_object_id)
        return {"save_url": save_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))