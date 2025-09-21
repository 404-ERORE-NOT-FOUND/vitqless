import os
import pathlib
import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from google.auth.transport import requests as google_requests

# Load environment variables from .env file
load_dotenv()

# --- Google OAuth Setup ---
# Manually create a client_secrets.json equivalent from .env for the flow object
client_config = {
    "web": {
        "client_id": os.environ.get("GOOGLE_CLIENT_ID"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET"),
        "redirect_uris": ["http://127.0.0.1:5000/callback"]
    }
}

# The Google-auth flow to handle the OAuth 2.0 process
flow = Flow.from_client_config(
    client_config,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
)

# --- Flask Application Setup ---
app = Flask(__name__)
# A strong secret key is required for Flask sessions
app.secret_key = "your_strong_secret_key" 

# --- Core Web Pages ---
@app.route('/')
def dashboard():
    # Protect the dashboard by checking for a user in the session
    if 'user_email' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    # Retrieve user data from the session and pass it to the template
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    user_name = session.get('user_name', 'User')
    user_email = session.get('user_email', 'No Email')
    
    return render_template('profile.html', user_name=user_name, user_email=user_email)

@app.route('/appointments')
def appointments():
    return render_template('appointments.html')

@app.route('/admin')
def admin_login():
    return render_template('admin.html')

@app.route('/queue/<name>')
def queue(name):
    return render_template('queue.html', queue_name=name)

# --- OAuth Routes ---
@app.route("/authorize")
def authorize():
    # Redirects the user to Google's consent screen
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

@app.route("/callback")
def callback():
    # Handles the response from Google and exchanges the auth code for a token
    try:
        flow.fetch_token(authorization_response=request.url)
    except Exception as e:
        return f"Error fetching token: {e}", 400

    if not "state" in session or session["state"] != request.args.get("state"):
        return "State mismatch!", 400

    credentials = flow.credentials
    request_session = google_requests.Request()
    
    try:
        # Verify the ID token and get user info
        user_info = id_token.verify_oauth2_token(
            credentials.id_token, request_session, flow.client_config['web']['client_id']
        )
        
        email = user_info["email"]
        
        # Check for the required email domain
        if not email.endswith('@vitstudent.ac.in'):
            return "Access denied. Use your official VIT email.", 403

        # Store user info in session
        session["user_uid"] = user_info.get("sub")
        session["user_name"] = user_info.get("name")
        session["user_email"] = user_info.get("email")
        
        # TODO: Here is where you would save the user info to your database

    except ValueError:
        return "Could not verify user token.", 400

    return redirect(url_for('dashboard'))

# --- API Endpoints (from your original project) ---
@app.route('/api/queues')
def get_all_queues():
    queues = [
        {"name": "Q Block Paid Mess", "count": 158, "id": "q-block-mess"},
        {"name": "Admin Office", "count": 25, "id": "admin-office"},
    ]
    return jsonify(queues)

@app.route('/api/live_data')
def get_live_data():
    live_data = {
        "active_token_number": 57,
        "active_token_service": "Q Block Paid Mess",
        "featured_message": "Reminder to book an appointment."
    }
    return jsonify(live_data)

# --- To run the application ---
if __name__ == "__main__":
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    app.run(debug=True, host="0.0.0.0")