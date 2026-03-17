import streamlit as st
from deltalake import DeltaTable
import plotly.express as px
import os

st.set_page_config(page_title="Bitcoin Streaming Dashboard", layout="wide")

GOLD_PATH = "/data/delta/gold"
REFRESH_SECONDS = max(1, int(os.getenv("DASHBOARD_REFRESH_SECONDS", "10")))


def extract_window_start(value):
    if isinstance(value, dict):
        return value.get("start")
    return getattr(value, "start", value)


st.title("Bitcoin Streaming Dashboard (Gold Layer)")
st.markdown(f"Data sourced from Delta Lake Gold layer, auto-refreshing every {REFRESH_SECONDS} seconds.")
st.markdown(
    f'<meta http-equiv="refresh" content="{REFRESH_SECONDS}">',
    unsafe_allow_html=True,
)


def load_data():
    if not os.path.exists(GOLD_PATH):
        return None

    try:
        dt = DeltaTable(GOLD_PATH)
        df = dt.to_pandas()

        # Spark window is a struct {start, end}
        # deltalake to_pandas might return it as a dict or flat columns depending on version
        # Let's try to normalize it
        if "window" in df.columns:
            # Extract start time from the window struct/dict
            df["timestamp"] = df["window"].apply(extract_window_start)
            df = df.drop(columns=["window"])

        df = df.sort_values("timestamp")
        return df
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return None

df = load_data()

if df is not None and not df.empty:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Average Price (1-min Window)")
        fig_price = px.line(df, x="timestamp", y="avg_price", markers=True)
        st.plotly_chart(fig_price, use_container_width=True)

    with col2:
        st.subheader("Trading Volume (1-min Window)")
        fig_vol = px.bar(df, x="timestamp", y="total_volume")
        st.plotly_chart(fig_vol, use_container_width=True)

    st.subheader("Latest Raw Data")
    st.dataframe(df.tail(10), use_container_width=True)
else:
    st.warning("No data found. Please ensure the Gold layer job is running and writing data.")
    st.info(f"Checking path: {GOLD_PATH}")

