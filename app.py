import os
import uuid
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for, session, send_file
from pymongo import MongoClient
import pandas as pd
from datetime import datetime
from urllib.parse import quote_plus
import certifi
import io

app = Flask(__name__)
app.secret_key = "aditya_university_secret_key" 

# --- 1. DATABASE CONNECTION ---
username = quote_plus('proudtobecoder_db_user')
password = quote_plus('Mukesh2007') 
uri = f"mongodb+srv://{username}:{password}@dean.b0lfohs.mongodb.net/?appName=DEAN"

try:
    client = MongoClient(uri, tlsCAFile=certifi.where())
    db = client['excel_dashboard_db']
    uploads_meta = db['uploads_meta']
    print("✅ SUCCESS: Connected to MongoDB")
except Exception as e:
    print(f"❌ DATABASE ERROR: {e}")
    db = None

# --- 2. CLUB DATA ---
CLUBS_DATA = {
    "1": {"id": "1", "name": "Abhinaya Club", "head": "Dr. T. Neelima", "category": "Cultural", "img": "club-1.png", "username": "neelima", "password": "neelima_abhinaya"},
    "2": {"id": "2", "name": "Eco Club", "head": "Mrs. P. Lakshmi", "category": "Environmental", "img": "club-2.png", "username": "lakshmi", "password": "lakshmi_ecoclub"},
    "3": {"id": "3", "name": "Leo Club", "head": "Mr. N. Naresh", "category": "Social", "img": "club-3.png", "username": "naresh", "password": "naresh_leoclub"},
    "4": {"id": "4", "name": "LitVerse Club", "head": "Dr. M. Mary Jyothi", "category": "Literary", "img": "club-4.png", "username": "mary", "password": "mary_litverse"},
    "5": {"id": "5", "name": "Motor Sports Club", "head": "Dr. Rahul Bharathi", "category": "Technical", "img": "club-5.png", "username": "bharathi", "password": "bharathi_motorsports"},
    "6": {"id": "6", "name": "Innovative Makers (IMEC)", "head": "Mr. P. Jai Kishan", "category": "Technical", "img": "club-6.png", "username": "kishan", "password": "kishan_imec"},
    "7": {"id": "7", "name": "Rotaract Club", "head": "Mr. V. V. Srimannarayana", "category": "Social", "img": "club-7.png", "username": "srimanarayana", "password": "narayana_rotaract"},
    "8": {"id": "8", "name": "Youth Red Cross", "head": "Mr. Siva Kumar", "category": "Social", "img": "club-8.png", "username": "sivakumar", "password": "sivakumar_yrc"},
    "9": {"id": "9", "name": "Film & Photography Club", "head": "Dr. R. Uzwal Kiran", "category": "Creative", "img": "club-9.png", "username": "kiran", "password": "kiran_fpc"},
    "10": {"id": "10", "name": "Aditya Space Tech", "head": "Dr. Akash Kumar Gupta", "category": "Science", "img": "club-10.png", "username": "akash", "password": "akash_astecc"},
    "11": {"id": "11", "name": "Digital Media Club", "head": "Mr. Ch. Kasi Viswanadham", "category": "Media", "img": "club-11.png", "username": "vishwanadham", "password": "vishwanadham_dmc"},
    "12": {"id": "12", "name": "Heritage (Spic Macay)", "head": "Ms. B. Prameela Rani", "category": "Cultural", "img": "club-12.png", "username": "rani", "password": "rani_heritage"},
    "13": {"id": "13", "name": "Google Developers Group", "head": "Mr. V. Appalakonda", "category": "Coding", "img": "club-13.png", "username": "appalakonda", "password": "appalakonda_gdg"},
    "14": {"id": "14", "name": "Chanakya Capital Club", "head": "Mr. B. Surya Teja", "category": "Finance", "img": "club-14.png", "username": "surya", "password": "surya_ccc"},
    "15": {"id": "15", "name": "Strategic Leaders Forum", "head": "Mr. B. Kamesh Sharma", "category": "Leadership", "img": "club-15.png", "username": "kamesh", "password": "kamesh_slf"},
    "16": {"id": "16", "name": "Elite Marketing Hub", "head": "Mr. K. Pardha Sai", "category": "Business", "img": "club-16.png", "username": "pardhasai", "password": "pardhasai_emh"},
    "17": {"id": "17", "name": "Diz Initiatives Club", "head": "Dr. T. Suresh", "category": "Innovation", "img": "club-17.png", "username": "suresh", "password": "suresh_dic"},
    "18": {"id": "18", "name": "The Synergy Squad", "head": "Dr. Aarif Mohd Sheikh", "category": "General", "img": "club-18.png", "username": "aarif", "password": "aarif_tss"},
    "19": {"id": "19", "name": "Pharm-AI Club", "head": "Ms. K. Pushpalatha", "category": "Medical", "img": "club-19.png", "username": "pushpalatha", "password": "pushpalatha_pac"},
    "20": {"id": "20", "name": "Rx Wellness Club", "head": "Mrs. T. Gowthami", "category": "Health", "img": "club-20.png", "username": "gowthami", "password": "gowthami_rwc"}
}

