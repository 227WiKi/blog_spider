import os
import requests
from urllib.parse import urlparse
from tqdm import tqdm

class OneDriveClient:
    def __init__(self):
        self.site_url = os.getenv("SHAREPOINT_SITE_URL")
        self.client_id = os.getenv("AZURE_CLIENT_ID")
        self.client_secret = os.getenv("AZURE_CLIENT_SECRET")
        self.tenant_id = os.getenv("AZURE_TENANT_ID")
        self.root_folder_path = "227wiki/Backup/Blog"
        
        self.access_token = None
        self.drive_id = None
        self.headers = None

    def _get_token(self):
        """Directly retrieve Graph API token."""
        token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': 'https://graph.microsoft.com/.default'
        }
        try:
            r = requests.post(token_url, data=data)
            r.raise_for_status()
            self.access_token = r.json().get('access_token')
            self.headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            return True
        except Exception as e:
            print(f"[ERROR] Get Token Failed: {e}")
            return False

    def _get_drive_id(self):
        """Resolve user's Drive ID via SharePoint URL."""
        if not self.access_token: return False
        
        try:
            # 1. Parse URL
            parsed = urlparse(self.site_url)
            hostname = parsed.netloc
            site_path = parsed.path # e.g., /personal/user_...
            
            # 2. Call Graph API to get Site info
            # Format: GET /sites/{hostname}:{server-relative-path}
            req_url = f"https://graph.microsoft.com/v1.0/sites/{hostname}:{site_path}"
            r = requests.get(req_url, headers=self.headers)
            r.raise_for_status()
            site_id = r.json().get('id')
            
            # 3. Get default Drive (Document Library) under that Site
            drive_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive"
            r_drive = requests.get(drive_url, headers=self.headers)
            r_drive.raise_for_status()
            
            self.drive_id = r_drive.json().get('id')
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to resolve Drive ID. Please check if SHAREPOINT_SITE_URL is correct (must include /personal/...). Error: {e}")
            return False

    def connect(self):
        """Initialize connection process."""
        if not all([self.site_url, self.client_id, self.client_secret, self.tenant_id]):
            print("[ERROR] Missing credentials in .env")
            return False
            
        print("1. Getting Access Token...", end=" ")
        if not self._get_token(): return False
        print("[SUCCESS]")
        
        print("2. Resolving Drive ID...", end=" ")
        if not self._get_drive_id(): return False
        print("[SUCCESS]")
        
        return True

    def ensure_folder(self, path):
        """Recursively create folders (Graph API)."""
        # Graph API cannot create multi-level paths at once like SharePoint
        # We need to check level by level
        if not self.drive_id: return False
        
        # Remove leading slash
        clean_path = path.strip('/')
        parts = clean_path.split('/')
        
        current_parent_id = "root" # Start from root
        
        for part in parts:
            # Check if folder exists
            check_url = f"https://graph.microsoft.com/v1.0/drives/{self.drive_id}/items/{current_parent_id}/children?$filter=name eq '{part}'"
            r = requests.get(check_url, headers=self.headers)
            
            found = False
            if r.status_code == 200:
                items = r.json().get('value', [])
                if items:
                    current_parent_id = items[0]['id']
                    found = True
            
            if not found:
                # Create folder
                create_url = f"https://graph.microsoft.com/v1.0/drives/{self.drive_id}/items/{current_parent_id}/children"
                payload = {
                    "name": part,
                    "folder": {},
                    "@microsoft.graph.conflictBehavior": "rename"
                }
                r_create = requests.post(create_url, headers=self.headers, json=payload)
                if r_create.status_code in [200, 201]:
                    current_parent_id = r_create.json().get('id')
                else:
                    tqdm.write(f"[ERROR] Could not create folder {part}: {r_create.text}")
                    return False
        return current_parent_id

    def upload_file(self, local_path, remote_subfolder):
        """Upload file."""
        filename = os.path.basename(local_path)
        full_remote_path = f"{self.root_folder_path}/{remote_subfolder}".strip("/")
        
        try:
            # 1. Ensure folder exists and get target folder ID
            folder_id = self.ensure_folder(full_remote_path)
            if not folder_id: return False
            
            # 2. Upload file
            upload_url = f"https://graph.microsoft.com/v1.0/drives/{self.drive_id}/items/{folder_id}:/{filename}:/content"
            
            with open(local_path, 'rb') as f:
                content = f.read()
                
            r = requests.put(upload_url, headers=self.headers, data=content)
            
            if r.status_code in [200, 201]:
                return True
            else:
                tqdm.write(f"[ERROR] Upload API Failed: {r.text}")
                return False
                
        except Exception as e:
            tqdm.write(f"[ERROR] Upload Exception: {e}")
            return False