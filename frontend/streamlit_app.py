import streamlit as st
import requests

# ---------------- CONFIG ----------------
API_URL = "http://127.0.0.1:8000/api/predict/"

st.set_page_config(
    page_title="Phishing URL Detection",
    page_icon="🔐",
    layout="centered"
)

# ---------------- TITLE ----------------
st.title("🔐 Phishing URL Detection System")
st.write(
    "Enter a website URL to check whether it is **Phishing** or **Legitimate** "
    "using a Machine Learning + Rule-Based security system."
)

st.divider()

# ---------------- INPUT ----------------
raw_url = st.text_input(
    "🌐 Enter Website URL",
    placeholder="example: google.com or https://secure-login-paypal.com"
)

url = raw_url.strip()

# ---- Basic validation ----
if url:
    if "." not in url:
        st.error("❌ Invalid URL. Please enter a full domain like google.com")
        st.stop()

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

st.caption(f"🔍 URL sent to API: `{url}`")


 
 

# ---------------- BUTTON ----------------
check_btn = st.button("🔍 Check URL")

# ---------------- API CALL ----------------
if check_btn:
    if not url:
        st.warning("⚠️ Please enter a URL")
    else:
        with st.spinner("Analyzing URL..."):
            try:
                response = requests.post(
                    API_URL,
                    json={"url": url},
                    headers={"Content-Type": "application/json"},
                    timeout=5
                )

                # ---- DEBUG (same as Postman) ----
                st.caption(f"🔁 API Status Code: {response.status_code}")
                st.caption(f"📦 Raw API Response: {response.text}")

                if response.status_code == 200:
                    result = response.json()

                    prediction = result.get("prediction")
                    confidence = result.get("confidence")
                    reason = result.get("reason")

                    st.divider()

                    # -------- RESULT DISPLAY --------
                    if "phishing" in prediction.lower():
                        st.error("🚨 PHISHING WEBSITE DETECTED")
                    else:
                        st.success("✅ LEGITIMATE WEBSITE")

                    st.markdown(f"**🔎 Prediction:** `{prediction}`")
                    st.markdown(f"**📊 Confidence:** `{confidence * 100:.1f}%`")

                    if reason:
                        st.markdown(f"**⚠️ Reason:** {reason}")

                    # -------- CONFIDENCE BAR --------
                    st.progress(float(confidence))

                else:
                    st.error("❌ API returned an error")

            except requests.exceptions.RequestException as e:
                st.error(f"❌ Cannot connect to backend API\n\n{e}")
