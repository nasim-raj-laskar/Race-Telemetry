import streamlit as st
import requests
import pandas as pd
import time

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Race Telemetry Dashboard",
    layout="wide"
)

st.title("🏎️ Race Telemetry – Live Inference Dashboard")

# ---------------- Session State ----------------
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame()

if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = True

# ---------------- Controls ----------------
col1, col2, col3 = st.columns(3)

with col1:
    batch_size = st.number_input(
        "Batch size per fetch",
        min_value=1,
        max_value=50,
        value=5
    )

with col2:
    refresh_interval = st.slider(
        "Refresh interval (seconds)",
        min_value=1,
        max_value=10,
        value=2
    )

with col3:
    st.session_state.auto_refresh = st.toggle(
        "Auto refresh",
        value=True
    )

# ---------------- Fetch Data ----------------
def fetch_predictions(batch_size: int):
    try:
        resp = requests.get(
            f"{BACKEND_URL}/infer/next",
            params={"batch_size": batch_size},
            timeout=5
        )
        resp.raise_for_status()
        return pd.DataFrame(resp.json())
    except Exception as e:
        st.error(f"Backend error: {e}")
        return pd.DataFrame()

# ---------------- Live Update ----------------
if st.session_state.auto_refresh:
    new_data = fetch_predictions(batch_size)

    if not new_data.empty:
        st.session_state.data = pd.concat(
            [st.session_state.data, new_data],
            ignore_index=True
        )

# ---------------- Display ----------------
st.subheader("📊 Live Predictions")

if st.session_state.data.empty:
    st.info("Waiting for data...")
else:
    st.dataframe(
        st.session_state.data.tail(50),
        use_container_width=True
    )

# ---------------- Simple Metrics ----------------
st.subheader("📈 Quick Stats")

if not st.session_state.data.empty:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Avg Predicted Lap Time",
            f"{st.session_state.data['predicted_lap_time'].mean():.2f}"
        )

    with col2:
        st.metric(
            "Most Common Gear",
            int(st.session_state.data['predicted_gear'].mode()[0])
        )

    with col3:
        if "driving_behavior" in st.session_state.data.columns:
            st.metric(
                "Aggressive %",
                f"{(st.session_state.data['driving_behavior'] == 'Aggressive Driving').mean() * 100:.1f}%"
            )

# ---------------- Auto Refresh ----------------
if st.session_state.auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()
