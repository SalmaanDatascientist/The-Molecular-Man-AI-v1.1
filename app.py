import streamlit as st
from groq import Groq
import json
import hashlib
from datetime import datetime
import uuid
import os
from PIL import Image
import base64
import io

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
        default_user = {
            "Mohammed": hashlib.sha256("Molsalmaan@9292".encode()).hexdigest()
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
        
        st.markdown('<div class="welcome-text">🧮</div>', unsafe_allow_html=True)
        st.markdown('<div class="subtitle">The Molecular Man AI</div>', unsafe_allow_html=True)
        st.markdown('<div class="subtitle">Aya - Universal Problem Solver</div>', unsafe_allow_html=True)
        st.markdown('<div class="tagline">"Hello! I\'m Aya. To access my expert tuition solutions, please authenticate first."</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
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
    
    # --- GROQ API CONFIGURATION ---
    try:
        groq_api_key = st.secrets["GROQ_API_KEY"]
        client = Groq(api_key=groq_api_key)
        
        # Auto-detect available models
        available_models = []
        try:
            models = client.models.list()
            available_models = [m.id for m in models.data]
        except:
            available_models = []
        
        # Try to find a working model
        model_to_use = None
        preferred_models = ["llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768", "gemma-7b-it"]
        
        for model in preferred_models:
            if model in available_models:
                model_to_use = model
                break
        
        if not model_to_use and available_models:
            model_to_use = available_models[0]
        
        if not model_to_use:
            model_to_use = "llama3-8b-8192"
        
        st.caption(f"🔑 Using Groq API - Model: {model_to_use} ♾️")
        
    except KeyError:
        st.error("⚠️ GROQ_API_KEY not found in Streamlit Secrets!")
        st.info("📌 Steps to fix:")
        st.info("1. Go to your Streamlit app → Click 'Manage app' (bottom right)")
        st.info("2. Click 'Secrets'")
        st.info("3. Add: GROQ_API_KEY = \"your_key_here\"")
        st.info("4. Get your key from: https://console.groq.com/keys")
        return
    except Exception as e:
        st.error(f"⚠️ Error: {str(e)}")
        return
    
    def universal_solver(question_text=None, file_obj=None, file_type=None):
        
        if file_obj is not None:
            # File-based problem
            
            if file_type == "image":
                try:
                    image = Image.open(file_obj)
                    buffered = io.BytesIO()
                    image.save(buffered, format="PNG")
                    img_base64 = base64.standard_b64encode(buffered.getvalue()).decode("utf-8")
                    
                    prompt = """You are 'Aya', an expert and extremely patient Math Tutor from 'The Molecular Man Expert Tuition Solutions'. 
                    You are teaching a student who finds this topic difficult, so explain everything in the SIMPLEST way possible.
                    
                    IMPORTANT INSTRUCTIONS:
                    - Assume the student knows NOTHING about this topic
                    - Use real-life examples and analogies that a 5-year-old can understand
                    - Break down EVERY step into micro-steps
                    - Explain WHY we do each step, not just HOW
                    - Use simple words, avoid jargon
                    - If you must use a technical term, explain it first
                    - Include visual descriptions (draw with words)
                    - Use analogies from daily life
                    - Give multiple examples (at least 3)
                    
                    Format your response EXACTLY like this:
                    
                    ### 🧠 What Is This Topic? (Easy Explanation)
                    Explain what this topic is about in the simplest way. Use an analogy from real life.
                    Example: "Algebra is like a mystery game where X is the secret number we need to find..."
                    
                    ### 📊 What Do We Know? (The Given Information)
                    List each piece of information given in the problem in simple language.
                    
                    ### 🔑 Key Concepts You Need To Know
                    Explain 2-3 fundamental concepts needed to solve this problem.
                    Use analogies and real-life examples for each.
                    
                    ### 📐 The Formula/Rule/Method (With Explanation)
                    Explain the formula or method in simple words.
                    Then explain WHY this formula works (use analogy).
                    
                    ### 📝 Step-By-Step Solution (Ultra Detailed)
                    **Step 1:** [Action] → [Why we do this] → [Simple explanation]
                    **Step 2:** [Action] → [Why we do this] → [Simple explanation]
                    **Step 3:** [Action] → [Why we do this] → [Simple explanation]
                    Continue for each step...
                    
                    ### 💡 Why This Answer Makes Sense (Validation)
                    Explain why the answer is reasonable. Check if it makes sense in real life.
                    
                    ### ✅ Final Answer
                    State the answer clearly.
                    
                    ### 🎯 Similar Problems To Practice
                    Give 2-3 similar problems the student can try to practice this concept.
                    
                    ### 🧠 Common Mistakes Students Make
                    List 2-3 mistakes students often make and how to avoid them.
                    
                    Now solve this problem with the image shown. Remember: SIMPLE, DETAILED, WITH EXAMPLES!"""
                    
                    message = client.chat.completions.create(
                        model=model_to_use,
                        messages=[
                            {"role": "user", "content": prompt + f"\n\nImage (base64): {img_base64}"}
                        ],
                        max_tokens=1000,
                    )
                    return message.choices[0].message.content
                except Exception as e:
                    return f"Error processing image: {str(e)}"
            
            elif file_type == "pdf":
                try:
                    import PyPDF2
                    pdf_reader = PyPDF2.PdfReader(file_obj)
                    pdf_text = ""
                    
                    for page_num in range(len(pdf_reader.pages)):
                        page = pdf_reader.pages[page_num]
                        pdf_text += f"\n--- Page {page_num + 1} ---\n"
                        pdf_text += page.extract_text()
                    
                    prompt = f"""You are 'Aya', an expert and extremely patient Math Tutor from 'The Molecular Man Expert Tuition Solutions'. 
                    You are teaching a student who finds this topic difficult, so explain everything in the SIMPLEST way possible.
                    
                    IMPORTANT INSTRUCTIONS:
                    - Assume the student knows NOTHING about this topic
                    - Use real-life examples and analogies that a 5-year-old can understand
                    - Break down EVERY step into micro-steps
                    - Explain WHY we do each step, not just HOW
                    - Use simple words, avoid jargon
                    - If you must use a technical term, explain it first
                    - Include visual descriptions (draw with words)
                    - Use analogies from daily life
                    - Give multiple examples (at least 3)
                    
                    Format your response EXACTLY like this:
                    
                    ### 🧠 What Is This Topic? (Easy Explanation)
                    Explain what this topic is about in the simplest way. Use an analogy from real life.
                    Example: "Algebra is like a mystery game where X is the secret number we need to find..."
                    
                    ### 📊 What Do We Know? (The Given Information)
                    List each piece of information given in the problem in simple language.
                    
                    ### 🔑 Key Concepts You Need To Know
                    Explain 2-3 fundamental concepts needed to solve this problem.
                    Use analogies and real-life examples for each.
                    
                    ### 📐 The Formula/Rule/Method (With Explanation)
                    Explain the formula or method in simple words.
                    Then explain WHY this formula works (use analogy).
                    
                    ### 📝 Step-By-Step Solution (Ultra Detailed)
                    **Step 1:** [Action] → [Why we do this] → [Simple explanation]
                    **Step 2:** [Action] → [Why we do this] → [Simple explanation]
                    **Step 3:** [Action] → [Why we do this] → [Simple explanation]
                    Continue for each step...
                    
                    ### 💡 Why This Answer Makes Sense (Validation)
                    Explain why the answer is reasonable. Check if it makes sense in real life.
                    
                    ### ✅ Final Answer
                    State the answer clearly.
                    
                    ### 🎯 Similar Problems To Practice
                    Give 2-3 similar problems the student can try to practice this concept.
                    
                    ### 🧠 Common Mistakes Students Make
                    List 2-3 mistakes students often make and how to avoid them.
                    
                    Now analyze this PDF and solve ALL problems in it. Remember: SIMPLE, DETAILED, WITH EXAMPLES!"""
                    
                    message = client.chat.completions.create(
                        model=model_to_use,
                        messages=[
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=1000,
                    )
                    return message.choices[0].message.content
                except Exception as e:
                    return f"Error processing PDF: {str(e)}"
            
            elif file_type == "video":
                return "⚠️ Video analysis not available with Groq. Please upload an image of the problem instead."
        
        else:
            # Text-based problem
            prompt = f"""You are an expert Math Tutor for 'The Molecular Man'. 
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
                message = client.chat.completions.create(
                    model=model_to_use,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1000,
                )
                return message.choices[0].message.content
            except Exception as e:
                return f"Error: {str(e)}"
    
    # --- INPUT SECTION ---
    st.markdown("### 📝 How to Solve?")
    
    input_type = st.radio(
        "Choose input type:", 
        ["📄 Text Problem", "🖼️ Upload Image", "📕 Upload PDF"], 
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
    
    # --- SOLVE BUTTON ---
    if st.button("Solve Problem 🚀", type="primary", use_container_width=True):
        if input_type == "📄 Text Problem":
            if not user_question or not user_question.strip():
                st.warning("❌ Please enter a question first.")
            else:
                with st.spinner("🤖 Aya is busy doing work..."):
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
                with st.spinner(f"🤖 Aya is busy doing work..."):
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
