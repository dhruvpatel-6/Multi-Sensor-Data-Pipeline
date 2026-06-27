import streamlit as st
import pandas as pd
import socket
import json

st.set_page_config(page_title="Convergence Telemetry Platform", layout="wide")

st.markdown("""
<style>
    .metric-card { background-color: #0f172a; padding: 20px; border-radius: 8px; border-left: 5px solid #3b82f6; }
    .fault-active { background-color: #451a03; padding: 20px; border-radius: 8px; border-left: 5px solid #f97316; }
</style>
""", unsafe_allow_html=True)

MAX_UI_HISTORY = 40
if "time_hist" not in st.session_state: st.session_state.time_hist = []
if "latency_hist" not in st.session_state: st.session_state.latency_hist = []
if "stability_hist" not in st.session_state: st.session_state.stability_hist = []
if "sock_conn" not in st.session_state: st.session_state.sock_conn = None
if "payload" not in st.session_state: st.session_state.payload = None

if st.session_state.sock_conn is None:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', 5556))
        s.setblocking(False)
        st.session_state.sock_conn = s
        st.success("🔌 Stream Link Socket Verified.")
    except Exception:
        st.error("⏳ Telemetry Stream Disconnected. Start backend worker architectures.")
        st.stop()

s = st.session_state.sock_conn
raw_data = ""
try:
    while True:
        chunk = s.recv(4096).decode('utf-8')
        if not chunk: break
        raw_data += chunk
except BlockingIOError:
    pass

if raw_data:
    lines = raw_data.strip().split("\n")
    if lines:
        try:
            frame = json.loads(lines[-1])
            st.session_state.payload = frame
            
            st.session_state.time_hist.append(frame["timestamp"])
            st.session_state.latency_hist.append(frame["observed_latency_ms"])
            st.session_state.stability_hist.append(frame["analytics"]["stability_score"])
            
            if len(st.session_state.time_hist) > MAX_UI_HISTORY:
                st.session_state.time_hist.pop(0)
                st.session_state.latency_hist.pop(0)
                st.session_state.stability_hist.pop(0)
        except Exception:
            pass

if st.session_state.payload is None:
    st.info("🔄 Re-aligning schema contracts. Synchronizing state arrays...")
    st.button("Force Global Refresh")
    st.stop()

frame = st.session_state.payload
analytics = frame["analytics"]
fault = frame["fault_injection_state"]

if fault != "NOMINAL":
    st.error(f"🚨 ACTIVE INJECTED FAULT propagation: {fault} | System response: {analytics['control_response']}")
else:
    st.success("🟢 REALITY CONVERGENCE PIPELINE METRICS CRITERIA: NOMINAL")

st.title("🐕 Quadruped Convergence Telemetry Core")
st.markdown(f"**Canonical Schema Model ID:** `{frame['contract_version']}` | **Current Framework Iteration ID:** `{frame['frame_idx']}`")
st.markdown("---")

m1, m2, m3, m4 = st.columns(4)
with m1:
    f_class = "fault-active" if fault != "NOMINAL" else "metric-card"
    st.markdown(f"<div class='{f_class}'>⚠️ Failure Model Layer<br><h3>{fault}</h3></div>", unsafe_allow_html=True)
with m2:
    st.markdown(f"<div class='metric-card'>🌍 Target Terrain Domain Context<br><h3>{frame['terrain_context']['terrain_id']}</h3></div>", unsafe_allow_html=True)
with m3:
    st.markdown(f"<div class='metric-card'>🎯 Deterministic Deadline Compliance<br><h3>{analytics['compliance_metrics']['cumulative_compliance_pct']}%</h3></div>", unsafe_allow_html=True)
with m4:
    st.markdown(f"<div class='metric-card'>⚖️ Locomotion Stability Score<br><h3>{analytics['stability_score']} / 100</h3></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

p1, p2 = st.columns(2)
with p1:
    st.subheader("Dynamic Locomotion Stability Score History Tracking")
    df_stab = pd.DataFrame(st.session_state.stability_hist, columns=["Stability Metric"], index=st.session_state.time_hist)
    st.line_chart(df_stab)
with p2:
    st.subheader("Observed Processing Loop Latency Profile vs Target Deadline (5.0ms)")
    df_lat = pd.DataFrame(st.session_state.latency_hist, columns=["Observed Latency"], index=st.session_state.time_hist)
    st.area_chart(df_lat)

st.subheader("Authoritative Contract Observability Breakdown Matrix")
d1, d2, d3 = st.columns(3)
with d1:
    st.info("🗺️ Active Terrain Boundaries")
    st.write(f"**Gait Command Selection:** `{frame['terrain_context']['recommended_gait']}`")
    st.write(f"**Energy Cost Coefficient:** `{frame['terrain_context']['energy_cost_estimate']} W`")
    st.write(f"**Calculated Slip Signature:** `{analytics['slip_signature']}`")
with d2:
    st.info("🦾 Joint Actuator Thermal/Torque State Vectors")
    st.write(f"**Max Actuator Peak Temp:** `{max(frame['sensor_matrices']['temperatures_c'])} °C`")
    st.write(f"**Active Torque Strain Index:** `{frame['sensor_matrices']['torques_nm']}`")
with d3:
    st.info("⏱️ Honest Real-time Performance Tracking")
    st.write(f"**Observed Process Latency:** `{frame['observed_latency_ms']} ms`")
    st.write(f"**Accumulated Clock Deadlines Breached:** `{analytics['compliance_metrics']['total_violations']} frames`")
    st.write(f"**Calculated Run Jitter (StdDev):** `{analytics['compliance_metrics']['running_mean_jitter_ms']} ms`")

st.rerun()