import streamlit as st
import pandas as pd
import pymongo
from datetime import date
import plotly.express as px
import folium
from streamlit_folium import st_folium


st.set_page_config(page_title="Cyclothon 2026", layout="wide")

if 'east_admin' not in st.session_state:
    st.session_state.east_admin = False
if 'west_admin' not in st.session_state:
    st.session_state.west_admin = False


@st.cache_resource
def get_east_db():
    client = pymongo.MongoClient(st.secrets["MONGO_URI"])
    db = client["Cyclothon"]
    return {
        "individuals": db["east_individuals"],
        "team": db["east_team"],
        "locations": db["east_locations"],
        "route": db["east_route"],
    }

@st.cache_resource
def get_west_db():
    client = pymongo.MongoClient(st.secrets["MONGO_URI"])
    db = client["Cyclothon"]
    return {
        "individuals": db["west_individuals"],
        "team": db["west_team"],
        "locations": db["west_locations"],
        "route": db["west_route"],
    }


st.title("🏔️ Cyclothon 2026")


east_tab, west_tab = st.tabs(["🌅 East Coast", "🌊 West Coast"])


with st.sidebar:
    st.header("👨‍💼 Admin Login")
    
    
    st.markdown("### 🌅 East Coast Admin")
    east_pass = st.text_input("East Password", type="password", key="east_pass")
    if st.button("🔓 East Login", key="east_login") and east_pass == "EAST123":
        st.session_state.east_admin = True
        st.rerun()
    
    
    st.markdown("### 🌊 West Coast Admin")
    west_pass = st.text_input("West Password", type="password", key="west_pass")
    if st.button("🔓 West Login", key="west_login") and west_pass == "WEST456":
        st.session_state.west_admin = True
        st.rerun()
    
    
    if st.session_state.east_admin:
        st.success("✅ East Admin Active")
    if st.session_state.west_admin:
        st.success("✅ West Admin Active")


