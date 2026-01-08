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
    .login-container {
        max-width: 500px;
        margin: 50px auto;
        padding: 50px;
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        border-radius: 15px;
        border: 3px solid #ffd700;
        box-shadow: 0 8px 32px rgba(255, 215, 0, 0.2);
    }
    .welcome-text {
        text-align: center;
        color: #ffd700;
        font-size: 48px;
        font-weight: bold;
        margin-bottom: 20px;
        animation: glow 2s ease-in-out infinite;
    }
    @keyframes glow {
        0%, 100% { text-shadow: 0 0 10px #ffd700; }
        50% { text-shadow: 0 0 20px #ffd700, 0 0 30px #ffd700; }
    }
    .subtitle {
        text-align: center;
        color: #e0e0e0;
        font-size: 20px;
        margin-bottom: 10px;
    }
    .tagline {
        text-align: center;
        color: #b0b0b0;
        font-size: 16px;
        margin-bottom: 40px;
        font-style: italic;
    }
    </style>
""", unsafe_allow_html=True)

# --- INITIALIZE SESSION STATE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "device_id" not in st.session_state:
    st.session_state.device_id = str(uuid.uuid4())

# --- FILE STORAGE ---
USERS_FILE = "users_database.json"
SESSIONS_FILE = "active_sessions.json"

def create_empty_database():
    if not os.path.exists(USERS_FILE):
        # Create with default admin user
        default_user = {
            "Mohammed": hash_password("Molsalmaan@9292")
        }
        with open(USERS_FILE, "w") as f:
            json.dump(default_user, f)

def create_empty_sessions():
    if not os.path.exists(SESSIONS_FILE):
        with open(SESSIONS_FILE, "w") as f:
            json.dump({}, f)

create_empty_database()
create_empty_sessions()

# --- PASSWORD HASHING ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# --- LOGIN CHECK ---
def login_user(username, password):
    with open(USERS_FILE, "r") as f:
        all_users = json.load(f)
    
    if username not in all_users:
        return False
    
    stored_hash = all_users[username]
    entered_hash = hash_password(password)
    
    return stored_hash == entered_hash

# --- DEVICE LOCK FUNCTIONS ---
def is_user_logged_elsewhere(username, current_device_id):
    with open(SESSIONS_FILE, "r") as f:
        sessions = json.load(f)
    
    if username in sessions:
        old_device_id = sessions[username]
        if old_device_id != current_device_id:
            return True, old_device_id
    return False, None

def save_session(username, device_id):
    with open(SESSIONS_FILE, "r") as f:
        sessions = json.load(f)
    
    sessions[username] = device_id
    
    with open(SESSIONS_FILE, "w") as f:
        json.dump(sessions, f)

def remove_session(username):
    with open(SESSIONS_FILE, "r") as f:
        sessions = json.load(f)
    
    if username in sessions:
        del sessions[username]
    
    with open(SESSIONS_FILE, "w") as f:
        json.dump(sessions, f)

# --- ADD NEW USER ---
def add_new_user(username, password):
    with open(USERS_FILE, "r") as f:
        all_users = json.load(f)
    
    if username in all_users:
        return False, "Username already exists!"
    
    all_users[username] = hash_password(password)
    
    with open(USERS_FILE, "w") as f:
        json.dump(all_users, f)
    
    return True, "User created successfully!"

# --- LOGIN PAGE ---
def show_login_page():
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        # Welcome banner
        st.markdown('<div class="welcome-text">🧮</div>', unsafe_allow_html=True)
        st.markdown('<div class="subtitle">The Molecular Man AI</div>', unsafe_allow_html=True)
        st.markdown('<div class="subtitle">Aya - Universal Problem Solver</div>', unsafe_allow_html=True)
        st.markdown('<div class="tagline">"Hello! I\'m Aya. To access my expert tuition solutions, please authenticate first."</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Login form
        tab1, tab2 = st.tabs(["🔓 Login", "🆕 Create Account"])
        
        with tab1:
            st.markdown("### Access Your Account")
            username = st.text_input("👤 Username", key="login_user")
            password = st.text_input("🔐 Password", type="password", key="login_pass")
            
            if st.button("Login 🚀", use_container_width=True, type="primary"):
                if not username or not password:
                    st.error("❌ Please enter both username and password")
                elif login_user(username, password):
                    device_id = st.session_state.device_id
                    logged_elsewhere, old_device = is_user_logged_elsewhere(username, device_id)
                    
                    if logged_elsewhere:
                        st.info("⚠️ Your previous session has been closed.")
                    
                    save_session(username, device_id)
                    
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success("✅ Welcome to Aya!")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
        
        with tab2:
            st.markdown("### Create New Account")
            st.info("📌 Ask your admin for the secret key to create an account")
            
            secret_key = st.text_input("🔑 Admin Secret Key", type="password", key="create_secret")
            new_username = st.text_input("👤 New Username", key="create_user")
            new_password = st.text_input("🔐 New Password", type="password", key="create_pass")
            confirm_password = st.text_input("🔐 Confirm Password", type="password", key="confirm_pass")
            
            ADMIN_SECRET = "Ayasalmaan@9292"
            
            if st.button("Create Account 🔑", use_container_width=True, type="primary"):
                if secret_key != ADMIN_SECRET:
                    st.error("❌ Invalid admin secret key")
                elif not new_username or not new_password:
                    st.error("❌ Please fill all fields")
                elif new_password != confirm_password:
                    st.error("❌ Passwords don't match")
                elif len(new_password) < 4:
                    st.error("❌ Password must be at least 4 characters")
                else:
                    success, message = add_new_user(new_username, new_password)
                    if success:
                        st.success(f"✅ {message} Now you can login!")
                    else:
                        st.error(f"❌ {message}")
        
        st.markdown('</div>', unsafe_allow_html=True)

# --- MAIN APP ---
def show_main_app():
    # HEADER WITH LOGOUT
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
        if st.button("Logout 🚪", use_container_width=True):
            remove_session(st.session_state.username)
            st.session_state.logged_in = False
            st.session_state.username = None
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
    
    def universal_solver(question_text=None, file_obj=None, file_type=None):
        model = get_working_model()
        if not model: 
            return "Error: No AI models found."
        
        if file_obj is not None:
            # File-based problem (Image, PDF, or Video)
            
            if file_type == "image":
                # Image file
                from PIL import Image
                image = Image.open(file_obj)
                
                prompt = """You are an expert Math Tutor for 'The Molecular Man'. 
                Look at this image carefully and solve the problem shown in it step-by-step. 
                Use LaTeX for math equations (enclose in $ signs).
                
                Format your response exactly like this:
                
                ### 🧠 Topic Identification
                (Name of the topic)
                
                ### 📊 Given Data
                (List variables/information from the image)
                
                ### 📐 Formula & Logic
                (Formulas used)
                
                ### 📝 Step-by-Step Solution
                (Detailed steps)
                
                ### ✅ Final Answer
                (The final result)
                """
                
                try:
                    response = model.generate_content([prompt, image])
                    return response.text
                except Exception as e:
                    return f"Error processing image: {str(e)}"
            
            elif file_type == "pdf":
                # PDF file
                import PyPDF2
                
                try:
                    pdf_reader = PyPDF2.PdfReader(file_obj)
                    pdf_text = ""
                    
                    for page_num in range(len(pdf_reader.pages)):
                        page = pdf_reader.pages[page_num]
                        pdf_text += f"\n--- Page {page_num + 1} ---\n"
                        pdf_text += page.extract_text()
                    
                    prompt = f"""You are an expert Math Tutor for 'The Molecular Man'. 
                    Analyze this PDF content and solve the problems step-by-step. 
                    Use LaTeX for math equations (enclose in $ signs).
                    
                    Format your response exactly like this:
                    
                    ### 🧠 Topic Identification
                    (Name of the topic)
                    
                    ### 📊 Given Data
                    (List variables/information from PDF)
                    
                    ### 📐 Formula & Logic
                    (Formulas used)
                    
                    ### 📝 Step-by-Step Solution
                    (Detailed steps)
                    
                    ### ✅ Final Answer
                    (The final result)
                    
                    **PDF Content:**
                    {pdf_text}
                    """
                    
                    response = model.generate_content(prompt)
                    return response.text
                except Exception as e:
                    return f"Error processing PDF: {str(e)}"
            
            elif file_type == "video":
                # Video file
                import cv2
                import numpy as np
                from PIL import Image as PILImage
                
                try:
                    # Read video and extract frames
                    video = cv2.VideoCapture(file_obj)
                    frames = []
                    frame_count = 0
                    
                    while len(frames) < 5:  # Extract up to 5 key frames
                        ret, frame = video.read()
                        if not ret:
                            break
                        
                        if frame_count % max(1, int(video.get(cv2.CAP_PROP_FRAME_COUNT)) // 5) == 0:
                            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            frames.append(PILImage.fromarray(frame_rgb))
                        
                        frame_count += 1
                    
                    video.release()
                    
                    if not frames:
                        return "Error: Could not extract frames from video"
                    
                    prompt = """You are an expert Math Tutor for 'The Molecular Man'. 
                    Look at these video frames and analyze the problem or content shown. 
                    Solve any problems step-by-step. Use LaTeX for math equations (enclose in $ signs).
                    
                    Format your response exactly like this:
                    
                    ### 🧠 Topic Identification
                    (Name of the topic)
                    
                    ### 📊 Given Data
                    (List variables/information from video frames)
                    
                    ### 📐 Formula & Logic
                    (Formulas used)
                    
                    ### 📝 Step-by-Step Solution
                    (Detailed steps)
                    
                    ### ✅ Final Answer
                    (The final result)
                    """
                    
                    # Send prompt with multiple frames
                    content = [prompt] + frames
                    response = model.generate_content(content)
                    return response.text
                
                except Exception as e:
                    return f"Error processing video: {str(e)}"
        
        else:
            # Text-based problem
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
    st.markdown("### 📝 How to Solve?")
    
    input_type = st.radio(
        "Choose input type:", 
        ["📄 Text Problem", "🖼️ Upload Image", "📕 Upload PDF", "🎥 Upload Video"], 
        horizontal=True
    )
    
    user_question = None
    uploaded_file = None
    file_type = None
    
    if input_type == "📄 Text Problem":
        user_question = st.text_area(
            "Problem Statement", 
            height=150, 
            placeholder="Enter your problem here..."
        )
    
    elif input_type == "🖼️ Upload Image":
        uploaded_file = st.file_uploader("Upload a problem image", type=["jpg", "jpeg", "png", "gif", "bmp"])
        if uploaded_file:
            st.image(uploaded_file, caption="Uploaded Problem", use_container_width=True)
            file_type = "image"
    
    elif input_type == "📕 Upload PDF":
        uploaded_file = st.file_uploader("Upload a PDF with problems", type=["pdf"])
        if uploaded_file:
            st.info(f"📄 PDF Uploaded: {uploaded_file.name}")
            file_type = "pdf"
    
    elif input_type == "🎥 Upload Video":
        uploaded_file = st.file_uploader("Upload a video with problems", type=["mp4", "avi", "mov", "mkv", "flv", "wmv"])
        if uploaded_file:
            st.info(f"🎥 Video Uploaded: {uploaded_file.name}")
            file_type = "video"
            # Show video preview
            st.video(uploaded_file)
    
    # --- SOLVE BUTTON ---
    if st.button("Solve Problem 🚀", type="primary", use_container_width=True):
        if input_type == "📄 Text Problem":
            if not user_question or not user_question.strip():
                st.warning("❌ Please enter a question first.")
            else:
                with st.spinner("🤖 Aya is analyzing..."):
                    solution = universal_solver(question_text=user_question)
                    
                    st.markdown("---")
                    st.markdown("## 💡 Detailed Solution")
                    
                    with st.container():
                        st.markdown('<div class="solution-box">', unsafe_allow_html=True)
                        st.markdown(solution)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.success("✅ Solved by Aya!")
        else:
            if uploaded_file is None:
                st.warning(f"❌ Please upload a {input_type.lower()} first.")
            else:
                with st.spinner(f"🤖 Aya is analyzing the {file_type}..."):
                    solution = universal_solver(file_obj=uploaded_file, file_type=file_type)
                    
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

# --- MAIN FLOW ---
if st.session_state.logged_in:
    show_main_app()
else:
    show_login_page()