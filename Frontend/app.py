import streamlit as st
import requests

st.title("Railway Criminal Tracker")

uploaded_file = st.file_uploader("Upload Criminal PDF or Image", type=['pdf', 'jpg', 'jpeg', 'png'])

if uploaded_file:
    st.info("Uploading...")
    response = requests.post("http://localhost:5000/upload_file", files={"file": uploaded_file})
    st.success(response.json()["message"])

if st.button("Start CCTV Tracking"):
    response = requests.get("http://localhost:5000/start_feed")
    st.info(response.json()["message"])
