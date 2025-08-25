import streamlit as st
import requests
from streamlit_autorefresh import st_autorefresh

BACKEND_URL = "http://localhost:5000"

# ---------- Page setup ----------
st.set_page_config(page_title="🚨 Railway Criminal Tracker", layout="wide")
st.title("🚨 Railway Criminal Tracker Dashboard")

# Keep state to avoid duplicate uploads on reruns
if "last_uploaded_key" not in st.session_state:
    st.session_state.last_uploaded_key = None

# ---------- Layout: Left / Right ----------
col_left, col_right = st.columns([1, 1])

# ================= LEFT: Uploads & Controls =================
with col_left:
    st.subheader("📂 Controls & Uploads")

    uploaded_file = st.file_uploader(
        "Upload Criminal PDF or Image",
        type=["pdf", "jpg", "jpeg", "png"],
        help="Select a PDF or image that contains the criminal's face."
    )

    # Show selected file info (optional)
    if uploaded_file is not None:
        st.caption(f"Selected: **{uploaded_file.name}** ({uploaded_file.size} bytes)")

    # Upload happens ONLY when user clicks the button (prevents loops)
    if st.button("⬆️ Upload File", use_container_width=True, disabled=(uploaded_file is None)):
        try:
            # Build a unique key for this exact file selection to stop accidental re-uploads across reruns
            cur_key = f"{uploaded_file.name}:{uploaded_file.size}"
            if st.session_state.last_uploaded_key == cur_key:
                st.info("This file is already uploaded in the current session.")
            else:
                st.info("Uploading...")
                files = {
                    "file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type or "application/octet-stream")
                }
                resp = requests.post(f"{BACKEND_URL}/upload_file", files=files, timeout=30)
                if resp.ok:
                    data = {}
                    try:
                        data = resp.json()
                    except Exception:
                        pass
                    msg = data.get("message", "Uploaded successfully.") if isinstance(data, dict) else "Uploaded successfully."
                    st.success(msg)
                    st.session_state.last_uploaded_key = cur_key
                else:
                    st.error(f"❌ Upload failed (HTTP {resp.status_code}).")
        except Exception as e:
            st.error(f"❌ Upload error: {e}")

    st.divider()

    if st.button("▶️ Start CCTV Tracking", use_container_width=True):
        try:
            resp = requests.get(f"{BACKEND_URL}/start_feed", timeout=10)
            if resp.ok:
                data = {}
                try:
                    data = resp.json()
                except Exception:
                    pass
                st.success(data.get("message", "CCTV feed started."))
            else:
                st.error(f"❌ Could not start CCTV (HTTP {resp.status_code}).")
        except Exception as e:
            st.error(f"❌ Error starting feed: {e}")

    st.markdown(
        """
        <div style="border:2px solid #0af; padding:12px; border-radius:10px; 
                    text-align:center; margin-top:16px; background:#111; color:#0af;">
            🎥 Camera feed will open in a separate window.
        </div>
        """,
        unsafe_allow_html=True
    )

# ================= RIGHT: Live Logs =================
with col_right:
    st.subheader("📋 Live Logs")

    # Auto-refresh this area every 5 seconds
    st_autorefresh(interval=5000, key="logs_refresh")

    # Fetch logs once per render
    logs = []
    error_msg = None
    try:
        resp = requests.get(f"{BACKEND_URL}/get_logs", timeout=10)
        if resp.ok:
            logs = resp.json() or []
        else:
            error_msg = f"HTTP {resp.status_code}"
    except Exception as e:
        error_msg = str(e)

    if error_msg:
        st.error(f"⚠️ Error fetching logs: {error_msg}")

    # Helper to render a scrollable log box
    def render_log_box(filtered_logs, height=500, title_suffix=""):
        html = [
            f"""
            <div style='height:{height}px; overflow-y:auto; border:1px solid #444;
                        padding:10px; border-radius:8px; background:#111; color:#eee;'>
            """
        ]
        if not filtered_logs:
            html.append("<p style='opacity:0.8'>No logs yet.</p>")
        else:
            for log in reversed(filtered_logs[-25:]):  # show latest 25
                role = log.get("role", "")
                role_color = "red" if role == "CRIMINAL" else "lime"
                time_s = log.get("time", "")
                ident = log.get("identity", "")
                act = log.get("activity", "")
                html.append(
                    f"<p><b style='color:{role_color};'>[{time_s}] {ident} ({role})</b>: {act}</p>"
                )
        html.append("</div>")
        st.markdown("".join(html), unsafe_allow_html=True)

    # Two tabs: Criminal-only & All Activity
    tab_criminal, tab_all = st.tabs(["🔴 Criminal Logs", "📝 All Activity"])

    with tab_criminal:
        criminals_only = [l for l in logs if str(l.get("role", "")).upper() == "CRIMINAL"]
        render_log_box(criminals_only, height=500)

    with tab_all:
        render_log_box(logs, height=500)