# --- 3. PAGE ROUTING LOGIC ---

@app.route('/')
def landing():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/home')
def dean_dashboard():
    if session.get('user_role') != 'dean':
        return redirect(url_for('login_page'))
    return render_template('frontend.html', clubs=CLUBS_DATA)

# --- NEW: Annual Reports Route ---
@app.route('/reports')
def annual_reports():
    if session.get('user_role') != 'dean':
        return redirect(url_for('login_page'))
    return render_template('annualreports.html')

@app.route('/club/<club_id>')
def club_dashboard(club_id):
    if 'user_role' not in session:
        return redirect(url_for('login_page', next=f'/club/{club_id}'))
    
    user_role = session['user_role']
    user_id = session.get('user_id') 

    if user_role == 'coordinator' and user_id != club_id:
        return f"<h1>Access Denied</h1><p>You cannot view this club.</p><a href='/club/{user_id}'>Go to My Club</a>"

    club = CLUBS_DATA.get(club_id)
    if not club: return "Club Not Found", 404
    
    return render_template('club_dashboard.html', club=club, club_id=club_id, user_role=user_role)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('landing'))

# --- 4. AUTHENTICATION API ---

@app.route('/api/login', methods=['POST'])
def login_api():
    data = request.json
    role = data.get('role')
    user_input = data.get('email')
    password = data.get('password')
    
    if role == 'dean':
        if user_input == 'dean@aditya.ac.in' and password == 'admin':
            session['user_role'] = 'dean'
            session['user_id'] = 'dean'
            return jsonify({"success": True, "redirect": '/home'})
    
    elif role == 'coordinator':
        for club_id, club_info in CLUBS_DATA.items():
            if user_input.strip() == club_info['username']:
                if password == club_info['password']:
                    session['user_role'] = 'coordinator'
                    session['user_id'] = club_id
                    return jsonify({"success": True, "redirect": f'/club/{club_id}'})
        
        return jsonify({"success": False, "message": "User ID Not Found"})

    return jsonify({"success": False, "message": "Invalid Credentials"})

# --- 5. FILE & DATA API ---

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files: return jsonify({"error": "No file"}), 400
    file = request.files['file']
    club_id = request.form.get('club_id')
    
    if file and club_id:
        file_id = str(uuid.uuid4())
        collection_name = f"data_{file_id}" 
        
        try:
            file.seek(0)
            df = pd.read_excel(file)
        except:
            try:
                df = pd.read_excel(file, engine='openpyxl')
            except:
                return jsonify({"error": "Invalid Excel File"}), 400
        
        df = df.fillna('').astype(str)
        records = df.to_dict(orient='records')
        if records: db[collection_name].insert_many(records)
        
        meta = {
            "file_id": file_id,
            "club_id": str(club_id),
            "filename": file.filename,
            "collection_name": collection_name,
            "upload_date": datetime.now(),
            "columns": list(df.columns),
            "event_name": request.form.get('event_name'),
            "event_date": request.form.get('event_date'),
            "team_head": request.form.get('team_head')
        }
        uploads_meta.insert_one(meta)
        return jsonify({"message": "Success", "file_id": file_id}), 200
    return jsonify({"error": "Failed"}), 500

