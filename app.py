import streamlit as st
import google.generativeai as genai
import json
import hashlib
from datetime import datetime
import uuid
import os

# --- PAGE SETUP ---
st.set_page_config(
    page_title="The Molecular Man AI",
    page_icon="🧮",
    layout="wide"
)

st.markdown("""
    <style>
    .main {
        background-color: #0d1117;
    }
    .solution-box {
        background-color: white; 
        padding: 40px; 
        border-radius: 10px; 
        color: black;
        border: 2px solid #e0e0e0;
    }
    .login-box {
        max-width: 400px;
        margin: 100px auto;
        padding: 40px;
        background-color: #1a1a1a;
        border-radius: 10px;
        border: 2px solid #ffd700;
    }
    </style>
""", unsafe_allow_html=True)

# --- SIMPLE FILE STORAGE ---
# These files store usernames and passwords
USERS_FILE = "users_database.json"
SESSIONS_FILE = "active_sessions.json"

# Create empty database if it doesn't exist
def create_empty_database():
    if not os.path.exists(USERS_FILE):
        # Start with one admin user
        initial_users = {
            "admin": "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"  # password: "admin"
        }
        with open(USERS_FILE, "w") as f:
            json.dump(initial_users, f)

# Create empty sessions file
def create_empty_sessions():
    if not os.path.exists(SESSIONS_FILE):
        with open(SESSIONS_FILE, "w") as f:
            json.dump({}, f)

create_empty_database()
create_empty_sessions()

# Generate unique device ID for this browser/device
def get_device_id():
    if "device_id" not in st.session_state:
        st.session_state.device_id = str(uuid.uuid4())
    return st.session_state.device_id

# Check if user is already logged in on another device
def is_user_logged_elsewhere(username, current_device_id):
    with open(SESSIONS_FILE, "r") as f:
        sessions = json.load(f)
    
    if username in sessions:
        old_device_id = sessions[username]
        if old_device_id != current_device_id:
            return True, old_device_id  # Logged in somewhere else
    return False, None  # Not logged in elsewhere

# Save active session
def save_session(username, device_id):
    with open(SESSIONS_FILE, "r") as f:
        sessions = json.load(f)
    
    sessions[username] = device_id
    
    with open(SESSIONS_FILE, "w") as f:
        json.dump(sessions, f)

# Remove session (when logout)
def remove_session(username):
    with open(SESSIONS_FILE, "r") as f:
        sessions = json.load(f)
    
    if username in sessions:
        del sessions[username]
    
    with open(SESSIONS_FILE, "w") as f:
        json.dump(sessions, f)

# --- SIMPLE PASSWORD HASHING (SECURITY) ---
def hash_password(password):
    """Converts password to a secure hash"""
    return hashlib.sha256(password.encode()).hexdigest()

# --- CHECK IF PASSWORD IS CORRECT ---
def login_user(username, password):
    """Check if username and password match"""
    with open(USERS_FILE, "r") as f:
        all_users = json.load(f)
    
    # Check if username exists
    if username not in all_users:
        return False
    
    # Check if password is correct
    stored_hash = all_users[username]
    entered_hash = hash_password(password)
    
    return stored_hash == entered_hash

# --- ADD NEW USER (ADMIN ONLY) ---
def add_new_user(username, password):
    """Add a new user to the database"""
    with open(USERS_FILE, "r") as f:
        all_users = json.load(f)
    
    # Check if username already exists
    if username in all_users:
        return False, "Username already exists!"
    
    # Add new user
    all_users[username] = hash_password(password)
    
    with open(USERS_FILE, "w") as f:
        json.dump(all_users, f)
    
    return True, "User created successfully!"

# --- INITIALIZE SESSION (REMEMBER LOGIN STATUS) ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None

# --- LOGIN PAGE ---
def show_login_page():
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown("# 🧮 The Molecular Man AI")
    st.markdown("### Login to Access")
    st.markdown("---")
    
    username = st.text_input("👤 Enter Username")
    password = st.text_input("🔐 Enter Password", type="password")
    
    if st.button("Login 🚀", use_container_width=True, type="primary"):
        if login_user(username, password):
            device_id = get_device_id()
            logged_elsewhere, old_device = is_user_logged_elsewhere(username, device_id)
            
            if logged_elsewhere:
                st.warning(f"⚠️ You were logged in on another device. That session is now closed.")
            
            # Close old session and start new one
            save_session(username, device_id)
            
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("✅ Login successful!")
            st.rerun()
        else:
            st.error("❌ Invalid username or password!")
    
    st.markdown("---")
    st.info("📌 Default login: username=**admin**, password=**admin**")
    st.markdown('</div>', unsafe_allow_html=True)

