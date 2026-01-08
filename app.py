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
import re

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
    </style>
""", unsafe_allow_html=True)

# --- INITIALIZE SESSION ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "device_id" not in st.session_state:
    st.session_state.device_id = str(uuid.uuid4())

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

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def login_user(username, password):
    with open(USERS_FILE, "r") as f:
        all_users = json.load(f)
    if username not in all_users:
        return False
    return all_users[username] == hash_password(password)

def is_user_logged_elsewhere(username, current_device_id):
    with open(SESSIONS_FILE, "r") as f:
        sessions = json.load(f)
    if username in sessions:
        if sessions[username] != current_device_id:
            return True
    return False

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

def add_new_user(username, password):
    with open(USERS_FILE, "r") as f:
        all_users = json.load(f)
    if username in all_users:
        return False, "Username already exists!"
    all_users[username] = hash_password(password)
    with open(USERS_FILE, "w") as f:
        json.dump(all_users, f)
    return True, "User created successfully!"

def remove_latex(text):
    """Remove LaTeX formatting"""
    text = text.replace('\\frac{', '(')
    text = text.replace('\\cdot', '*')
    text = text.replace('\\text{', '')
    text = text.replace('}{', '/')
    text = text.replace('\\', '')
    text = text.replace('[', '').replace(']', '')
    text = text.replace('{', '').replace('}', '')
    return text

def solve_problem(groq_client, question_text, file_obj=None, file_type=None):
    """Optimized solver using 512 tokens efficiently"""
    
    try:
        # Optimized prompt with international standards
        base_prompt = """You are Aya, an expert tutor from The Molecular Man Expert Tuition Solutions.

IMPORTANT: Use ONLY internationally recognized definitions and standards (ISO, IUPAC, IEC, etc.)

For the PROBLEM below, provide:
1) CONCEPT: Official definition (use international standard terms)
2) EXAMPLE: One real-life example  
3) SOLUTION: Step-by-step calculation/explanation
4) ANSWER: Clear final answer
5) TIP: Common mistake to avoid

Guidelines:
- Use official terminology (IUPAC for chemistry, SI units, etc.)
- Follow standard notation where applicable
- Reference recognized standards if relevant
- Be accurate and precise
- Use plain English primarily, but you MAY use standard symbols/units"""

        if file_type == "image" and file_obj:
            try:
                image = Image.open(file_obj)
                buffered = io.BytesIO()
                image.save(buffered, format="PNG")
                img_base64 = base64.standard_b64encode(buffered.getvalue()).decode("utf-8")
                
                prompt = base_prompt + "\n\nSOLVE THE PROBLEM IN THIS IMAGE:"
                
                # Try different models
                for model in ["llama-3.1-70b-versatile", "llama-3.1-8b-instant", "gemma-7b-it", "llama2-70b-4096"]:
                    try:
                        message = groq_client.chat.completions.create(
                            model=model,
                            messages=[{"role": "user", "content": prompt + f"\n{img_base64[:50]}..."}],
                            max_tokens=512,
                            temperature=0.7
                        )
                        break
                    except:
                        continue
            except Exception as e:
                return f"Error: {str(e)}"
        
        elif file_type == "pdf" and file_obj:
            try:
                import PyPDF2
                pdf_reader = PyPDF2.PdfReader(file_obj)
                pdf_text = ""
                for page_num in range(min(2, len(pdf_reader.pages))):
                    page = pdf_reader.pages[page_num]
                    pdf_text += page.extract_text()[:500]  # Limit text
                
                prompt = base_prompt + f"\n\nPROBLEM:\n{pdf_text}"
                
                # Try different models
                for model in ["llama-3.1-70b-versatile", "llama-3.1-8b-instant", "gemma-7b-it", "llama2-70b-4096"]:
                    try:
                        message = groq_client.chat.completions.create(
                            model=model,
                            messages=[{"role": "user", "content": prompt}],
                            max_tokens=512,
                            temperature=0.7
                        )
                        break
                    except:
                        continue
            except Exception as e:
                return f"Error: {str(e)}"
        
        else:
            prompt = base_prompt + f"\n\nPROBLEM:\n{question_text}"
            
            # Try different models
            for model in ["llama-3.1-70b-versatile", "llama-3.1-8b-instant", "gemma-7b-it", "llama2-70b-4096"]:
                try:
                    message = groq_client.chat.completions.create(
                        model=model,
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=512,
                        temperature=0.7
                    )
                    break
                except:
                    continue
        
        response_text = message.choices[0].message.content
        response_text = remove_latex(response_text)
        return response_text
    
    except Exception as e:
        return f"❌ Error: {str(e)}"

# --- LOGIN PAGE ---
def show_login_page():
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<div class="welcome-text">🧮</div>', unsafe_allow_html=True)
        st.markdown('<div style="text-align: center; color: #e0e0e0; font-size: 20px;">The Molecular Man AI</div>', unsafe_allow_html=True)
        st.markdown('<div style="text-align: center; color: #b0b0b0; font-size: 16px;">Aya - Universal Problem Solver</div>', unsafe_allow_html=True)
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
                    if is_user_logged_elsewhere(username, st.session_state.device_id):
                        st.info("⚠️ Previous session closed.")
                    save_session(username, st.session_state.device_id)
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
            
            if st.button("Create Account 🔑", use_container_width=True, type="primary"):
                if secret_key != "Ayasalmaan@9292":
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
    
    # --- API SETUP ---
    try:
        groq_api_key = st.secrets["GROQ_API_KEY"]
        groq_client = Groq(api_key=groq_api_key)
        st.caption("🔑 Using Groq API - Optimized for Quality")
    except KeyError:
        st.error("⚠️ GROQ_API_KEY not found in Streamlit Secrets!")
        st.info("Get key from: https://console.groq.com/keys")
        return
    except Exception as e:
        st.error(f"⚠️ Error: {str(e)}")
        return
    
    # --- INPUT ---
    st.markdown("### 📝 How to Solve?")
    input_type = st.radio("Choose input type:", ["📄 Text Problem", "🖼️ Upload Image", "📕 Upload PDF"], horizontal=True)
    
    user_question = None
    uploaded_file = None
    file_type = None
    
    if input_type == "📄 Text Problem":
        user_question = st.text_area("Problem Statement", height=150, placeholder="Enter your problem here...")
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
    
    # --- SOLVE ---
    if st.button("Solve Problem 🚀", type="primary", use_container_width=True):
        if input_type == "📄 Text Problem":
            if not user_question or not user_question.strip():
                st.warning("❌ Please enter a question first.")
            else:
                with st.spinner("🤖 Aya is busy doing work..."):
                    solution = solve_problem(groq_client, user_question)
                    st.markdown("---")
                    st.markdown("## 💡 Solution")
                    st.markdown(solution)
                    st.success("✅ Solved by Aya!")
        else:
            if uploaded_file is None:
                st.warning(f"❌ Please upload a {input_type.lower()} first.")
            else:
                with st.spinner(f"🤖 Aya is busy doing work..."):
                    solution = solve_problem(groq_client, None, uploaded_file, file_type)
                    st.markdown("---")
                    st.markdown("## 💡 Solution")
                    st.markdown(solution)
                    st.success("✅ Solved by Aya!")
    
    st.markdown("---")
    st.markdown("<div style='text-align: center; color: #808080; padding: 20px;'><p>Developed by Mohammed Salmaan M | The Molecular Man Expert Tuition Solutions</p></div>", unsafe_allow_html=True)

# --- MAIN FLOW ---
if st.session_state.logged_in:
    show_main_app()
else:
    show_login_page()
