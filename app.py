import streamlit as st
import google.generativeai as genai

# --- 1. PAGE CONFIGURATION & STYLING ---
st.set_page_config(
    page_title="The Molecular Man AI",
    page_icon="🧮",
    layout="wide"
)

# Custom CSS from your original app
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

# --- 2. HEADER SECTION (Fixed Alignment & Quality) ---
col1, col2 = st.columns([1.2, 5], gap="medium", vertical_alignment="center")

with col1:
    try:
        st.image("logo.png", use_container_width=True) 
    except:
        # Fallback if logo file is missing locally
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
st.title("Aya - The Molecular Man AI - Universal Problem Solver")
st.caption("Paste any statement problem below (Algebra, Geometry, Physics, Chemistry, etc.)")

# --- 3. AI LOGIC (SECURE BACKEND) ---
# This tries to get the key from Streamlit Secrets.
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    # This error shows only if you haven't set up the secrets yet
    st.error("⚠️ API Key missing! Please add 'GOOGLE_API_KEY' to your Streamlit Secrets.")
    st.stop() # Stops the app here so it doesn't crash further down

def get_working_model():
    """Auto-selects the best available AI model."""
    try:
        # Check available models to avoid 404 errors
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
        
        # Priority list (Newest to oldest)
        preferences = ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro']
        for pref in preferences:
            if pref in available_models:
                return genai.GenerativeModel(pref)
        
        # Fallback to whatever is available
        if available_models:
            return genai.GenerativeModel(available_models[0])
    except:
        # Ultimate fallback
        return genai.GenerativeModel('gemini-1.5-flash')
    return None

def universal_solver(question_text):
    model = get_working_model()
    if not model: return "Error: No AI models found."

    prompt = f"""
    You are an expert Math Tutor for 'The Molecular Man'. 
    Solve this problem step-by-step. Use LaTeX for math equations (enclose in $ signs).
    
    Format your response exactly like this:
    
    ### 🧐 Topic Identification
    (Name of the topic)

    ### 📊 Given Data if it is mathematics
    (List variables)

    ### 📐 Formula & Logic if it is mathematics
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
    placeholder="Enter anything you are Backed by Aya - The Molecular Man AI"
)

# --- 5. SOLVE BUTTON & OUTPUT (In White Box) ---
if st.button("Solve Problem 🚀", type="primary", use_container_width=True):
    if not user_question.strip():
        st.warning("Please enter a question first.")
    else:
        with st.spinner("🤖 Aya - The Molecular Man AI is analyzing..."):
            solution = universal_solver(user_question)
            
            st.markdown("---")
            st.markdown("## 💡 Detailed Solution")
            
            with st.container():
                st.markdown('<div class="solution-box">', unsafe_allow_html=True)
                st.markdown(solution)
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.success("✅ Solution by Aya -The Molecular Man AI")

# --- 6. FOOTER ---
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #808080; padding: 20px;">
        <p>Developed by Mohammed Salmaan M | The Molecular Man Expert Tuition Solutions</p>
    </div>
""", unsafe_allow_html=True)