import streamlit as st
import pandas as pd
import numpy as np
import socket
import json
from datetime import datetime

st.set_page_config(
    page_title="Enterprise Distributed Telemetry Core",
    layout="wide"
)

# Custom styling sheets
st.markdown("""
<style>
    .metric-box {
        background-color: #111827;
        padding: 22px;
        border-radius: 8px;
        border-left: 6px solid #10b981;
    }
    .metric-box-anomaly {
        background-color: #111827;
        padding: 22px;
        border-radius: 8px;
        border-left: 6px solid #ef4444;
        animation: pulse 2s infinite;
    }
</style>
""", unsafe_allow_html=True)

# Instantiating persistent session caching parameters
MAX_UI_HISTORY = 40
if "time_history" not in st.session_state: st.session_state.time_history = []
if "temp_history" not in st.session_state: st.session_state.temp_history = []
if "latency_history" not in st.session_state: st.session_state.latency_history = []
if "sock" not in st.session_state: st.session_state.sock = None
if "latest_payload" not in st.session_state: st.session_state.latest_payload = None

# Establish UI pipeline handshake connection
if st.session_state.sock is None:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', 5556))
        s.setblocking(False) # Non-blocking operations layout
        st.session_state.sock = s
        st.success("🔌 Telemetry Pipeline Stream Connected Successfully!")
    except Exception:
        st.warning("⏳ Pipeline processing engine offline. Verify background worker terminals are running.")
        st.stop()

# Consume incoming buffer frames from backend socket
s = st.session_state.sock
raw_buffer = ""
try:
    while True:
        chunk = s.recv(4096).decode('utf-8')
        if not chunk: break
        raw_buffer += chunk
except BlockingIOError:
    pass 

# Update visualization state arrays when data is available
if raw_buffer:
    lines = raw_buffer.strip().split("\n")
    if lines:
        try:
            latest_frame = json.loads(lines[-1]) # Read latest state update frame
            st.session_state.latest_payload = latest_frame
            
            st.session_state.time_history.append(latest_frame["timestamp"])
            st.session_state.temp_history.append(latest_frame["temperatures"])
            st.session_state.latency_history.append(latest_frame["latency_ms"])
            
            if len(st.session_state.time_history) > MAX_UI_HISTORY:
                st.session_state.time_history.pop(0)
                st.session_state.temp_history.pop(0)
                st.session_state.latency_history.pop(0)
        except Exception:
            pass

# Fallback block for buffering state initialization
if st.session_state.latest_payload is None:
    st.info("🔄 Synchronizing array matrices with core engine. Awaiting next live frame transmission tick...")
    st.button("Force Interface Refresh")
    st.stop()

frame = st.session_state.latest_payload

# Render advanced notification alerts dynamically based on worker processing state
if frame.get("is_anomaly", False):
    st.error(f"🚨 INDUSTRIAL ALARM: Statistical Jitter Detected by Analytics Engine! (Calculated Z-Score: {frame['calculated_z']})")
else:
    st.success("🟢 PIPELINE ARCHITECTURE METRICS STATUS: HEALTHY STRUCTURE")

st.title("🦿 Quadruped Telemetry Distributed Engine")
st.markdown(f"**Live Processing Sync Target:** `v3 Canonical Truth Architecture` | **Active Frame Tracking ID:** `{frame['frame_idx']}`")
st.markdown("---")

# Main Dashboard KPI blocks
k1, k2, k3, k4 = st.columns(4)
with k1:
    box_class = "metric-box-anomaly" if frame.get("is_anomaly", False) else "metric-box"
    status_text = "ANOMALOUS SPIKE" if frame.get("is_anomaly", False) else frame["computed_status"]
    st.markdown(f"<div class='{box_class}'>🔒 Pipeline Health Status<br><h3>{status_text}</h3></div>", unsafe_allow_html=True)
with k2:
    st.markdown(f"<div class='metric-box'>⏱️ Processing Loop Latency<br><h3>{frame['latency_ms']} ms</h3></div>", unsafe_allow_html=True)
with k3:
    st.markdown(f"<div class='metric-box'>🚌 Embedded CAN-FD Bus State<br><h3>{frame['bus_status']}</h3></div>", unsafe_allow_html=True)
with k4:
    st.markdown(f"<div class='metric-box'>🔥 High-Limit Actinide Thermal Tracker<br><h3>{max(frame['temperatures'])} °C</h3></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# High-Frequency Data Charts Layer
c1, c2 = st.columns(2)
with c1:
    st.subheader("Dynamic Actuator Temperature Curves Profile History")
    df_temp = pd.DataFrame(st.session_state.temp_history, columns=["FL", "FR", "RL", "RR"])
    df_temp.index = st.session_state.time_history
    st.line_chart(df_temp)
with c2:
    st.subheader("Calculated Core Loop Latency Over Time (ms)")
    df_lat = pd.DataFrame(st.session_state.latency_history, columns=["Latency"])
    df_lat.index = st.session_state.time_history
    st.area_chart(df_lat)

# Detailed Vector Matrix Grid
st.subheader("Isolated Multi-Channel Actuator Structural Array Metrics")
cols = st.columns(4)
labels = ["Front-Left Module (FL)", "Front-Right Module (FR)", "Rear-Left Module (RL)", "Rear-Right Module (RR)"]
for idx, col in enumerate(cols):
    with col:
        st.info(f"**{labels[idx]}**")
        st.metric(label="Module Thermal State", value=f"{frame['temperatures'][idx]} °C")
        st.metric(label="Applied Shaft Torque", value=f"{frame['torques'][idx]} Nm")

# Automated High-Frequency UI Rerun script hook
st.rerun()