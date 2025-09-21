import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

# Load environment variables from .env file
load_dotenv()

# --- Google Identity Services Setup ---
# You only need your client ID now
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
if not GOOGLE_CLIENT_ID:
    raise RuntimeError("GOOGLE_CLIENT_ID environment variable not set.")

# --- Flask Application Setup ---
app = Flask(__name__)
# A strong secret key is required for Flask sessions
app.secret_key = "your_strong_secret_key" 

# --- Core Web Pages ---
@app.route('/')
def dashboard():
    # You can add a check here to ensure the user is logged in
    # if 'user_email' not in session:
    #     return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login')
def login():
    # This route renders the login page with the Google Sign-in button
    return render_template('login.html', GOOGLE_CLIENT_ID=GOOGLE_CLIENT_ID)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    # This route is now protected and requires a logged-in user
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    # You can get user details from the session
    return render_template('profile.html', user_name=session.get('user_name'), user_email=session.get('user_email'))


@app.route('/appointments')
def appointments():
    return render_template('appointments.html')

@app.route('/admin')
def admin_login():
    return render_template('admin.html')

@app.route('/queue/<name>')
def queue(name):
    return render_template('queue.html', queue_name=name)

# --- GSI Callback Endpoint ---
@app.route('/callback')
def callback():
    token = request.args.get("token")
    if not token:
        return "Authentication token not provided.", 400

    try:
        # Verify the ID token using the client ID
        id_info = id_token.verify_oauth2_token(token, google_requests.Request(), GOOGLE_CLIENT_ID)
        
        # Check for the required VIT email domain
        if not id_info.get('email', '').endswith('@vitstudent.ac.in'):
            return "Access denied. Use your official VIT email.", 403

        # Set user details in the Flask session
        session['logged_in'] = True
        session['user_uid'] = id_info['sub']
        session['user_email'] = id_info['email']
        session['user_name'] = id_info.get('name')

        # TODO: Save user details to your database here
        # This is where you would call your Firestore or MongoDB logic
        # For now, it just stores the info in the session.
        
        return redirect(url_for('dashboard'))

    except ValueError:
        return "Invalid or expired authentication token.", 401
    except Exception as e:
        return f"An unexpected error occurred: {e}", 500

# --- Original Project's API Endpoints ---
@app.route('/api/queues')
def get_all_queues():
    # Your original API logic for queues goes here
    # For now, this returns placeholder data
    queues = [
        {"name": "Q Block Paid Mess", "count": 158, "id": "q-block-mess"},
        {"name": "Admin Office", "count": 25, "id": "admin-office"},
    ]
    return jsonify(queues)

@app.route('/api/live_data')
def get_live_data():
    # Your original API logic for live data goes here
    live_data = {
        "active_token_number": 57,
        "active_token_service": "Q Block Paid Mess",
        "featured_message": "Reminder to book an appointment."
    }
    return jsonify(live_data)

# --- To run the application ---
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')