with east_tab:
    st.header("🌅 East Coast Team")
    
    
    if st.session_state.east_admin:
        with st.sidebar.expander("📝 East Coast Entry Forms", expanded=True):
            
            with st.form("east_individual"):
                cyclist = st.selectbox("Select Cyclist", ["Siddhant Goswami", "Sujata Tushir", "Saurabh Yadav", "Kunal Sharma", "Tyarhiikho","Manoj","Kiran Mer","Jyoti Shukla","Pooja Jirwal","Lavanya","Satya Vrat","Belalsen","Saibabu","Duttajit","Monika Sabbu","Durga Charan","Chandra Shekhar","Shriram Meena","Srikanth","Madne Anil","Rajesh","Dinesh","Kunal Shah","Roshan","Mithilesh","Asha","Dhivya","Sivasankari","Hemlatha","Santhya","Balaji","Dasari Mouli","Amisha","Manisha Debnath","Shivani yadav","Mona Singh","Rajani Singh","Rachana","Gujalaramar","Sathish Kumar","Gosula Hareesh","Mude Ramana","Gottipalli Sateesh","Pushpender","Samir Modi","Saurav Sharma","Dora","Manisha Devi","Manju","Rimpa","Manisha","Munna Devi","Manasi","Mohini","Kodigana Bhawani","Pativada Pavani","Jyoti Kumari","Pooja Murmu","Jahnavi","Pallavi","Rahul Meitei","Muttanna","Babita Rani","Rohini M","Abhinaya"])
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
            
            
            total_distance = df_team['team_total_distance'].sum()
            avg_speed = df_team['team_avg_speed'].mean().round(1)
            days_active = len(df_team['date'].dt.date.unique())
            cyclists = df_individual['cyclist'].nunique() if len(df_individual) > 0 else 0
            
            with col1: st.metric("Total Distance", f"{total_distance:.0f} km")
            with col2: st.metric("Avg Speed", f"{avg_speed} km/h")
            with col3: st.metric("Days Active", days_active)
            with col4: st.metric("Cyclists", cyclists)
            
            
            if len(df_individual) > 0:
                summary = df_individual.groupby('cyclist')['daily_distance'].sum().round(1).sort_values(ascending=False)
                st.subheader("👥 East Coast Leaderboard")
                leaderboard_df = pd.DataFrame({
                    'Cyclist': summary.index,
                    'Total (km)': summary.values
                })
                st.dataframe(leaderboard_df, width='stretch', height=300)

            st.subheader("📊 Daily Team Distance - Day Numbers")
            df_daily = df_team.groupby(df_team['date'].dt.date)['team_total_distance'].sum().reset_index()
            df_daily = df_daily.sort_values('date')  # Oldest first
            df_daily['day_number'] = range(1, len(df_daily) + 1)
            df_daily['day_label'] = ['Day ' + str(n) for n in df_daily['day_number']]
            fig_scatter = px.scatter(
                df_daily.tail(30),  # Last 30 days
                x='day_label',
                y='team_total_distance',
                size='team_total_distance',  # Bigger dots = more distance
                size_max=25,color='team_total_distance',color_continuous_scale='Viridis',
                title="Daily Distance (Day 1, 2, 3...)",
                hover_data=['date', 'team_total_distance'])
            fig_scatter.update_traces(texttemplate='%{y:.0f}km',textposition='middle center',textfont_size=12,
                                      marker=dict(line=dict(width=1.5, color='white')))
            fig_scatter.update_layout(xaxis_title="Day Number",yaxis_title="Daily Distance (km)",height=450,
                                      showlegend=False)
            st.plotly_chart(fig_scatter,width='stretch')

            
            
            
            st.subheader("🗺️ East Coast Route")
            route_data = list(dbs["route"].find())
            admin_locations = list(dbs["locations"].find().sort("date", -1))  # Admin current location
            latest_admin_loc = admin_locations[0] if admin_locations else None 
            if route_data or admin_locations:
                m = folium.Map(location=[15.0, 85.0], zoom_start=6,
                               tiles='https://mt1.google.com/vt/lyrs=r&x={x}&y={y}&z={z}',
                               attr='Google')
                for stop in route_data:
                    folium.Marker([stop['lat'], stop['lng']],
                                  popup=f"""
                                  <b>📍 {stop['name']}</b><br>
                                  <i>Expected: {stop['date']}</i><br>
                                  <small>Route checkpoint</small>""",
                                  tooltip=f"{stop['name']} ({stop['date']})",
                                  icon=folium.DivIcon(
                                      html='🚴',
                                      icon_size=(10,10),
                                      icon_anchor=(15,15))
                                 ).add_to(m)

                if latest_admin_loc:
                    folium.Marker([latest_admin_loc['lat'], latest_admin_loc['lng']],
                                  popup=f"""
                                  <b style='color:red'>🎯 CURRENT LOCATION</b><br>
                                  {latest_admin_loc['name']}<br>
                                  <small>Reported: {latest_admin_loc.get('date', 'Today')}</small""",
                                  tooltip="CURRENT POSITION",
                                  icon=folium.Icon(color='red', icon='info-sign', icon_color='white')
                                 ).add_to(m)

                if len(route_data) > 1:
                    folium.PolyLine(locations=[[stop['lat'], stop['lng']] for stop in route_data],
                                    color="blue",
                                    weight=4,
                                    opacity=0.7,
                                    popup="Planned Route"
                                   ).add_to(m)
                    
                    
                m.fit_bounds([[8.0, 76.0], [24.0, 89.0]])
                st_folium(m, width=1200, height=500)
        
            else:
                st.info("👆 East Admin: Add locations using sidebar form")
        else:
            st.info("👆 East Admin: Log first team entry using sidebar!")
            
    except Exception as e:
        st.error(f"East Coast data error: {str(e)}")


