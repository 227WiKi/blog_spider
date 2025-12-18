import os
import sys
from dotenv import load_dotenv
from onedrive_client import OneDriveClient

def run_test():
    load_dotenv()
    
    print("=== OneDrive Test ===")
    
    client = OneDriveClient()
    
    print("1. Connecting to Azure...", end=" ")
    if client.connect():
        print("[SUCCESS] Connected!")
    else:
        print("[ERROR] Connection failed! Please check .env configuration.")
        sys.exit(1) # Exit immediately on connection failure

    # Create test file
    test_filename = "test_module_upload.txt"
    with open(test_filename, "w", encoding="utf-8") as f:
        f.write("Test content.")
    
    test_subfolder = "Test_Connection"
    
    print(f"2. Uploading file to: {client.root_folder_path}/{test_subfolder} ...")
    
    # Receive return value to check success/failure
    success = client.upload_file(test_filename, test_subfolder)
    
    # Clean up local file (regardless of success/failure)
    if os.path.exists(test_filename):
        os.remove(test_filename)

    if success:
        print("\n[SUCCESS] Upload complete!")
        print(f"   Please check OneDrive path: {client.root_folder_path}/{test_subfolder}/{test_filename}")
    else:
        print("\n[ERROR] Upload failed! Program terminated.")
        print("   Please check Azure permissions (Admin Consent) or Tenant ID settings based on the [ERROR] above.")
        sys.exit(1) # Exit on upload failure

if __name__ == "__main__":
    run_test()