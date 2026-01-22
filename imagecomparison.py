import streamlit as st
import pandas as pd
import pymongo
from datetime import date
import plotly.express as px
import folium
from streamlit_folium import st_folium

# Page config
st.set_page_config(page_title="Cyclothon 2026", layout="wide")

# Initialize session state
if 'east_admin' not in st.session_state:
    st.session_state.east_admin = False
if 'west_admin' not in st.session_state:
    st.session_state.west_admin = False

# MongoDB Database Functions
@st.cache_resource
def get_east_db():
    client = pymongo.MongoClient(st.secrets["MONGO_URI"])
    db = client["Cyclothon"]
    return {
        "individuals": db["east_individuals"],
        "team": db["east_team"],
        "locations": db["east_locations"]
    }

@st.cache_resource
def get_west_db():
    client = pymongo.MongoClient(st.secrets["MONGO_URI"])
    db = client["Cyclothon"]
    return {
        "individuals": db["west_individuals"],
        "team": db["west_team"],
        "locations": db["west_locations"]
    }

# MAIN HEADING
st.title("🏔️ Cyclothon 2026")

# Create Coast Tabs
east_tab, west_tab = st.tabs(["🌅 East Coast", "🌊 West Coast"])

# SIDEBAR - DUAL ADMIN LOGIN
with st.sidebar:
    st.header("👨‍💼 Admin Login")
    
    # East Coast Admin Login
    st.markdown("### 🌅 East Coast Admin")
    east_pass = st.text_input("East Password", type="password", key="east_pass")
    if st.button("🔓 East Login", key="east_login") and east_pass == "EAST123":
        st.session_state.east_admin = True
        st.rerun()
    
    # West Coast Admin Login
    st.markdown("### 🌊 West Coast Admin")
    west_pass = st.text_input("West Password", type="password", key="west_pass")
    if st.button("🔓 West Login", key="west_login") and west_pass == "WEST456":
        st.session_state.west_admin = True
        st.rerun()
    
    # Status
    if st.session_state.east_admin:
        st.success("✅ East Admin Active")
    if st.session_state.west_admin:
        st.success("✅ West Admin Active")

# EAST COAST TAB
with east_tab:
    st.header("🌅 East Coast Team")
    
    # East Coast Admin Forms (Only for East Admin)
    if st.session_state.east_admin:
        with st.sidebar.expander("📝 East Coast Entry Forms", expanded=True):
            # Individual Entry
            with st.form("east_individual"):
                cyclist = st.selectbox("Select Cyclist", ["Ravi", "Priya", "Amit", "Neha"])
                daily_distance = st.number_input("Today's Distance (km)", min_value=0.0, step=0.1)
                submitted = st.form_submit_button("✅ Log East Distance")
                if submitted:
                    dbs = get_east_db()
                    dbs["individuals"].insert_one({
                        "cyclist": cyclist,
                        "date": date.today().isoformat(),
                        "daily_distance": daily_distance
                    })
                    st.success(f"✅ {daily_distance}km logged for {cyclist}!")
                    st.rerun()
            
            # Team Entry
            with st.form("east_team"):
                team_distance = st.number_input("Team Total Distance (km)", min_value=0.0, step=1.0)
                team_speed = st.number_input("Team Avg Speed (km/h)", min_value=0.0, step=0.1)
                submitted = st.form_submit_button("✅ Log East Team")
                if submitted:
                    dbs = get_east_db()
                    dbs["team"].insert_one({
                        "date": date.today().isoformat(),
                        "team_total_distance": team_distance,
                        "team_avg_speed": team_speed
                    })
                    st.success(f"✅ East Team: {team_distance}km @ {team_speed}km/h!")
                    st.rerun()
            
            # Location Entry
            with st.form("east_location"):
                location_name = st.text_input("Location Name")
                latitude = st.number_input("Latitude", value=20.0, min_value=-90.0, max_value=90.0, step=0.0001)
                longitude = st.number_input("Longitude", value=80.0, min_value=-180.0, max_value=180.0, step=0.0001)
                submitted = st.form_submit_button("📍 Add East Location")
                if submitted:
                    dbs = get_east_db()
                    dbs["locations"].insert_one({
                        "name": location_name,
                        "lat": latitude,
                        "lng": longitude,
                        "date": date.today().isoformat()
                    })
                    st.success(f"✅ {location_name} added!")
                    st.rerun()
    
    # East Coast Dashboard
    col1, col2, col3, col4 = st.columns(4)
    try:
        dbs = get_east_db()
        team_logs = list(dbs["team"].find().sort("date", -1))
        individual_logs = list(dbs["individuals"].find().sort("date", -1))
        
        if team_logs:
            df_team = pd.DataFrame(team_logs)
            df_team['date'] = pd.to_datetime(df_team['date'])
            df_individual = pd.DataFrame(individual_logs)
            df_individual['date'] = pd.to_datetime(df_individual['date'])
            
            # KPIs
            total_distance = df_team['team_total_distance'].sum()
            avg_speed = df_team['team_avg_speed'].mean().round(1)
            days_active = len(df_team['date'].dt.date.unique())
            cyclists = df_individual['cyclist'].nunique() if len(df_individual) > 0 else 0
            
            with col1: st.metric("Total Distance", f"{total_distance:.0f} km")
            with col2: st.metric("Avg Speed", f"{avg_speed} km/h")
            with col3: st.metric("Days Active", days_active)
            with col4: st.metric("Cyclists", cyclists)
            
            # Leaderboard
            if len(df_individual) > 0:
                summary = df_individual.groupby('cyclist')['daily_distance'].sum().round(1).sort_values(ascending=False)
                st.subheader("👥 East Coast Leaderboard")
                leaderboard_df = pd.DataFrame({
                    'Cyclist': summary.index,
                    'Total (km)': summary.values
                })
                st.dataframe(leaderboard_df, width='stretch', height=300)
            
            
            # Route Map
            st.subheader("🗺️ East Coast Route")
            locs = list(dbs["locations"].find().sort("date", -1))
            if locs:
                m = folium.Map(location=[15.0, 85.0], zoom_start=6)
                for loc in locs:
                    folium.Marker(
                        [loc['lat'], loc['lng']],
                        popup=f"<b style='color:red'>{loc['name']}</b><br>{loc.get('date', 'N/A')}",
                        tooltip=loc['name'],
                        icon=folium.Icon(color='red', icon='info-sign')
                    ).add_to(m)
                st_folium(m, width=1200, height=500)
            else:
                st.info("👆 East Admin: Add locations using sidebar form")
        else:
            st.info("👆 East Admin: Log first team entry using sidebar!")
            
    except Exception as e:
        st.error(f"East Coast data error: {str(e)}")

