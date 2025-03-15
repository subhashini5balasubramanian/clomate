import streamlit as st
import random
import time
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import google.generativeai as genai
import requests
import os
from dotenv import load_dotenv

# --- Load API Keys ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# --- Streamlit Config ---
st.set_page_config(page_title="🌩 AI Cloud Optimizer", layout="wide")

# --- Session State Initialization ---
if "page" not in st.session_state:
    st.session_state.page = "login"
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()
if "active_servers" not in st.session_state:
    st.session_state.active_servers = 2  # Start with 2 servers
if "mock_data" not in st.session_state:
    st.session_state.mock_data = {
        "CPU Utilization": 50,
        "Storage Used": 500,
        "API Calls": 25000,
        "Monthly Cost": 200,
    }
if "selected_api" not in st.session_state:
    st.session_state.selected_api = "None"

# --- Mock Data with Auto-Scaling ---
def fetch_mock_data():
    if time.time() - st.session_state.last_refresh > 10:
        st.session_state.last_refresh = time.time()

        st.session_state.mock_data = {
            "CPU Utilization": random.randint(10, 90),
            "Storage Used": random.randint(100, 1000),
            "API Calls": random.randint(1000, 50000),
            "Monthly Cost": random.randint(50, 500),
        }

        # Simulate Auto-Scaling: Increase/Decrease Servers
        if st.session_state.mock_data["CPU Utilization"] > 80 or st.session_state.mock_data["API Calls"] > 50000:
            st.session_state.active_servers += 1  # Scale Up
            send_telegram_alert(f"🚀 Scaling Up! New Server Count: {st.session_state.active_servers}")
        elif st.session_state.mock_data["CPU Utilization"] < 30 and st.session_state.mock_data["API Calls"] < 5000 and st.session_state.active_servers > 1:
            st.session_state.active_servers -= 1  # Scale Down
            send_telegram_alert(f"🛑 Scaling Down! New Server Count: {st.session_state.active_servers}")

    return st.session_state.mock_data

# --- AI Cost Prediction ---
def ai_cost_prediction(usage_data):
    past_data = pd.DataFrame({
        "Days": np.arange(1, 31),
        "CPU_Usage": np.random.randint(20, 90, size=30),
        "API_Calls": np.random.randint(5000, 50000, size=30),
        "Storage_Used": np.random.randint(100, 1000, size=30),
        "Cost": np.linspace(50, 500, num=30) + np.random.normal(0, 15, size=30)
    })

    past_data["Cost_MA"] = past_data["Cost"].rolling(5, min_periods=1).mean()

    X = past_data[["Days", "CPU_Usage", "API_Calls", "Storage_Used", "Cost_MA"]]
    y = past_data["Cost"]

    model = LinearRegression()
    model.fit(X, y)

    future_data = np.array([[45, usage_data.get("CPU Utilization", 50), usage_data.get("API Calls", 25000), usage_data.get("Storage Used", 500), past_data["Cost_MA"].iloc[-1]]])
    return round(model.predict(future_data)[0], 2)

# --- AI Recommendations ---
def ai_recommendations(usage_data):
    prompt = f"""
    Given this cloud usage:
    - CPU: {usage_data['CPU Utilization']}%
    - API Calls: {usage_data['API Calls']}
    - Storage: {usage_data['Storage Used']}GB
    - Cost: ${usage_data['Monthly Cost']}

    Suggest ONLY precise cost-saving actions.

    Example:  
    ✅ Reduce API Calls (Batching, Caching)  
    ✅ Optimize Compute (Downsize VM, Auto-scale)  
    ✅ Switch to Cheaper Storage (S3, Glacier)  
    ✅ Use Free-Tier APIs (AWS, Firebase, Supabase)
    """

    model = genai.GenerativeModel("gemini-1.5-pro")
    return model.generate_content(prompt).text.strip()

# --- Telegram Alert System ---
def send_telegram_alert(message):
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        requests.post(url, data=data)

# --- Login Page ---
def login_page():
    st.title("🔐 User Login / Registration")

    option = st.radio("Login or Register:", ["Login", "Register"])
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if option == "Login" and st.button("Login"):
        if email and password:
            st.success("✅ Login Successful!")
            st.session_state.page = "role_selection"
            st.session_state.user = email
            st.rerun()
        else:
            st.error("❌ Please enter email and password.")

# --- Role Selection Page ---
def role_selection_page():
    st.title("Select Your Role")
    role = st.radio("Are you a Company or a Developer?", ["Company", "Developer"])

    if st.button("Continue"):
        st.session_state.page = "dashboard"
        st.session_state.role = role
        st.rerun()

# --- Dashboard Page ---
def dashboard_page():
    st.title("📊 AI Cloud Optimizer Dashboard")
    st.subheader(f"Welcome, {st.session_state.role}!")

    st.session_state.selected_api = st.selectbox("🔍 Select Project API Usage", ["None", "AWS", "Azure", "Google Cloud", "Other"])

    # --- Fetch & Display Mock Data ---
    usage_data = fetch_mock_data()
    st.write("📊 Live Cloud Usage:", usage_data)

    # --- Display Active Servers (Auto-Scaling) ---
    st.write(f"🖥 Active Servers: {st.session_state.active_servers}")

    # --- AI Cost Prediction ---
    predicted_cost = ai_cost_prediction(usage_data)
    st.write(f"📈 AI Predicted Cost: ${predicted_cost}")

    # --- AI Recommendations ---
    ai_suggestions = ai_recommendations(usage_data)
    st.write("🤖 AI Cost Optimization:", ai_suggestions)

    if st.session_state.role == "Developer":
        st.write("👨‍💻 *Credits:* Developed by [Your Name]")

# --- Run the App ---
if _name_ == "_main_":
    if st.session_state.page == "login":
        login_page()
    elif st.session_state.page == "role_selection":
        role_selection_page()
    elif st.session_state.page == "dashboard":
        dashboard_page()