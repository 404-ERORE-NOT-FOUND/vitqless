import os
import re
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import firebase_admin
from firebase_admin import credentials, firestore

# Load environment variables from .env file
load_dotenv()

# --- Google Identity Services Setup ---
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
if not GOOGLE_CLIENT_ID:
    raise RuntimeError("GOOGLE_CLIENT_ID environment variable not set.")

# --- Firebase Admin SDK Setup ---
FIREBASE_CREDENTIALS_PATH = os.environ.get("FIREBASE_CREDENTIALS_PATH")
if not FIREBASE_CREDENTIALS_PATH or not os.path.exists(FIREBASE_CREDENTIALS_PATH):
    pass 

if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
    firebase_admin.initialize_app(cred)
db = firestore.client()

# --- Flask Application Setup ---
app = Flask(__name__)
app.secret_key = "your_strong_secret_key" 

# --- Core Web Pages ---
@app.route('/')
def dashboard():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    current_hour = datetime.now().hour
    if 5 <= current_hour < 12:
        greeting_message = "Good morning"
    elif 12 <= current_hour < 17:
        greeting_message = "Good afternoon"
    elif 17 <= current_hour < 22:
        greeting_message = "Good evening"
    else:
        greeting_message = "Good night"
    
    user_name = session.get('user_name', 'User')
    
    return render_template('index.html', user_name=user_name, greeting=greeting_message)

@app.route('/login')
def login():
    return render_template('login.html', GOOGLE_CLIENT_ID=GOOGLE_CLIENT_ID)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    user_name = session.get('user_name', 'User')
    user_email = session.get('user_email', 'No Email')
    reg_no = session.get('reg_no', 'N/A')
    
    return render_template('profile.html', user_name=user_name, user_email=user_email, reg_no=reg_no)

@app.route('/appointments')
def appointments():
    return render_template('appointments.html')

@app.route('/admin')
def admin_page():
    if not session.get('is_admin'):
        return "Access Denied", 403
    
    queues_ref = db.collection('queues')
    queues = [doc.to_dict() for doc in queues_ref.stream()]
    
    return render_template('admin.html', queues=queues)

@app.route('/admin/queues/create', methods=['GET', 'POST'])
def admin_create_queue():
    if not session.get('is_admin'):
        return "Access Denied", 403

    if request.method == 'POST':
        queue_name = request.form.get('queue_name')
        if queue_name:
            new_queue_doc = db.collection('queues').document()
            new_queue_doc.set({
                'name': queue_name,
                'current_token': 0,
                'last_token': 0,
                'created_at': firestore.SERVER_TIMESTAMP
            })
            return redirect(url_for('admin_page'))
    
    return render_template('admin_create_queue.html')

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
        id_info = id_token.verify_oauth2_token(token, google_requests.Request(), GOOGLE_CLIENT_ID)
        
        email = id_info.get('email', '')
        
        is_admin = (email == 'axongfx.help@gmail.com')
        if not is_admin and not email.endswith('@vitstudent.ac.in'):
            return "Access denied. Use your official VIT email.", 403
        
        google_name = id_info.get('name')
        uid = id_info['sub']

        extracted_reg_no = None
        display_name = google_name
        
        reg_no_match = re.search(r'(\d{2}[A-Z]{3}\d{4})', email) or re.search(r'(\d{2}[A-Z]{3}\d{4})', google_name)
        
        if reg_no_match:
            extracted_reg_no = reg_no_match.group(1).upper()
            display_name = re.sub(r'\s*' + re.escape(extracted_reg_no) + r'\s*', '', google_name, flags=re.IGNORECASE).strip()

        session['user_uid'] = uid
        session['user_email'] = email
        session['user_name'] = display_name
        session['reg_no'] = extracted_reg_no
        session['is_admin'] = is_admin

        user_ref = db.collection('users').document(uid)
        user_doc = user_ref.get()

        if not user_doc.exists:
            user_ref.set({
                'name': display_name,
                'email': email,
                'reg_no': extracted_reg_no,
                'is_admin': is_admin,
                'created_at': firestore.SERVER_TIMESTAMP
            })
        else:
            update_data = {}
            if user_doc.to_dict().get('name') != display_name:
                update_data['name'] = display_name
            if user_doc.to_dict().get('email') != email:
                update_data['email'] = email
            if user_doc.to_dict().get('reg_no') != extracted_reg_no:
                update_data['reg_no'] = extracted_reg_no
            if user_doc.to_dict().get('is_admin') != is_admin:
                update_data['is_admin'] = is_admin
            
            if update_data:
                user_ref.update(update_data)
        
        if is_admin:
            return redirect(url_for('admin_page'))
        else:
            return redirect(url_for('dashboard'))

    except ValueError:
        return "Invalid or expired authentication token.", 401
    except Exception as e:
        return f"An unexpected error occurred: {e}", 500

# --- API Endpoints ---
@app.route('/api/queues')
def get_all_queues():
    queues_ref = db.collection('queues').order_by('created_at', direction=firestore.Query.DESCENDING)
    queues = [doc.to_dict() for doc in queues_ref.stream()]
    return jsonify(queues)

@app.route('/api/live_data')
def get_live_data():
    live_data = {
        "active_token_number": 57,
        "active_token_service": "Q Block Paid Mess",
        "featured_message": "Reminder to book an appointment."
    }
    return jsonify(live_data)

@app.route('/api/queues/join/<queue_id>')
def join_queue(queue_id):
    if 'user_uid' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    queue_ref = db.collection('queues').document(queue_id)
    
    queue_doc = queue_ref.get()
    if not queue_doc.exists:
        return jsonify({"error": "Queue not found"}), 404

    queue_data = queue_doc.to_dict()
    last_token = queue_data.get('last_token', 0)
    new_token = last_token + 1

    queue_ref.update({
        'last_token': new_token,
        'users': firestore.ArrayUnion([{
            'uid': session.get('user_uid'),
            'token': new_token,
            'joined_at': firestore.SERVER_TIMESTAMP
        }])
    })
    
    return jsonify({"token": new_token, "queue_name": queue_data.get('name')})

@app.route('/api/queues/serve_next/<queue_id>', methods=['POST'])
def serve_next(queue_id):
    if not session.get('is_admin'):
        return jsonify({"error": "Permission Denied"}), 403

    queue_ref = db.collection('queues').document(queue_id)
    queue_doc = queue_ref.get()
    
    if not queue_doc.exists:
        return jsonify({"error": "Queue not found"}), 404

    current_token = queue_doc.to_dict().get('current_token', 0)
    queue_ref.update({'current_token': current_token + 1})
    
    return jsonify({"message": "Next person served"})

@app.route('/api/queues/set_tokens/<queue_id>', methods=['POST'])
def set_tokens(queue_id):
    if not session.get('is_admin'):
        return jsonify({"error": "Permission Denied"}), 403

    data = request.get_json()
    new_current = data.get('current_token')
    new_last = data.get('last_token')

    if new_current is None or new_last is None:
        return jsonify({"error": "Missing token values"}), 400

    queue_ref = db.collection('queues').document(queue_id)
    queue_ref.update({
        'current_token': int(new_current),
        'last_token': int(new_last)
    })
    
    return jsonify({"message": "Tokens updated successfully"}), 200

# --- To run the application ---
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')