with west_tab:
    st.header("🌊 West Coast Team")
    
    
    if st.session_state.west_admin:
        with st.sidebar.expander("📝 West Coast Entry Forms", expanded=True):
            
            with st.form("west_individual"):
                cyclist = st.selectbox("Select Cyclist", ["Praveen Kumar", "Nayana B Paul", "Ria Gope", "Bairagi Janardhan Arun", "Sameer Patil","Pushpender","Ramesh Ola","Pooja Jangra","Neeraj Dahia","Rishabh Bhandari","Mahendra Kumar","Layaket Ali","Sanjay Kumar","Lalita Kumari","Tulsi Das","Anuradha Yadav","Bansode Ganesh","Manju Mein","Gagan Yadav","Vignesh","Yashvant Thorat","Sarandev", "Anjali Kumari","Jadeja Nitalba","Arya Krishna","Rahul","Charanya Rutvik","Shridhar","Vaishnav","Ajith Krishnan","Pawan Prakash","Smirthy","Vanishree","Shalu meena","Arunima","Dinesh Yadav","Arun M","Yashkumar","Shinde Vaibhav","Sanjeev Kumar","Sanjay Nair","Anu Kumari","Mansoori","Neeraj Sharma","Varsha","Khushbu","Deepanjali Goya","Rinku","Payal Marve","Pinky","Sapna Rajput","Steffy","Rajeshwari","Geetanjali","Bornita","Shraddha Dhulaji","Bhil Pooja","Jyoti Kumai","Kajal Kushwaha","Alpna","Bharat Kumar","Amardeep","Jadhav","Archna","Shivani"])
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
            
            
            total_distance = df_team['team_total_distance'].sum()
            avg_speed = df_team['team_avg_speed'].mean().round(1)
            days_active = len(df_team['date'].dt.date.unique())
            cyclists = df_individual['cyclist'].nunique() if len(df_individual) > 0 else 0
            
            with col1: st.metric("Total Distance", f"{total_distance:.0f} km")
            with col2: st.metric("Avg Speed", f"{avg_speed} km/h")
            with col3: st.metric("Days Active", days_active)
            with col4: st.metric("Cyclists", cyclists)
            
            
            if len(df_individual) > 0:
                summary = df_individual.groupby('cyclist')['daily_distance'].sum().round(1).sort_values(ascending=False)
                st.subheader("👥 West Coast Leaderboard")
                leaderboard_df = pd.DataFrame({
                    'Cyclist': summary.index,
                    'Total (km)': summary.values
                })
                st.dataframe(leaderboard_df, width='stretch', height=300)

            st.subheader("📊 Daily Team Distance - Day Numbers")
            df_daily = df_team.groupby(df_team['date'].dt.date)['team_total_distance'].sum().reset_index()
            df_daily = df_daily.sort_values('date')  # Oldest first
            df_daily['day_number'] = range(1, len(df_daily) + 1)
            df_daily['day_label'] = ['Day ' + str(n) for n in df_daily['day_number']]
            fig_scatter = px.scatter(
                df_daily.tail(30),  # Last 30 days
                x='day_label',
                y='team_total_distance',
                size='team_total_distance',  # Bigger dots = more distance
                size_max=25,color='team_total_distance',color_continuous_scale='Viridis',
                title="Daily Distance (Day 1, 2, 3...)",
                hover_data=['date', 'team_total_distance'])
            fig_scatter.update_traces(texttemplate='%{y:.0f}km',textposition='middle center',textfont_size=12,
                                      marker=dict(line=dict(width=1.5, color='white')))
            fig_scatter.update_layout(xaxis_title="Day Number",yaxis_title="Daily Distance (km)",height=450,
                                      showlegend=False)
            st.plotly_chart(fig_scatter,width='stretch')
            
            
            
            st.subheader("🗺️ West Coast Route")
            route_data = list(dbs["route"].find())
            admin_locations = list(dbs["locations"].find().sort("date", -1))  # Admin current location
            latest_admin_loc = admin_locations[0] if admin_locations else None 
            if route_data or admin_locations:
                m = folium.Map(location=[20.0, 72.0], zoom_start=6,
                               tiles='https://mt1.google.com/vt/lyrs=r&x={x}&y={y}&z={z}',
                               attr='Google')
                for stop in route_data:
                    folium.Marker([stop['lat'], stop['lng']],
                                  popup=f"""
                                  <b>📍 {stop['name']}</b><br>
                                  <i>Expected: {stop['date']}</i><br>
                                  <small>Route checkpoint</small>""",
                                  tooltip=f"{stop['name']} ({stop['date']})",
                                  icon=folium.DivIcon(
                                      html='🚴',
                                      icon_size=(10,10),
                                      icon_anchor=(15,15))
                                 ).add_to(m)

                if latest_admin_loc:
                    folium.Marker([latest_admin_loc['lat'], latest_admin_loc['lng']],
                                  popup=f"""
                                  <b style='color:red'>🎯 CURRENT LOCATION</b><br>
                                  {latest_admin_loc['name']}<br>
                                  <small>Reported: {latest_admin_loc.get('date', 'Today')}</small""",
                                  tooltip="CURRENT POSITION",
                                  icon=folium.Icon(color='red', icon='info-sign', icon_color='white')
                                 ).add_to(m)

                if len(route_data) > 1:
                    folium.PolyLine(locations=[[stop['lat'], stop['lng']] for stop in route_data],
                                    color="blue",
                                    weight=4,
                                    opacity=0.7,
                                    popup="Planned Route"
                                   ).add_to(m)
                    
                    
                m.fit_bounds([[8.0, 68.0], [24.0, 75.0]])
                st_folium(m, width=1200, height=500)
            else:
                st.info("👆 West Admin: Add locations using sidebar form")
        else:
            st.info("👆 West Admin: Log first team entry using sidebar!")
            
    except Exception as e:
        st.error(f"West Coast data error: {str(e)}")
