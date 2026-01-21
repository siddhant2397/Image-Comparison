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
@st.cache_resource
def get_team_db():
    client = pymongo.MongoClient(st.secrets["MONGO_URI"])
    return client["Cyclothon"]["team"]

st.set_page_config(page_title="Cyclothon Dashboard", layout="wide")
st.title("🏔️ Coastal Cyclothon")

# Sidebar Admin
with st.sidebar:
    st.header("👨‍💼 Admin Panel")
    admin_pass = st.text_input("Password", type="password")
    
    if st.button("Login") and admin_pass == "230200957":
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
        with st.form("daily_team_entry"):
            st.subheader("Daily Team Entry")
            team_total_distance = st.number_input("Team Total Distance Today (km)", min_value=0.0, step=1.0)
            team_avg_speed = st.number_input("Team Avg Speed Today (km/h)", min_value=0.0, step=0.1)
            submitted = st.form_submit_button("Log Team Data")
            
            if submitted:
                get_team_db().insert_one({
                    "date": date.today().isoformat(),
                    "team_total_distance": team_total_distance,
                    "team_avg_speed": team_avg_speed
                })
                st.success(f"✅ Team: {team_total_distance}km at {team_avg_speed}km/h!")
                st.rerun()



# Main Dashboard (visible to all)
col1, col2, col3, col4 = st.columns(4)
try:
    # Fetch ALL daily logs
    logs = list(get_team_db().find().sort("date", -1))
    df = pd.DataFrame(logs)
    df['date'] = pd.to_datetime(df['date'])
    log = list(get_db().find().sort("date", -1))
    df1 = pd.DataFrame(log)
    df1['date'] = pd.to_datetime(df1['date'])
    
    
    # Calculate cumulative totals per cyclist
    summary = df1.groupby('cyclist')['daily_distance'].sum().round(1)
    summary = summary.sort_values(ascending=False)
    total_distance = df['team_total_distance'].sum()
    avg_speed_all = df['team_avg_speed'].mean().round(1)
    days_active = len(df['date'].unique())
    
    
    # KPIs
    with col1: st.metric("Cumulative Team Distance", f"{total_distance:.1f} km")
    with col2: st.metric("Avg Speed (All Time)", f"{avg_speed_all} km/h")
    with col3: st.metric("Days Active", days_active)
    with col4: st.metric("Active Cyclists", len(summary))
    https://cloud.mongodb.com/v2/6881051e4e790c520e195dc2#/clusters/starterTemplates?from=ctaClusterHeader
    # Main table - CUMULATIVE totals
    st.subheader("👥 Cumulative Leaderboard")
    leaderboard_df = pd.DataFrame({
        'Cyclist': summary.index,
        'Total Distance (km)': summary.values
    })
    st.dataframe(leaderboard_df, use_container_width=True, height=400)
    
    # Chart
    # Daily Team Distance (AGGREGATED by date)
    st.subheader("📈 Daily Team Distance")
    df_daily = df.groupby(df['date'].dt.date)['team_total_distance'].sum().reset_index()
    df_daily['date'] = pd.to_datetime(df_daily['date'])

    fig_daily = px.bar(df_daily.sort_values('date', ascending=False).head(30),
                       x='date', y='team_total_distance',
                       title="Daily Distance (Combined)",
                       color='team_total_distance',
                       color_continuous_scale='Viridis')
    fig_daily.update_traces(texttemplate='%{y:.0f}km', textposition='outside')
    fig_daily.update_layout(xaxis_title="Date", yaxis_title="Daily Distance (km)")
    st.plotly_chart(fig_daily, use_container_width=True)


    
    
    
except:
    st.info("👆 Admin: Log first entry using sidebar")
