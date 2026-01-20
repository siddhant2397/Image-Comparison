import streamlit as st
import pandas as pd
import pymongo
from datetime import datetime, date
import plotly.express as px

# MongoDB connection
@st.cache_resource
def get_db():
    client = pymongo.MongoClient(st.secrets["MONGO_URI"])
    return client["Cyclothon"]["daily_logs"]

st.set_page_config(page_title="Cyclothon Dashboard", layout="wide")
st.title("🏔️ Coastal Cyclothon - Cumulative Progress")

# Sidebar Admin
with st.sidebar:
    st.header("👨‍💼 Admin Panel")
    admin_pass = st.text_input("Password", type="password")
    
    if st.button("Login") and admin_pass == "cyclothon2026":
        st.session_state.admin = True
        st.rerun()
    
    if st.session_state.get("admin", False):
        st.success("✅ Admin Logged In")
        
        # Daily Entry Form
        with st.form("daily_entry"):
            st.subheader("Daily Distance Entry")
            cyclist_name = st.selectbox("Select Cyclist", 
                options=["Ravi", "Priya", "Amit", "Neha", "Vikram", "Sonia"])  # Add your team names
            daily_distance = st.number_input("Today's Distance (km)", min_value=0.0, step=0.1)
            submitted = st.form_submit_button("Log Daily Distance")
            
            if submitted:
                # Save daily log
                get_db().insert_one({
                    "cyclist": cyclist_name,
                    "date": date.today().isoformat(),
                    "daily_distance": daily_distance
                })
                st.success(f"✅ {daily_distance}km logged for {cyclist_name}!")
                st.rerun()

# Main Dashboard (visible to all)
col1, col2, col3 = st.columns(3)
try:
    # Fetch ALL daily logs
    logs = list(get_db().find().sort("date", -1))
    df = pd.DataFrame(logs)
    df['date'] = pd.to_datetime(df['date'])
    
    # Calculate cumulative totals per cyclist
    summary = df.groupby('cyclist')['daily_distance'].sum().round(1)
    summary = summary.sort_values(ascending=False)
    
    # KPIs
    with col1: st.metric("Total Team Distance", f"{summary.sum():.1f} km")
    with col2: st.metric("Cyclists", len(summary))
    with col3: st.metric("Avg per Cyclist", f"{summary.mean():.1f} km")
    
    # Main table - CUMULATIVE totals
    st.subheader("👥 Cumulative Leaderboard")
    leaderboard_df = pd.DataFrame({
        'Cyclist': summary.index,
        'Total Distance (km)': summary.values
    })
    st.dataframe(leaderboard_df, use_container_width=True, height=400)
    
    # Chart
    fig = px.bar(leaderboard_df, x='Cyclist', y='Total Distance (km)', 
                title="Cumulative Distance by Cyclist", color='Total Distance (km)')
    st.plotly_chart(fig, use_container_width=True)
    
    # Recent daily entries
    st.subheader("📅 Today's Latest Entries")
    recent = df.tail(10)[['cyclist', 'daily_distance', 'date']]
    recent['date'] = recent['date'].dt.strftime('%Y-%m-%d')
    st.dataframe(recent, use_container_width=True)
    
except:
    st.info("👆 Admin: Log first entry using sidebar")
