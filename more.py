import streamlit as st
import pandas as pd
import pickle
import os
from auth import register_user, check_login  
from pathlib import Path

# DIAGNOSTIC CODE: This will print exactly what is happening in your terminal
print("\n")
print("🔍 STREAMLIT RUNTIME DIAGNOSTIC")
base_path = Path(__file__).resolve().parent
print(f"📂 Folder Streamlit is looking inside: {base_path}")
print(f"📄 Exact files sitting inside this folder: {os.listdir(base_path)}")
print("\n")

# 1. Page Configuration & Styling
st.set_page_config(page_title="Maize Yield Predictor", page_icon="🌾", layout="centered")

# Initialize session state variables for login memory if they don't exist
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""


# 🌍 Regional Baseline Environmental Database (from ISRIC / FAO profiles)
STATE_DB = {
    "Enugu State": {
        "clay": 0.15, "sand": 0.10, "ph": 5.2, "nitrogen": 1.4, "potassium": 0.12, "phosphorus": 4.0
    },
    "Kaduna State": {
        "clay": 0.14, "sand": 0.08, "ph": 6.1, "nitrogen": 1.1, "potassium": 0.16, "phosphorus": 5.2
    },
    "Kano State": {
        "clay": 0.09, "sand": 0.05, "ph": 6.5, "nitrogen": 0.7, "potassium": 0.20, "phosphorus": 6.0
    },
    "Oyo State": {
        "clay": 0.16, "sand": 0.11, "ph": 5.8, "nitrogen": 1.2, "potassium": 0.14, "phosphorus": 4.5
    },
    "Niger State": {
        "clay": 0.13, "sand": 0.08, "ph": 5.9, "nitrogen": 0.9, "potassium": 0.18, "phosphorus": 5.5
    }
}


# 🔐 AUTHENTICATION INTERFACE (IF NOT LOGGED IN)
if not st.session_state.logged_in:
    st.title("🌾 Welcome to AgroYield Nigeria")
    st.markdown("Please log in or register a new account to access the predictive modeling engine.")
    
    # Create tabs for Login and Registration
    tab1, tab2 = st.tabs(["🔒 User Login", "📝 New Account Registration"])
    
    with tab1:
        st.subheader("Login to Your Dashboard")
        login_user = st.text_input("Username", key="login_user_input").strip()
        login_pass = st.text_input("Password", type="password", key="login_pass_input")
        
        if st.button("Log In", type="primary"):
            if login_user == "" or login_pass == "":
                st.error("Please fill out all fields.")
            elif check_login(login_user, login_pass):
                st.session_state.logged_in = True
                st.session_state.username = login_user
                st.success("Login successful!")
                st.rerun()  # Instantly reloads page to show your ML dashboard
            else:
                st.error("❌ Invalid Username or Password.")
                
    with tab2:
        st.subheader("Create a Free Developer Account")
        reg_user = st.text_input("Choose Username", key="reg_user_input").strip()
        reg_pass = st.text_input("Choose Password", type="password", key="reg_pass_input")
        reg_pass_confirm = st.text_input("Confirm Password", type="password", key="reg_pass_confirm_input")
        
        if st.button("Register Account"):
            if reg_user == "" or reg_pass == "":
                st.error("Fields cannot be left blank.")
            elif reg_pass != reg_pass_confirm:
                st.error("⚠️ Passwords do not match!")
            elif len(reg_pass) < 4:
                st.error("⚠️ Password must be at least 4 characters long.")
            else:
                success, message = register_user(reg_user, reg_pass)
                if success:
                    st.success(message)
                else:
                    st.error(message)

