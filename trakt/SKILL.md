---
name: Trakt Authentication
description: Instructions on how to authenticate with the Trakt API using a local web server to capture the OAuth code, and how to store the tokens and credentials in ~/.trakt-mcp.
---

# Trakt API Authentication Skill

This skill explains how to automate the authentication process with the Trakt API (OAuth 2.0).

## 1. Credentials
You will need the `client_id` and `client_secret` from your Trakt API App.

## 2. Authorization Flow
To avoid making the user manually copy and paste the Authorization Code (PIN), you should spin up a temporary local Python web server. The server will catch the redirect from Trakt, extract the code, and then shut itself down.

> **Note**: The user must configure the app's **Redirect URI** on Trakt to match your local server port exactly, e.g., `http://localhost:37295`. Port `37295` is recommended as an uncommon port to avoid clashing with other local development servers.

### Step-by-Step
1. **Start a local web server**: Run a short-lived Python HTTP server on port `37295`.
2. **Open the browser**: Provide the Trakt authorization URL to the user or open it automatically:
   `https://trakt.tv/oauth/authorize?response_type=code&client_id=<CLIENT_ID>&redirect_uri=http://localhost:37295`
3. **Capture the code**: Once the user approves the app, Trakt redirects to `http://localhost:37295/?code=<AUTHORIZATION_CODE>`. The local server parses the query string to save the `code`, then immediately stops.
4. **Exchange for Token**: Use the extracted `code` to make a POST request to `https://api.trakt.tv/oauth/token` to retrieve the `access_token` and `refresh_token`.
5. **Save to Dotfile**: Save the `access_token`, `refresh_token`, `client_id`, and `client_secret` in a JSON file at `~/.trakt-mcp`. This allows you to easily read the credentials for future API requests and regenerate the token if it expires.

## Example Python Script
Here is a complete, standalone Python snippet demonstrating this automated flow:

```python
import urllib.request
import urllib.parse
import json
import os
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

CLIENT_ID = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"
PORT = 37295
REDIRECT_URI = f"http://localhost:{PORT}"
CREDENTIALS_FILE = os.path.expanduser("~/.trakt-mcp")

auth_code = None

class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        
        if 'code' in params:
            auth_code = params['code'][0]
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"<html><body><h1>Autenticazione Trakt completata!</h1><p>Puoi chiudere questa finestra e tornare al terminale.</p></body></html>")
            # Shutdown server asynchronously
            threading.Thread(target=self.server.shutdown).start()
        else:
            self.send_response(400)
            self.end_headers()
            
    # Suppress log messages
    def log_message(self, format, *args):
        pass

def authenticate():
    print(f"Avvio del server in ascolto sulla porta {PORT}...")
    server = HTTPServer(('localhost', PORT), OAuthHandler)
    
    auth_url = f"https://trakt.tv/oauth/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={urllib.parse.quote(REDIRECT_URI, safe='')}"
    print(f"\nSe il browser non si apre da solo, clicca su questo link:\n{auth_url}\n")
    
    webbrowser.open(auth_url)
    server.serve_forever()
    
    if auth_code:
        print("Codice catturato dal server locale. Scambio in corso...")
        token_data = {
            "code": auth_code,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code"
        }
        
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" # Prevents Cloudflare blocks
        }
        
        req = urllib.request.Request("https://api.trakt.tv/oauth/token", data=json.dumps(token_data).encode(), headers=headers)
        
        try:
            with urllib.request.urlopen(req) as response:
                token_res = json.loads(response.read().decode())
                
                # Save to dotfile
                save_data = {
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "access_token": token_res["access_token"],
                    "refresh_token": token_res["refresh_token"]
                }
                
                with open(CREDENTIALS_FILE, 'w') as f:
                    json.dump(save_data, f, indent=4)
                print(f"Successo! Credenziali salvate in: {CREDENTIALS_FILE}")
        except Exception as e:
            print(f"Errore nello scambio del token: {e}")
            if hasattr(e, 'read'):
                print(e.read().decode())

if __name__ == "__main__":
    authenticate()
```

## Refreshing an Expired Token
When the `access_token` expires, you don't need user interaction. Read `~/.trakt-mcp`, extract the `refresh_token`, and make a POST request to `https://api.trakt.tv/oauth/token` with the `grant_type` set to `refresh_token`. Then, overwrite `~/.trakt-mcp` with the new tokens returned.
