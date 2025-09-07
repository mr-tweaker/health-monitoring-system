"""
Streamlit Dashboard for Health Monitoring System
Day 4: Demo Dashboard & Documentation
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import time

# Page configuration
st.set_page_config(
    page_title="Health Monitoring System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API configuration
API_BASE_URL = "http://localhost:8000"

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .alert-critical {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .alert-warning {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .alert-info {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
        padding: 1rem;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)  # Cache for 1 minute
def fetch_api_data(endpoint):
    """Fetch data from API with caching"""
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Connection Error: {e}")
        return None

def check_api_health():
    """Check if API is healthy"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def display_system_status():
    """Display system status"""
    st.subheader("🔧 System Status")
    
    if check_api_health():
        st.success("✅ API is healthy and responding")
        
        # Get system health details
        health_data = fetch_api_data("/api/status")
        if health_data:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("System Status", health_data.get("system", {}).get("status", "Unknown"))
            
            with col2:
                st.metric("Database", health_data.get("database", {}).get("status", "Unknown"))
            
            with col3:
                st.metric("ML Models", health_data.get("services", {}).get("ml_models", "Unknown"))
            
            with col4:
                st.metric("Alert System", health_data.get("services", {}).get("alert_system", "Unknown"))
    else:
        st.error("❌ API is not responding. Please start the health monitoring system.")

def display_dashboard_overview():
    """Display dashboard overview"""
    st.subheader("📊 Dashboard Overview")
    
    overview_data = fetch_api_data("/api/dashboard/overview")
    if overview_data:
        summary = overview_data.get("summary", {})
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            st.metric("Total Patients", summary.get("total_patients", 0))
        
        with col2:
            st.metric("Recent Vitals", summary.get("recent_vitals_count", 0))
        
        with col3:
            st.metric("Anomalies", summary.get("recent_anomalies_count", 0))
        
        with col4:
            st.metric("Total Alerts", summary.get("recent_alerts_count", 0))
        
        with col5:
            st.metric("Critical Alerts", summary.get("critical_alerts_count", 0))
        
        with col6:
            st.metric("Unacknowledged", summary.get("unacknowledged_alerts_count", 0))