# --- MAIN APP (ONLY SHOWN AFTER LOGIN) ---
def show_main_app():
    # HEADER WITH LOGOUT BUTTON
    col1, col2, col3 = st.columns([1.2, 4, 1], gap="medium", vertical_alignment="center")
    
    with col1:
        try:
            st.image("logo.png", use_container_width=True) 
        except:
            st.write("🧮") 
    
    with col2:
        st.markdown("""
            <div style="text-align: left;">
                <div style="font-size: 42px; font-weight: bold; color: white; line-height: 1.2;">The Molecular Man</div>
                <div style="font-size: 18px; color: #e0e0e0; margin-bottom: 5px;">Expert Tuition Solutions Bot</div>
                <div style="font-size: 16px; color: white;">📞 +91 7339315376</div>
                <div style="font-size: 16px; color: white;">🌐 <a href="https://the-molecularman-expert-tuitions.streamlit.app/" target="_blank" style="color: #ffd700; text-decoration: none;">Visit Our Website</a></div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"<p style='color: #ffd700;'><b>👋 Hello, {st.session_state.username}!</b></p>", unsafe_allow_html=True)
        if st.button("Logout 🚪"):
            remove_session(st.session_state.username)
            st.session_state.logged_in = False
            st.session_state.username = None
            st.info("✅ You have been logged out!")
            st.rerun()
    
    st.markdown("---")
    st.title("Aya - Universal Problem Solver")
    st.caption("Paste any problem below (Algebra, Geometry, Physics, Chemistry, etc.)")
    
    # --- API CONFIGURATION ---
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
    except:
        st.error("⚠️ API Key missing! Add 'GOOGLE_API_KEY' to Streamlit Secrets.")
        return
    
    def get_working_model():
        try:
            available_models = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    available_models.append(m.name)
            
            preferences = ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro']
            for pref in preferences:
                if pref in available_models:
                    return genai.GenerativeModel(pref)
            
            if available_models:
                return genai.GenerativeModel(available_models[0])
        except:
            return genai.GenerativeModel('gemini-1.5-flash')
        return None
    
    def universal_solver(question_text):
        model = get_working_model()
        if not model: 
            return "Error: No AI models found."
        
        prompt = f"""
        You are an expert Math Tutor for 'The Molecular Man'. 
        Solve this problem step-by-step. Use LaTeX for math equations (enclose in $ signs).
        
        Format your response exactly like this:
        
        ### 🧠 Topic Identification
        (Name of the topic)
        
        ### 📊 Given Data
        (List variables)
        
        ### 📐 Formula & Logic
        (Formulas used)
        
        ### 📝 Step-by-Step Solution
        (Detailed steps)
        
        ### ✅ Final Answer
        (The final result)
        
        **Question:** "{question_text}"
        """
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"
    
    # --- INPUT SECTION ---
    user_question = st.text_area(
        "Problem Statement", 
        height=150, 
        placeholder="Enter your problem here..."
    )
    
    # --- SOLVE BUTTON ---
    if st.button("Solve Problem 🚀", type="primary", use_container_width=True):
        if not user_question.strip():
            st.warning("Please enter a question first.")
        else:
            with st.spinner("🤖 Analyzing..."):
                solution = universal_solver(user_question)
                
                st.markdown("---")
                st.markdown("## 💡 Detailed Solution")
                
                with st.container():
                    st.markdown('<div class="solution-box">', unsafe_allow_html=True)
                    st.markdown(solution)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                st.success("✅ Solved by Aya!")
    
    # --- FOOTER ---
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; color: #808080; padding: 20px;">
            <p>Developed by Mohammed Salmaan M | The Molecular Man Expert Tuition Solutions</p>
        </div>
    """, unsafe_allow_html=True)

# --- ADMIN PANEL (MANAGE USERS) - HIDDEN FROM USERS ---
def show_admin_panel():
    st.markdown("---")
    st.markdown("### 🔐 Admin Panel - Manage Users")
    st.info("⚠️ This panel is ONLY for the app owner/admin.")
    
    with st.expander("➕ Add New User"):
        # Ask for secret admin key to create users
        admin_secret = st.text_input("Enter Admin Secret Key", type="password", key="admin_secret_key")
        
        # Admin secret key set to: Ayasalmaan@9292
        REAL_ADMIN_SECRET = "Ayasalmaan@9292"
        
        if admin_secret == REAL_ADMIN_SECRET:
            st.success("✅ Admin verified!")
            
            new_username = st.text_input("New Username", key="new_user")
            new_password = st.text_input("New Password", type="password", key="new_pass")
            confirm_password = st.text_input("Confirm Password", type="password", key="confirm_pass")
            
            if st.button("Create User"):
                if not new_username or not new_password:
                    st.error("Please fill all fields")
                elif new_password != confirm_password:
                    st.error("Passwords don't match!")
                elif len(new_password) < 4:
                    st.error("Password must be at least 4 characters")
                else:
                    success, message = add_new_user(new_username, new_password)
                    if success:
                        st.success(f"✅ {message}")
                    else:
                        st.error(f"❌ {message}")
        elif admin_secret != "":
            st.error("❌ Invalid admin secret key!")
        else:
            st.warning("Enter the admin secret key to create users")

# --- MAIN FLOW ---
if st.session_state.logged_in:
    show_main_app()
    if st.session_state.username == "admin":
        show_admin_panel()
else:
    show_login_page()