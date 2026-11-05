import os
from pathlib import Path
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

def main():
    client_id = os.getenv("GMAIL_CLIENT_ID")
    client_secret = os.getenv("GMAIL_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("Error: GMAIL_CLIENT_ID or GMAIL_CLIENT_SECRET not found in .env file!")
        return

    # Check if credentials.json exists directly
    creds_file = Path("credentials.json")
    if creds_file.exists():
        print("Found credentials.json, using file...")
        flow = InstalledAppFlow.from_client_secrets_file(str(creds_file), SCOPES)
    else:
        client_config = {
            "installed": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost", "http://127.0.0.1"]
            }
        }
        flow = InstalledAppFlow.from_client_config(client_config, SCOPES)

    print("\n" + "="*60)
    print("Launching browser for Google OAuth authorization...")
    print("Please select your test Gmail account and grant permissions.")
    print("="*60 + "\n")

    try:
        creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")
    except Exception as e:
        print(f"Error during flow execution: {e}")
        return

    refresh_token = creds.refresh_token
    if not refresh_token:
        print("\n[Warning] Refresh token was not returned. Make sure to accept the prompt.")
        return

    print("\n" + "="*60)
    print("SUCCESS! Refresh Token obtained:")
    print(refresh_token)
    print("="*60 + "\n")

    # Update .env file
    env_path = Path(".env")
    if env_path.exists():
        content = env_path.read_text(encoding="utf-8")
        if "GMAIL_REFRESH_TOKEN=" in content:
            lines = content.splitlines()
            new_lines = []
            for l in lines:
                if l.startswith("GMAIL_REFRESH_TOKEN="):
                    new_lines.append(f"GMAIL_REFRESH_TOKEN={refresh_token}")
                else:
                    new_lines.append(l)
            env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        else:
            with open(".env", "a", encoding="utf-8") as f:
                f.write(f"\nGMAIL_REFRESH_TOKEN={refresh_token}\n")
        print("Updated .env file with GMAIL_REFRESH_TOKEN!")

if __name__ == "__main__":
    main()
