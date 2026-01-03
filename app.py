import streamlit as st
import pandas as pd
import requests
import time
import altair as alt

# ================= CONFIG =================
API_URL = "http://127.0.0.1:8000/infer/next"

st.set_page_config(page_title="Race Telemetry", layout="wide")

# ================= SESSION STATE =================
if "telemetry" not in st.session_state:
    st.session_state.telemetry = pd.DataFrame()

# ================= SIDEBAR =================
st.sidebar.title("🏎️ Pit Wall Controls")
auto_refresh = st.sidebar.toggle("Auto Refresh", value=True)
refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 1, 5, 1)
batch_size = st.sidebar.selectbox("Rows per fetch", [1, 5, 10], index=0)

# ================= FETCH =================
def fetch_data():
    try:
        r = requests.get(API_URL, params={"batch_size": batch_size}, timeout=5)
        r.raise_for_status()
        data = r.json()
        return pd.DataFrame(data) if data else pd.DataFrame()
    except Exception as e:
        st.error(e)
        return pd.DataFrame()

# ================= DATA UPDATE =================
new_data = fetch_data()
if not new_data.empty:
    st.session_state.telemetry = pd.concat(
        [st.session_state.telemetry, new_data],
        ignore_index=True
    )

df = st.session_state.telemetry
if df.empty:
    st.stop()

df["t"] = range(len(df))
latest = df.iloc[-1]

# ================= TITLE =================
st.markdown(
    "<h4 style='text-align:center;'>🏁 Race Telemetry – Live Pit Wall</h4>",
    unsafe_allow_html=True
)

# ================= ML OUTPUT (LIVE) =================
st.markdown(
    f"""
    <div style="display:flex;justify-content:space-around;
        background:#020617;border:1px solid #334155;
        padding:12px;border-radius:10px;margin-bottom:20px;">
        <div><b>Predicted Lap</b><br>
            <span style="color:#38bdf8;font-size:18px;">
            {latest['predicted_lap_time']:.2f} s</span></div>
        <div><b>Recommended Gear</b><br>
            <span style="color:#22c55e;font-size:18px;">
            {int(latest['predicted_gear'])}</span></div>
        <div><b>Driving Style</b><br>
            <span style="color:#facc15;">
            {latest['driving_behavior']}</span></div>
    </div>
    """,
    unsafe_allow_html=True
)

# ================= ROW 1 =================
c1, c2, c3 = st.columns(3)

c1.metric("Speed (km/h)", f"{latest['speed']:.1f}")
c1.altair_chart(
    alt.Chart(df).mark_line(color="#38bdf8").encode(
        x="t:Q", y="speed:Q"
    ),
    use_container_width=True
)

c2.metric("Engine RPM", int(latest["current_engine_rpm"]))
c2.altair_chart(
    alt.Chart(df).mark_area(color="#f97316", opacity=0.7).encode(
        x="t:Q", y="current_engine_rpm:Q"
    ),
    use_container_width=True
)

c3.metric("Gear", int(latest["gear"]))
c3.altair_chart(
    alt.Chart(df).mark_bar(color="#22c55e").encode(
        x="t:Q", y="gear:Q"
    ),
    use_container_width=True
)

# ================= ROW 2 =================
c1, c2, c3 = st.columns(3)

df["power_kw"] = df["power"] / 1000

c1.metric("Power (kW)", f"{df['power_kw'].iloc[-1]:.1f}")
c1.altair_chart(
    alt.Chart(df).mark_area(color="#a855f7", opacity=0.6).encode(
        x="t:Q", y="power_kw:Q"
    ),
    use_container_width=True
)

c2.metric("Torque (Nm)", f"{latest['torque']:.1f}")
c2.altair_chart(
    alt.Chart(df).mark_line(color="#ef4444").encode(
        x="t:Q", y="torque:Q"
    ),
    use_container_width=True
)

c3.metric("Boost (psi)", f"{latest['boost']:.2f}")
c3.altair_chart(
    alt.Chart(df).mark_line(color="#0ea5e9").encode(
        x="t:Q", y="boost:Q"
    ),
    use_container_width=True
)

# ================= ROW 3 =================
c1, c2 = st.columns(2)

c1.metric("Avg Tire Temp (°C)", f"{latest['avg_tire_temp']:.1f}")
c1.altair_chart(
    alt.Chart(df).mark_line(color="#facc15").encode(
        x="t:Q", y="avg_tire_temp:Q"
    ),
    use_container_width=True
)

slip_chart = alt.Chart(df).transform_fold(
    ["wheel_slip_magnitude_front", "wheel_slip_magnitude_rear"],
    as_=["Wheel", "Slip"]
).mark_area(opacity=0.6).encode(
    x="t:Q",
    y="Slip:Q",
    color=alt.Color("Wheel:N", scale=alt.Scale(
        range=["#22c55e", "#ef4444"]
    ))
)
c2.metric("Rear Wheel Slip", f"{latest['wheel_slip_magnitude_rear']:.2f}")
c2.altair_chart(slip_chart, use_container_width=True)

# ================= ATTITUDE =================
attitude_chart = alt.Chart(df).transform_fold(
    ["yaw", "pitch", "roll"],
    as_=["Axis", "Value"]
).mark_line(strokeWidth=2).encode(
    x="t:Q",
    y="Value:Q",
    color=alt.Color("Axis:N", scale=alt.Scale(
        range=["#38bdf8", "#f97316", "#a855f7"]
    ))
)

st.metric("Yaw / Pitch / Roll (rad)",
          f"{latest['yaw']:.2f}, {latest['pitch']:.2f}, {latest['roll']:.2f}")
st.altair_chart(attitude_chart, use_container_width=True)

# ================= AUTO REFRESH (THE FIX) =================
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()
