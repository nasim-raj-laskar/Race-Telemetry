import streamlit as st
import pandas as pd
import requests
import time
import altair as alt

#CONFIG
API_URL = "http://127.0.0.1:8000/infer/next"
TRACK_IMAGE_PATH = "assets/track.png"

st.set_page_config(page_title="Race Telemetry", layout="wide")

#GLOBAL CSS
st.markdown("""
<style>
.ml-label {
    font-size: 20px;
    color: #94a3b8;
    margin-bottom: 0px;
}
.ml-value {
    font-size: 38px;       
    font-weight: 500;
    line-height: 2;
}
</style>
""", unsafe_allow_html=True)

#SESSION STATE
if "telemetry" not in st.session_state:
    st.session_state.telemetry = pd.DataFrame()

#SIDEBAR
st.sidebar.title("Pit Wall Controls")
auto_refresh = st.sidebar.toggle("Auto Refresh", value=True)
refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 1, 5, 1)
batch_size = st.sidebar.selectbox("Rows per fetch", [1, 5, 10], index=0)

#FETCH
def fetch_data():
    try:
        r = requests.get(API_URL, params={"batch_size": batch_size}, timeout=5)
        r.raise_for_status()
        data = r.json()
        return pd.DataFrame(data) if data else pd.DataFrame()
    except Exception as e:
        st.error(e)
        return pd.DataFrame()

#UPDATE DATA
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

#TITLE
st.markdown(
    """
    <div style="text-align:center; line-height:0;">
        <h2>🏁 Race Telemetry</h2>
        <h4>Pit Wall Dashboard</h4>
    </div>
    """,
    unsafe_allow_html=True
)

#TOP GRID
left, right = st.columns([3, 1])

#LEFT SIDE
with left:

    #ROW 1 : ML OUTPUT
    with st.container(border=True):
        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown('<div class="ml-label">Predicted Lap</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="ml-value" style="color:#38bdf8;">{latest["predicted_lap_time"]:.2f} s</div>',
                unsafe_allow_html=True
            )

        with c2:
            st.markdown('<div class="ml-label">Recommended Gear</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="ml-value" style="color:#22c55e;">{int(latest["predicted_gear"])}</div>',
                unsafe_allow_html=True
            )

        with c3:
            st.markdown('<div class="ml-label">Driving Style</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="ml-value" style="color:#facc15;">{latest["driving_behavior"]}</div>',
                unsafe_allow_html=True
            )

    st.markdown("<br>", unsafe_allow_html=True)

    #ROW 2 : SPEED + RPM
    r2c1, r2c2 = st.columns(2)

    r2c1.metric("Speed (km/h)", f"{latest['speed']:.1f}")
    r2c1.altair_chart(
        alt.Chart(df).mark_line(color="#38bdf8").encode(
            x="t:Q", y="speed:Q"
        ),
        use_container_width=True
    )

    r2c2.metric("Engine RPM", int(latest["current_engine_rpm"]))
    r2c2.altair_chart(
        alt.Chart(df).mark_area(color="#f97316", opacity=0.7).encode(
            x="t:Q", y="current_engine_rpm:Q"
        ),
        use_container_width=True
    )

#TRACK IMAGE (ROWS 1–2)
with right:
    st.markdown("###  Track")
    st.image(TRACK_IMAGE_PATH, use_container_width=True)

#ROW 3 : POWER / TORQUE / BOOST / TIRE
p1, p2, p3, p4 = st.columns(4)

df["power_kw"] = df["power"] / 1000

p1.metric("Power (kW)", f"{df['power_kw'].iloc[-1]:.1f}")
p1.altair_chart(
    alt.Chart(df).mark_area(color="#a855f7", opacity=0.6).encode(
        x="t:Q", y="power_kw:Q"
    ),
    use_container_width=True
)

p2.metric("Torque (Nm)", f"{latest['torque']:.1f}")
p2.altair_chart(
    alt.Chart(df).mark_line(color="#ef4444").encode(
        x="t:Q", y="torque:Q"
    ),
    use_container_width=True
)

p3.metric("Boost (psi)", f"{latest['boost']:.2f}")
p3.altair_chart(
    alt.Chart(df).mark_line(color="#0ea5e9").encode(
        x="t:Q", y="boost:Q"
    ),
    use_container_width=True
)

p4.metric("Avg Tire Temp (°C)", f"{latest['avg_tire_temp']:.1f}")
p4.altair_chart(
    alt.Chart(df).mark_line(color="#facc15").encode(
        x="t:Q", y="avg_tire_temp:Q"
    ),
    use_container_width=True
)

#ROW 4 : YAW / PITCH / ROLL
attitude_chart = alt.Chart(df).transform_fold(
    ["yaw", "pitch", "roll"],
    as_=["Axis", "Value"]
).mark_line(strokeWidth=2).encode(
    x="t:Q",
    y="Value:Q",
    color=alt.Color(
        "Axis:N",
        scale=alt.Scale(range=["#38bdf8", "#f97316", "#a855f7"])
    )
)

st.metric(
    "Yaw / Pitch / Roll (rad)",
    f"{latest['yaw']:.2f}, {latest['pitch']:.2f}, {latest['roll']:.2f}"
)
st.altair_chart(attitude_chart, use_container_width=True)

#REFRESH
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()