def display_patients_status():
    """Display patients status"""
    st.subheader("👥 Patients Status")
    
    patients_data = fetch_api_data("/api/dashboard/patients-status")
    if patients_data:
        patients = patients_data.get("patients", [])
        
        if patients:
            # Create DataFrame
            df = pd.DataFrame(patients)
            
            # Color code status
            status_colors = {
                "NORMAL": "🟢",
                "WARNING": "🟡", 
                "CRITICAL": "🔴",
                "INFO": "🔵"
            }
            
            df["Status Icon"] = df["status"].map(status_colors)
            
            # Display table
            st.dataframe(
                df[["Status Icon", "patient_id", "name", "age", "gender", "status", "anomalies_count", "last_updated"]],
                use_container_width=True
            )
            
            # Status distribution
            col1, col2 = st.columns(2)
            
            with col1:
                status_counts = df["status"].value_counts()
                fig = px.pie(
                    values=status_counts.values,
                    names=status_counts.index,
                    title="Patient Status Distribution",
                    color_discrete_map={
                        "NORMAL": "#4CAF50",
                        "WARNING": "#FF9800", 
                        "CRITICAL": "#F44336",
                        "INFO": "#2196F3"
                    }
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Anomalies by patient
                fig = px.bar(
                    df,
                    x="name",
                    y="anomalies_count",
                    title="Anomalies Count by Patient",
                    color="anomalies_count",
                    color_continuous_scale="Reds"
                )
                fig.update_xaxes(tickangle=45)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No patients found. Please generate sample data first.")

def display_vitals_trends():
    """Display vital signs trends"""
    st.subheader("📈 Vital Signs Trends")
    
    # Get patients for selection
    patients_data = fetch_api_data("/api/patients/")
    if patients_data:
        patient_options = {f"{p['name']} ({p['patient_id']})": p['patient_id'] for p in patients_data}
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            selected_patient = st.selectbox("Select Patient", list(patient_options.keys()))
        
        with col2:
            hours = st.selectbox("Time Range", [6, 12, 24, 48], index=2)
        
        if selected_patient:
            patient_id = patient_options[selected_patient]
            
            # Get vital signs trends
            trends_data = fetch_api_data(f"/api/dashboard/vitals-trends?patient_id={patient_id}&hours={hours}")
            
            if trends_data and trends_data.get("trends"):
                trends = trends_data["trends"]

                # Compute LIVE badge (last point within 120 seconds)
                last_ts = None
                for series in trends.values():
                    if series:
                        # collect timestamps safely
                        s_ts = pd.to_datetime([p.get("timestamp") for p in series], errors="coerce", utc=True)
                        if not s_ts.empty and pd.notna(s_ts.max()):
                            t = s_ts.max()
                            if last_ts is None or t > last_ts:
                                last_ts = t
                is_live = False
                if last_ts is not None and pd.notna(last_ts):
                    is_live = (pd.Timestamp.now(tz="UTC") - last_ts).total_seconds() <= 120
                st.markdown(f"{'🟢 LIVE' if is_live else '⚪ Offline'} — last update: {last_ts if last_ts is not None else '—'}")
                
                # Create tabs for different metrics
                tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                    "Heart Rate", "SpO2", "Glucose", "Blood Pressure", "Temperature", "All Metrics"
                ])
                
                with tab1:
                    if trends.get("heart_rate"):
                        df_hr = pd.DataFrame(trends["heart_rate"])
                        # tolerant timestamp parsing (ISO or epoch seconds)
                        ts = df_hr["timestamp"]
                        df_hr["timestamp"] = pd.to_datetime(ts, errors="coerce", utc=True)
                        mask_num = df_hr["timestamp"].isna() & pd.to_numeric(ts, errors="coerce").notna()
                        if mask_num.any():
                            df_hr.loc[mask_num, "timestamp"] = pd.to_datetime(pd.to_numeric(ts[mask_num]), unit="s", utc=True)
                        df_hr = df_hr.dropna(subset=["timestamp"]).sort_values("timestamp")
                        
                        fig = px.line(
                            df_hr,
                            x="timestamp",
                            y="value",
                            title="Heart Rate Trend",
                            labels={"value": "Heart Rate (BPM)"}
                        )
                        fig.add_hline(y=120, line_dash="dash", line_color="red", annotation_text="High Threshold")
                        fig.add_hline(y=50, line_dash="dash", line_color="red", annotation_text="Low Threshold")
                        st.plotly_chart(fig, use_container_width=True)
                
                with tab2:
                    if trends.get("spo2"):
                        df_spo2 = pd.DataFrame(trends["spo2"])
                        ts = df_spo2["timestamp"]
                        df_spo2["timestamp"] = pd.to_datetime(ts, errors="coerce", utc=True)
                        mask_num = df_spo2["timestamp"].isna() & pd.to_numeric(ts, errors="coerce").notna()
                        if mask_num.any():
                            df_spo2.loc[mask_num, "timestamp"] = pd.to_datetime(pd.to_numeric(ts[mask_num]), unit="s", utc=True)
                        df_spo2 = df_spo2.dropna(subset=["timestamp"]).sort_values("timestamp")
                        
                        fig = px.line(
                            df_spo2,
                            x="timestamp",
                            y="value",
                            title="SpO2 Trend",
                            labels={"value": "SpO2 (%)"}
                        )
                        fig.add_hline(y=90, line_dash="dash", line_color="red", annotation_text="Low Threshold")
                        st.plotly_chart(fig, use_container_width=True)
                
                with tab3:
                    if trends.get("glucose"):
                        df_glucose = pd.DataFrame(trends["glucose"])
                        ts = df_glucose["timestamp"]
                        df_glucose["timestamp"] = pd.to_datetime(ts, errors="coerce", utc=True)
                        mask_num = df_glucose["timestamp"].isna() & pd.to_numeric(ts, errors="coerce").notna()
                        if mask_num.any():
                            df_glucose.loc[mask_num, "timestamp"] = pd.to_datetime(pd.to_numeric(ts[mask_num]), unit="s", utc=True)
                        df_glucose = df_glucose.dropna(subset=["timestamp"]).sort_values("timestamp")
                        
                        fig = px.line(
                            df_glucose,
                            x="timestamp",
                            y="value",
                            title="Glucose Trend",
                            labels={"value": "Glucose (mg/dL)"}
                        )
                        fig.add_hline(y=200, line_dash="dash", line_color="red", annotation_text="High Threshold")
                        fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Low Threshold")
                        st.plotly_chart(fig, use_container_width=True)
                
                with tab4:
                    if trends.get("blood_pressure_systolic") and trends.get("blood_pressure_diastolic"):
                        df_bp_sys = pd.DataFrame(trends["blood_pressure_systolic"])
                        df_bp_dia = pd.DataFrame(trends["blood_pressure_diastolic"])
                        ts_sys = df_bp_sys["timestamp"]
                        df_bp_sys["timestamp"] = pd.to_datetime(ts_sys, errors="coerce", utc=True)
                        mask_num = df_bp_sys["timestamp"].isna() & pd.to_numeric(ts_sys, errors="coerce").notna()
                        if mask_num.any():
                            df_bp_sys.loc[mask_num, "timestamp"] = pd.to_datetime(pd.to_numeric(ts_sys[mask_num]), unit="s", utc=True)
                        ts_dia = df_bp_dia["timestamp"]
                        df_bp_dia["timestamp"] = pd.to_datetime(ts_dia, errors="coerce", utc=True)
                        mask_num = df_bp_dia["timestamp"].isna() & pd.to_numeric(ts_dia, errors="coerce").notna()
                        if mask_num.any():
                            df_bp_dia.loc[mask_num, "timestamp"] = pd.to_datetime(pd.to_numeric(ts_dia[mask_num]), unit="s", utc=True)
                        df_bp_sys = df_bp_sys.dropna(subset=["timestamp"]).sort_values("timestamp")
                        df_bp_dia = df_bp_dia.dropna(subset=["timestamp"]).sort_values("timestamp")
                        
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=df_bp_sys["timestamp"],
                            y=df_bp_sys["value"],
                            name="Systolic",
                            line=dict(color="red")
                        ))
                        fig.add_trace(go.Scatter(
                            x=df_bp_dia["timestamp"],
                            y=df_bp_dia["value"],
                            name="Diastolic",
                            line=dict(color="blue")
                        ))
                        fig.update_layout(
                            title="Blood Pressure Trend",
                            xaxis_title="Time",
                            yaxis_title="Blood Pressure (mmHg)"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                with tab5:
                    if trends.get("temperature"):
                        df_temp = pd.DataFrame(trends["temperature"])
                        ts = df_temp["timestamp"]
                        df_temp["timestamp"] = pd.to_datetime(ts, errors="coerce", utc=True)
                        mask_num = df_temp["timestamp"].isna() & pd.to_numeric(ts, errors="coerce").notna()
                        if mask_num.any():
                            df_temp.loc[mask_num, "timestamp"] = pd.to_datetime(pd.to_numeric(ts[mask_num]), unit="s", utc=True)
                        df_temp = df_temp.dropna(subset=["timestamp"]).sort_values("timestamp")
                        
                        fig = px.line(
                            df_temp,
                            x="timestamp",
                            y="value",
                            title="Temperature Trend",
                            labels={"value": "Temperature (°F)"}
                        )
                        fig.add_hline(y=99.5, line_dash="dash", line_color="red", annotation_text="High Threshold")
                        fig.add_hline(y=97.5, line_dash="dash", line_color="red", annotation_text="Low Threshold")
                        st.plotly_chart(fig, use_container_width=True)
                
                with tab6:
                    # Combined chart
                    fig = go.Figure()
                    
                    colors = ["red", "blue", "green", "orange", "purple"]
                    metrics = ["heart_rate", "spo2", "glucose", "blood_pressure_systolic", "temperature"]
                    metric_names = ["Heart Rate", "SpO2", "Glucose", "BP Systolic", "Temperature"]
                    
                    for i, (metric, name) in enumerate(zip(metrics, metric_names)):
                        if trends.get(metric):
                            df_metric = pd.DataFrame(trends[metric])
                            ts = df_metric["timestamp"]
                            df_metric["timestamp"] = pd.to_datetime(ts, errors="coerce", utc=True)
                            mask_num = df_metric["timestamp"].isna() & pd.to_numeric(ts, errors="coerce").notna()
                            if mask_num.any():
                                df_metric.loc[mask_num, "timestamp"] = pd.to_datetime(pd.to_numeric(ts[mask_num]), unit="s", utc=True)
                            df_metric = df_metric.dropna(subset=["timestamp"]).sort_values("timestamp")
                            
                            fig.add_trace(go.Scatter(
                                x=df_metric["timestamp"],
                                y=df_metric["value"],
                                name=name,
                                line=dict(color=colors[i % len(colors)])
                            ))
                    
                    fig.update_layout(
                        title="All Vital Signs Trends",
                        xaxis_title="Time",
                        yaxis_title="Value"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No vital signs data available for the selected patient and time range.")

def display_alerts():
    """Display alerts"""
    st.subheader("🚨 Recent Alerts")
    
    # Get recent alerts
    alerts_data = fetch_api_data("/api/alerts/?hours=24")
    if alerts_data:
        if alerts_data:
            # Create DataFrame
            df = pd.DataFrame(alerts_data)
            
            # Display alerts
            for _, alert in df.iterrows():
                severity = alert["severity"]
                timestamp = pd.to_datetime(alert["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
                
                if severity == "CRITICAL":
                    st.markdown(f"""
                    <div class="alert-critical">
                        <strong>🔴 CRITICAL ALERT</strong><br>
                        <strong>Patient:</strong> {alert['patient_id']}<br>
                        <strong>Type:</strong> {alert['alert_type']}<br>
                        <strong>Time:</strong> {timestamp}<br>
                        <strong>Message:</strong> {alert['message']}<br>
                        <strong>Status:</strong> {'✅ Acknowledged' if alert['is_acknowledged'] else '⚠️ Unacknowledged'}
                    </div>
                    """, unsafe_allow_html=True)
                elif severity == "WARNING":
                    st.markdown(f"""
                    <div class="alert-warning">
                        <strong>🟡 WARNING ALERT</strong><br>
                        <strong>Patient:</strong> {alert['patient_id']}<br>
                        <strong>Type:</strong> {alert['alert_type']}<br>
                        <strong>Time:</strong> {timestamp}<br>
                        <strong>Message:</strong> {alert['message']}<br>
                        <strong>Status:</strong> {'✅ Acknowledged' if alert['is_acknowledged'] else '⚠️ Unacknowledged'}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="alert-info">
                        <strong>🔵 INFO ALERT</strong><br>
                        <strong>Patient:</strong> {alert['patient_id']}<br>
                        <strong>Type:</strong> {alert['alert_type']}<br>
                        <strong>Time:</strong> {timestamp}<br>
                        <strong>Message:</strong> {alert['message']}<br>
                        <strong>Status:</strong> {'✅ Acknowledged' if alert['is_acknowledged'] else '⚠️ Unacknowledged'}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No recent alerts found.")
    else:
        st.error("Failed to fetch alerts data.")

def display_anomalies():
    """Display anomalies"""
    st.subheader("🔍 Recent Anomalies")
    
    # Get anomalies summary
    anomalies_data = fetch_api_data("/api/dashboard/anomalies-summary?hours=24")
    if anomalies_data:
        summary = anomalies_data
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Anomalies", summary.get("total_anomalies", 0))
        
        with col2:
            severity_breakdown = summary.get("severity_breakdown", {})
            st.metric("Critical", severity_breakdown.get("CRITICAL", 0))
        
        with col3:
            st.metric("Warnings", severity_breakdown.get("WARNING", 0))
        
        # Anomalies by type
        type_breakdown = summary.get("type_breakdown", {})
        if type_breakdown:
            fig = px.bar(
                x=list(type_breakdown.keys()),
                y=list(type_breakdown.values()),
                title="Anomalies by Type",
                labels={"x": "Anomaly Type", "y": "Count"}
            )
            st.plotly_chart(fig, use_container_width=True)

def main():
    """Main dashboard function"""
    # Header
    st.markdown('<h1 class="main-header">🏥 Health Monitoring System</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📋 Navigation")
        page = st.selectbox("Select Page", [
            "Dashboard Overview",
            "Patients Status", 
            "Vital Signs Trends",
            "Alerts",
            "Anomalies",
            "System Status"
        ])
        
        st.header("🔄 Refresh")
        if st.button("Refresh Data"):
            st.cache_data.clear()
            st.rerun()
        
        st.header("ℹ️ Information")
        st.info("""
        This is a demo dashboard for the Health Monitoring System.
        
        **Features:**
        - Real-time patient monitoring
        - Anomaly detection
        - Alert management
        - Vital signs visualization
        
        **API Endpoint:** http://localhost:8000
        """)
    
    # Main content based on selected page
    if page == "Dashboard Overview":
        display_dashboard_overview()
        display_system_status()
    
    elif page == "Patients Status":
        display_patients_status()
    
    elif page == "Vital Signs Trends":
        display_vitals_trends()
    
    elif page == "Alerts":
        display_alerts()
    
    elif page == "Anomalies":
        display_anomalies()
    
    elif page == "System Status":
        display_system_status()
        
        # Additional system information
        st.subheader("🔧 System Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("""
            **System Components:**
            - FastAPI Backend
            - SQLite Database
            - ML Anomaly Detection
            - Alert System
            - UNIX Automation Scripts
            """)
        
        with col2:
            st.info("""
            **Automation Features:**
            - Health checks every 5 minutes
            - Data simulation every minute
            - Daily backups at 2 AM
            - Alert monitoring
            """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        Health Monitoring System - AI-Powered Health Monitoring<br>
        Built with FastAPI, Streamlit, and Machine Learning
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