@app.route('/api/files', methods=['GET'])
def get_files():
    club_id = request.args.get('club_id')
    query = {"club_id": str(club_id)} if club_id else {}
    files = list(uploads_meta.find(query, {'_id': 0}).sort('upload_date', -1))
    return jsonify(files)

@app.route('/api/data/<file_id>', methods=['GET'])
def get_data(file_id):
    meta = uploads_meta.find_one({"file_id": file_id})
    if not meta: return jsonify({"error": "Not Found"}), 404
    data = list(db[meta['collection_name']].find({}, {'_id': 0}))
    return jsonify({
        "data": data, "columns": meta['columns'], 
        "event_name": meta.get('event_name'), "event_date": meta.get('event_date'), "team_head": meta.get('team_head')
    })

@app.route('/api/export', methods=['POST'])
def export_filtered_data():
    if db is None: return jsonify({"error": "Database disconnected"}), 500
    try:
        req_data = request.json
        file_id = req_data.get('file_id')
        selected_columns = req_data.get('selected_columns', [])

        meta = uploads_meta.find_one({"file_id": file_id})
        if not meta: return jsonify({"error": "File not found"}), 404
        
        data = list(db[meta['collection_name']].find({}, {'_id': 0}))
        df = pd.DataFrame(data)

        if selected_columns:
            valid_cols = [c for c in selected_columns if c in df.columns]
            if valid_cols:
                df = df[valid_cols]

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Filtered Data')
        
        output.seek(0)
        filename = f"Filtered_{meta.get('event_name', 'Data')}.xlsx"
        
        return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name=filename)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- NEW: Aggregation API for Graphs ---
@app.route('/api/stats/annual', methods=['GET'])
def get_annual_stats():
    if db is None: return jsonify({"error": "Database error"}), 500

    # Initialize aggregators
    stats = {
        "schools": {},
        "events": {},
        "years": {},
        "departments": {}
    }

    # Fetch all file metadata
    all_files = list(uploads_meta.find({}))
    
    # Helper to find column by keywords
    def find_col(columns, keywords):
        for col in columns:
            if any(k in col.lower() for k in keywords):
                return col
        return None

    for file_meta in all_files:
        event_name = file_meta.get('event_name', 'Unknown Event')
        collection_name = file_meta.get('collection_name')
        
        # Load data for this file
        raw_data = list(db[collection_name].find({}, {'_id': 0}))
        if not raw_data: continue
        
        df = pd.DataFrame(raw_data)
        count = len(df)

        # 1. Events vs Participants
        stats['events'][event_name] = stats['events'].get(event_name, 0) + count

        # Detect Columns (fuzzy matching)
        school_col = find_col(df.columns, ['school', 'inst', 'college'])
        dept_col = find_col(df.columns, ['dept', 'department', 'branch'])
        year_col = find_col(df.columns, ['year', 'sem', 'current year'])

        # 2. Schools vs Participants
        if school_col:
            school_counts = df[school_col].value_counts().to_dict()
            for k, v in school_counts.items():
                k_clean = str(k).strip()
                if k_clean: stats['schools'][k_clean] = stats['schools'].get(k_clean, 0) + v
        
        # 3. Departments vs Participants
        if dept_col:
            dept_counts = df[dept_col].value_counts().to_dict()
            for k, v in dept_counts.items():
                k_clean = str(k).strip()
                if k_clean: stats['departments'][k_clean] = stats['departments'].get(k_clean, 0) + v

        # 4. Years vs Participants
        if year_col:
            year_counts = df[year_col].value_counts().to_dict()
            for k, v in year_counts.items():
                k_clean = str(k).strip()
                if k_clean: stats['years'][k_clean] = stats['years'].get(k_clean, 0) + v

    return jsonify(stats)

@app.route('/images/<path:filename>')
def serve_images(filename):
    return send_from_directory('static/images', filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)