"""
Setup script: Populate Master Registry and Log sheets with headers.
Run: python setup_sheets.py
"""

import json
import os
import sys
from google.oauth2 import service_account
from googleapiclient.discovery import build

def setup_sheets():
    """Populate Master Registry and Log sheets."""
    
    # Load credentials
    creds_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "")
    if not creds_path:
        print("❌ GOOGLE_SERVICE_ACCOUNT_JSON not set")
        return False
    
    try:
        with open(creds_path, 'r') as f:
            creds_dict = json.load(f)
        
        creds = service_account.Credentials.from_service_account_info(
            creds_dict,
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        service = build("sheets", "v4", credentials=creds)
    except Exception as e:
        print(f"❌ Failed to load credentials: {e}")
        return False
    
    MASTER_REGISTRY_ID = os.getenv("MASTER_REGISTRY_SHEET_ID", "")
    LOG_SHEET_ID = os.getenv("MORNING_INTELLIGENCE_LOG_SHEET_ID", "")
    
    if not MASTER_REGISTRY_ID or not LOG_SHEET_ID:
        print("❌ Missing sheet IDs in .env")
        return False
    
    # Master Registry Data
    master_registry_data = [
        ["Client_Name", "Client_Code", "ClickUp_List_ID", "Google_Sheet_ID", "Account_Manager", "Status", "Efficiency_Baseline"],
        ["Healthy Chuchos", "HC", "901713039974", "1LbL48DlaUfoo6-dJ2EK51CKFaTSsi-f2mqhbikEs3CI", "Pedro", "Active", 85],
        ["GreenRay", "GR", "901713039998", "1hR8uq8wJnT3r-v0eXv_3QWKVM7cmTVhf-a4lHIN7wXA", "Gibran", "Active", 85],
        ["LO Fitness", "LF", "901713039951", "16B46LJdPcbNYkgy6IXq9GSfL-hvOF73M-5x30nzvm2Y", "Pedro", "Active", 85],
        ["MetaGreen", "MG", "901713040022", "1AAX5oaHstMe-mqVQQdeAj1RI29251jWhnZscWpiUFTo", "Gibran", "Active", 85],
        ["Ferreteria Duarte", "F24", "901713519277", "1MWZ7_VVoCjuS0aJSWdkdOiilgU8pHtO-6-VwHXdRHwA", "Pedro", "Active", 85]
    ]
    
    # Log Sheet Headers
    log_sheet_data = [
        ["Date", "Duration (s)", "Status", "Clients Pulled", "Red Count", "Yellow Count", "Errors", "API Latency"]
    ]
    
    # Populate Master Registry
    try:
        service.spreadsheets().values().update(
            spreadsheetId=MASTER_REGISTRY_ID,
            range="Registry!A1:G100",
            valueInputOption="USER_ENTERED",
            body={"values": master_registry_data}
        ).execute()
        print("✅ Master Registry Sheet populated with 5 clients")
    except Exception as e:
        print(f"❌ Error populating Master Registry: {e}")
        return False
    
    # Populate Log Sheet
    try:
        service.spreadsheets().values().update(
            spreadsheetId=LOG_SHEET_ID,
            range="LOG!A1:H1",
            valueInputOption="USER_ENTERED",
            body={"values": log_sheet_data}
        ).execute()
        print("✅ Log Sheet headers created")
    except Exception as e:
        print(f"❌ Error populating Log Sheet: {e}")
        return False
    
    print("\n✅ All sheets populated successfully!")
    return True

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    success = setup_sheets()
    sys.exit(0 if success else 1)