# WEST COAST TAB
with west_tab:
    st.header("🌊 West Coast Team")
    
    # West Coast Admin Forms (Only for West Admin)
    if st.session_state.west_admin:
        with st.sidebar.expander("📝 West Coast Entry Forms", expanded=True):
            # Individual Entry
            with st.form("west_individual"):
                cyclist = st.selectbox("Select Cyclist", ["Vikram", "Sonia", "Kiran", "Meera"])
                daily_distance = st.number_input("Today's Distance (km)", min_value=0.0, step=0.1)
                submitted = st.form_submit_button("✅ Log West Distance")
                if submitted:
                    dbs = get_west_db()
                    dbs["individuals"].insert_one({
                        "cyclist": cyclist,
                        "date": date.today().isoformat(),
                        "daily_distance": daily_distance
                    })
                    st.success(f"✅ {daily_distance}km logged for {cyclist}!")
                    st.rerun()
            
            # Team Entry
            with st.form("west_team"):
                team_distance = st.number_input("Team Total Distance (km)", min_value=0.0, step=1.0)
                team_speed = st.number_input("Team Avg Speed (km/h)", min_value=0.0, step=0.1)
                submitted = st.form_submit_button("✅ Log West Team")
                if submitted:
                    dbs = get_west_db()
                    dbs["team"].insert_one({
                        "date": date.today().isoformat(),
                        "team_total_distance": team_distance,
                        "team_avg_speed": team_speed
                    })
                    st.success(f"✅ West Team: {team_distance}km @ {team_speed}km/h!")
                    st.rerun()
            
            # Location Entry
            with st.form("west_location"):
                location_name = st.text_input("Location Name")
                latitude = st.number_input("Latitude", value=20.0, min_value=-90.0, max_value=90.0, step=0.0001)
                longitude = st.number_input("Longitude", value=72.0, min_value=-180.0, max_value=180.0, step=0.0001)
                submitted = st.form_submit_button("📍 Add West Location")
                if submitted:
                    dbs = get_west_db()
                    dbs["locations"].insert_one({
                        "name": location_name,
                        "lat": latitude,
                        "lng": longitude,
                        "date": date.today().isoformat()
                    })
                    st.success(f"✅ {location_name} added!")
                    st.rerun()
    
    # West Coast Dashboard (identical structure)
    col1, col2, col3, col4 = st.columns(4)
    try:
        dbs = get_west_db()
        team_logs = list(dbs["team"].find().sort("date", -1))
        individual_logs = list(dbs["individuals"].find().sort("date", -1))
        
        if team_logs:
            df_team = pd.DataFrame(team_logs)
            df_team['date'] = pd.to_datetime(df_team['date'])
            df_individual = pd.DataFrame(individual_logs)
            df_individual['date'] = pd.to_datetime(df_individual['date'])
            
            # KPIs
            total_distance = df_team['team_total_distance'].sum()
            avg_speed = df_team['team_avg_speed'].mean().round(1)
            days_active = len(df_team['date'].dt.date.unique())
            cyclists = df_individual['cyclist'].nunique() if len(df_individual) > 0 else 0
            
            with col1: st.metric("Total Distance", f"{total_distance:.0f} km")
            with col2: st.metric("Avg Speed", f"{avg_speed} km/h")
            with col3: st.metric("Days Active", days_active)
            with col4: st.metric("Cyclists", cyclists)
            
            # Leaderboard
            if len(df_individual) > 0:
                summary = df_individual.groupby('cyclist')['daily_distance'].sum().round(1).sort_values(ascending=False)
                st.subheader("👥 West Coast Leaderboard")
                leaderboard_df = pd.DataFrame({
                    'Cyclist': summary.index,
                    'Total (km)': summary.values
                })
                st.dataframe(leaderboard_df, width='stretch', height=300)
            
            
            # Route Map
            st.subheader("🗺️ West Coast Route")
            locs = list(dbs["locations"].find().sort("date", -1))
            if locs:
                m = folium.Map(location=[20.0, 72.0], zoom_start=6)
                for loc in locs:
                    folium.Marker(
                        [loc['lat'], loc['lng']],
                        popup=f"<b style='color:blue'>{loc['name']}</b><br>{loc.get('date', 'N/A')}",
                        tooltip=loc['name'],
                        icon=folium.Icon(color='blue', icon='info-sign')
                    ).add_to(m)
                st_folium(m, width=1200, height=500)
            else:
                st.info("👆 West Admin: Add locations using sidebar form")
        else:
            st.info("👆 West Admin: Log first team entry using sidebar!")
            
    except Exception as e:
        st.error(f"West Coast data error: {str(e)}")
