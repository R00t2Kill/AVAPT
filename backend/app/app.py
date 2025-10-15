import os
import requests
import streamlit as st
from streamlit_folium import st_folium
import folium
import pandas as pd

API_BASE = os.environ.get("API_BASE", "http://localhost:8000")

st.set_page_config(layout="wide", page_title="CCTV AVAPT — Prototype")

st.title("CCTV AVAPT — Prototype (Python / Streamlit)")

with st.sidebar:
    st.header("Actions")
    if st.button("Load sample data (safe)"):
        resp = requests.post(f"{API_BASE}/api/ingest/shodan_sample")
        if resp.ok:
            st.success(f"Loaded sample: {resp.json().get('indexed')} items")
        else:
            st.error(f"Error: {resp.text}")

    shodan_query = st.text_input("Shodan query (read-only)", "")
    if st.button("Run Shodan ingest (read-only)"):
        if not os.environ.get("SHODAN_API_KEY"):
            st.warning("Set SHODAN_API_KEY in backend env to use this action.")
        else:
            resp = requests.post(f"{API_BASE}/api/ingest/shodan_query", json={"query": shodan_query})
            if resp.ok:
                st.success("Shodan ingestion started in background.")
            else:
                st.error(f"Error: {resp.text}")

    st.markdown("---")
    st.checkbox("Lab Mode (enable only for lab)", value=False, key="lab_mode")
    st.markdown("**Filtering**")
    q = st.text_input("Search text (vendor/model/banner)")

# Fetch devices
params = {"q": q, "size": 200}
resp = requests.get(f"{API_BASE}/api/devices", params=params)
if not resp.ok:
    st.error("Failed to fetch devices from backend.")
    st.stop()

data = resp.json().get("devices", [])
df = pd.DataFrame(data)

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Devices")
    if df.empty:
        st.info("No devices indexed. Click 'Load sample data (safe)' to populate demo data.")
    else:
        st.dataframe(df[["ip", "port", "vendor", "model", "firmware", "cves"]].fillna("-"))

        csv = df.to_csv(index=False)
        st.download_button("Export CSV", data=csv, file_name="devices.csv", mime="text/csv")

with col2:
    st.subheader("Map view")
    m = folium.Map(location=[20,0], zoom_start=2)
    # add markers for those with geo
    for idx, row in df.iterrows():
        geo = row.get("geo")
        if geo and isinstance(geo, dict) and geo.get("lat") and geo.get("lon"):
            folium.Marker([geo["lat"], geo["lon"]], popup=f"{row.get('ip')}:{row.get('port')}").add_to(m)
    st_data = st_folium(m, width=700, height=500)