# 🌾 MAIN PREDICTIVE SYSTEM (IF LOGGED IN)
else:
    # Sidebar layout for user profile control
    with st.sidebar:
        st.write(f"👤 Logged in as: **{st.session_state.username}**")
        if st.button("🚪 Log Out", type="secondary"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()

    st.title("🌾 Nigeria AgroYield Predictive Engine")
    st.markdown(f"Welcome back, **{st.session_state.username}**. Run parallel forecasts below.")
    st.markdown("---")

    # Automatically locate and load the models safely
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    rf_path = os.path.join(BASE_DIR, "maize_rf_model.pkl")
    gb_path = os.path.join(BASE_DIR, "maize_gb_model.pkl")

    @st.cache_resource 
    def load_models():
        if not os.path.exists(rf_path) or not os.path.exists(gb_path):
            st.error("⚠️ Model files (.pkl) not found in the script folder!")
            return None, None
        with open(rf_path, 'rb') as f:
            rf = pickle.load(f)
        with open(gb_path, 'rb') as f:
            gb = pickle.load(f)
        return rf, gb

    rf_model, gb_model = load_models()

    if rf_model and gb_model:
        # Your form inputs
        st.subheader("1. Temporal & Macro Context")
        col1, col2 = st.columns(2)
        with col1:
            year = st.number_input("Target Prediction Year", min_value=1990, max_value=2050, value=2026)
        with col2:
            disaster = st.selectbox("Disaster/Shock Occurred?", options=[0, 1], format_func=lambda x: "Yes" if x == 1 else "No")

        st.subheader("2. Climate and Weather Metrics")
        col3, col4 = st.columns(2)
        with col3:
            ann_rain = st.number_input("Annual Average Rainfall (mm)", value=1200.0)
            lag_rain_1 = st.number_input("Lagged Rainfall Year-1 (mm)", value=1150.0)
            lag_climate_2 = st.number_input("Lagged Climate Indicator Year-2", value=1200.0)
        with col4:
            growing_temp = st.number_input("Growing Season Avg Temp (°C)", value=26.0)
            veg_temp = st.number_input("Vegetative Phase Avg Temp (°C)", value=26.5)
            rep_temp = st.number_input("Reproductive Phase Avg Temp (°C)", value=25.0)

        st.subheader("3. Soil Profile Variables")
        col5, col6 = st.columns(2)
        with col5:
            soil_n = st.number_input("Soil Nitrogen Baseline (g/kg)", value=0.9)
            soil_ph = st.number_input("Soil pH Level", value=5.9)
            clay = st.number_input("AWC Clay Soil Ratio", value=0.13)
        with col6:
            sand = st.number_input("AWC Sandy Soil Ratio", value=0.08)
            potassium = st.number_input("Soil Potassium content (k)", value=0.18)
            phosphorus = st.number_input("Soil Phosphorus content (mg/kg)", value=5.5)
        st.subheader("4. Temporal, Scale & Management Context")
        col7, col8, col9 = st.columns(3)
        with col7:
            Area = st.number_input("Cultivated Area (Hectares)", min_value=0.1, max_value=1000.0, value=1.5)
        # Month Pickers
            Planting_month = st.selectbox("Planting_month", options=list(range(1, 13)), format_func=lambda x: pd.to_datetime(x, format='%m').strftime('%B'))
        with col8:
            Harvest_month = st.selectbox("Expected_Harvest month", options=list(range(1, 13)), format_func=lambda x: pd.to_datetime(x, format='%m').strftime('%B'))
        with col9:
            selected_state = st.selectbox("Select Target State", options=list(STATE_DB.keys()))
            
            # Fetch the baseline dictionary for the selected region
            state_defaults = STATE_DB[selected_state]
        FEATURE_COLUMNS = [
            'Year', 'Disaster_occur', 'Planting_month',
            'Harvest_month','Area', 'Avg_rainfall_annually',
            'Annual_Lagged_rainfall_1', 'Annual_Lagged_climate_2', 
            'Awc_Clay_soil', 'Awc_Sandy_soil', 'Soil_ph', 
            'Soil_Nitrogen(g/kg)', 'Soil_potassium(k)', 'Soil_phophorus(mg/kg)', 
            'Veg_Avg_Temp', 'Rep_Avg_Temp', 'Growing_Season_Avg_Temp'
        ]

        input_data = {
            'Year': year, 'Disaster_occur': disaster, 'Avg_rainfall_annually': ann_rain,
            'Annual_Lagged_rainfall_1': lag_rain_1, 'Annual_Lagged_climate_2': lag_climate_2,
            'Awc_Clay_soil': clay, 'Awc_Sandy_soil': sand, 'Soil_ph': soil_ph,
            'Soil_Nitrogen(g/kg)': soil_n, 'Soil_potassium(k)': potassium, 'Soil_phophorus(mg/kg)': phosphorus,
            'Veg_Avg_Temp': veg_temp, 'Rep_Avg_Temp': rep_temp, 'Growing_Season_Avg_Temp': growing_temp,
            'Planting_month': Planting_month, 'Area':Area,'Harvest_month': Harvest_month
            
         }
        # 3. Handle automated calculations
        # Computes duration across calendar wrap-arounds safely
        if Harvest_month >= Planting_month:
         input_data['Growing_Season_Length'] = Harvest_month - Planting_month
        else:
         input_data['Growing_Season_Length'] = (12 - Planting_month) + Harvest_month

        # Convert to final inference frame
        features_df = pd.DataFrame([input_data])[FEATURE_COLUMNS]

        st.markdown("---")
        if st.button("🚀 Process Parallel Machine Learning Forecast", type="primary"):
            pred_rf_val = rf_model.predict(features_df)[0]
            pred_gb_val = gb_model.predict(features_df)[0]

            res_col1, res_col2 = st.columns(2)
            with res_col1:
                st.metric(label="🌲 Random Forest Prediction", value=f"{pred_rf_val:.4f} t/ha")
            with res_col2:
                st.metric(label="⚡ Gradient Boosting Prediction", value=f"{pred_gb_val:.4f} t/ha")
                