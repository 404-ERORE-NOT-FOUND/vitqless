import os
import firebase_admin
from firebase_admin import credentials, firestore, auth
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, jsonify

# Load environment variables from .env file
load_dotenv()

# --- Firebase Admin SDK Setup ---
# Get the path to your Firebase service account key from the .env file
SERVICE_ACCOUNT_KEY_PATH = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY_PATH")

if not SERVICE_ACCOUNT_KEY_PATH or not os.path.exists(SERVICE_ACCOUNT_KEY_PATH):
    print("Error: Firebase service account key file not found. Please check your .env file.")
    exit()

try:
    cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
except Exception as e:
    print(f"Error initializing Firebase Admin SDK: {e}")
    exit()

# --- Flask Application Setup ---
app = Flask(__name__)

# --- Core Web Pages ---
@app.route('/')
def dashboard():
    """Renders the main dashboard page."""
    return render_template('index.html')

@app.route('/login')
def login():
    """Renders the login page."""
    # Pass environment variables to the template for client-side Firebase config
    return render_template(
        'login.html',
        firebase_api_key=os.getenv("FIREBASE_API_KEY"),
        firebase_auth_domain=os.getenv("FIREBASE_AUTH_DOMAIN"),
        firebase_project_id=os.getenv("FIREBASE_PROJECT_ID"),
        firebase_storage_bucket=os.getenv("FIREBASE_STORAGE_BUCKET"),
        firebase_messaging_sender_id=os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
        firebase_app_id=os.getenv("FIREBASE_APP_ID")
    )

@app.route('/profile')
def profile():
    """Renders the user profile page."""
    return render_template('profile.html')

@app.route('/appointments')
def appointments():
    """Renders the appointments booking page."""
    return render_template('appointments.html')

@app.route('/admin')
def admin_login():
    """Renders the admin login page."""
    return render_template('admin.html')

@app.route('/queue/<name>')
def queue(name):
    """Renders a specific queue page."""
    return render_template('queue.html', queue_name=name)

# --- API Endpoints ---
@app.route('/api/auth/google', methods=['POST'])
def google_auth():
    """
    Handles Google Sign-in token verification and authenticates users.
    Restricts access to @vitstudent.ac.in accounts only.
    """
    id_token = request.json.get('idToken')
    
    if not id_token:
        return jsonify({"error": "ID token not provided."}), 400
    
    try:
        decoded_token = auth.verify_id_token(id_token)
        email = decoded_token.get('email')
        
        # --- Authentication Rule: Only allow @vitstudent.ac.in emails ---
        if not email or not email.endswith('@vitstudent.ac.in'):
            return jsonify({
                "error": "Access Denied. Please use your official @vitstudent.ac.in email account."
            }), 403
            
        uid = decoded_token['uid']
        
        # Store or update user details in Firestore
        user_ref = db.collection('users').document(uid)
        user_ref.set({
            'email': email,
            'name': decoded_token.get('name', 'N/A')
        }, merge=True)
        
        return jsonify({"message": "User authenticated successfully", "uid": uid}), 200
        
    except auth.InvalidIdTokenError:
        return jsonify({"error": "Invalid or expired authentication token."}), 401
    except Exception as e:
        return jsonify({"error": f"Authentication failed: {str(e)}"}), 500

@app.route('/api/queues')
def get_all_queues():
    """Returns a JSON list of all live queues from Firestore."""
    queues_ref = db.collection('queues')
    queues = [doc.to_dict() for doc in queues_ref.stream()]
    return jsonify(queues)

@app.route('/api/live_data')
def get_live_data():
    """Returns live data for active tokens and featured content from Firestore."""
    doc_ref = db.collection('live_data').document('dashboard_info')
    doc = doc_ref.get()
    
    if doc.exists:
        live_data = doc.to_dict()
        return jsonify(live_data)
    else:
        return jsonify({"message": "Live data not found"}), 404

# --- To run the application ---
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')