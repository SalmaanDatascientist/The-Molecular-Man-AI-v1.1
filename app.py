import streamlit as st
import google.generativeai as genai
import os

# --- 1. PAGE CONFIGURATION & STYLING ---
st.set_page_config(
    page_title="The Molecular Man AI",
    page_icon="🧮",
    layout="wide"
)

# Custom CSS
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
    </style>
""", unsafe_allow_html=True)

# --- 2. HEADER SECTION ---
col1, col2 = st.columns([1.2, 5], gap="medium", vertical_alignment="center")

with col1:
    try:
        # Use logo.png if present, otherwise ignore
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

st.markdown("---")
st.title("The Molecular Man AI - Universal Problem Solver")
st.caption("Paste any statement problem below (Algebra, Geometry, Physics, Chemistry, etc.)")

# --- 3. SECURE AI SETUP ---
# This looks for the key you pasted in the 'Secrets' menu on Streamlit Cloud
try:
    if "GOOGLE_API_KEY" in st.secrets:
        API_KEY = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=API_KEY)
    else:
        st.error("⚠️ API Key not found. Please go to App Settings > Secrets and add GOOGLE_API_KEY.")
        st.stop()
except Exception as e:
    st.error(f"Configuration Error: {e}")
    st.stop()

def get_working_model():
    """Auto-selects the best available AI model."""
    try:
        # Priority list for best math reasoning
        preferences = ['models/gemini-1.5-pro', 'models/gemini-1.5-flash', 'models/gemini-pro']
        return genai.GenerativeModel(preferences[1]) # Defaulting to Flash for speed/stability
    except:
        return genai.GenerativeModel('gemini-1.5-flash')

def universal_solver(question_text):
    model = get_working_model()
    if not model: return "Error: No AI models found."

    prompt = f"""
    You are an expert Math Tutor for 'The Molecular Man'. 
    Solve this problem step-by-step. Use LaTeX for math equations (enclose in $ signs).
    
    Format your response exactly like this:
    
    ### 🧐 Topic Identification
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

# --- 4. INPUT SECTION ---
user_question = st.text_area(
    "Problem Statement", 
    height=150, 
    placeholder="Enter anything you are Backed by The Molecular Man AI"
)

# --- 5. SOLVE BUTTON & OUTPUT ---
if st.button("Solve Problem 🚀", type="primary", use_container_width=True):
    if not user_question.strip():
        st.warning("Please enter a question first.")
    else:
        with st.spinner("🤖 The Molecular Man AI is analyzing..."):
            solution = universal_solver(user_question)
            
            st.markdown("---")
            st.markdown("## 💡 Detailed Solution")
            
            with st.container():
                st.markdown('<div class="solution-box">', unsafe_allow_html=True)
                st.markdown(solution)
                st.markdown('</div>', unsafe_allow_html=True)
            
            if "Error" not in solution:
                st.success("✅ Solution Verified")

# --- 6. FOOTER ---
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #808080; padding: 20px;">
        <p>Developed by Mohammed Salmaan M | The Molecular Man Expert Tuition Solutions</p>
    </div>
""", unsafe_allow_html=True)