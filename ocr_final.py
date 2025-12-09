import streamlit as st
import pytesseract
from PIL import Image
from gtts import gTTS
import requests
import tempfile
import io

st.set_page_config(page_title="OCR Demo", layout="wide")
st.title("🔒 OCR → Text → Speech by SriVarshan, Viswesh and Sai Charan")
st.markdown("**6 Real Working Voices!**")

# FIXED VOICE OPTIONS - Actually work with gTTS
VOICES = {
    "👩 Female (US Fast)": ("com", False),
    "👩 Female (US Slow)": ("com", True),
    "🇬🇧 Female (UK Fast)": ("co.uk", False),
    "🇬🇧 Female (UK Slow)": ("co.uk", True),
    "🇦🇺 Female (Australia)": ("com.au", False),
    "🇮🇳 Female (India)": ("co.in", False)
}

OCR_API_URL = "https://api.ocr.space/parse/image"
API_KEY = "helloworld"

# Windows Tesseract fix
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def local_ocr(image):
    try:
        text = pytesseract.image_to_string(image).strip()
        return text, "✅ Local OCR (Private)"
    except:
        return "", "❌ Local failed"

def cloud_ocr(image_bytes):
    try:
        files = {'file': ('image.jpg', image_bytes, 'image/jpeg')}
        data = {'apikey': API_KEY, 'language': 'eng'}
        response = requests.post(OCR_API_URL, files=files, data=data)
        result = response.json()
        if result.get('ParsedResults'):
            return result['ParsedResults'][0]['ParsedText'].strip(), "☁️ Cloud OCR"
        return "", "❌ Cloud failed"
    except:
        return "", "❌ No internet"

def safe_ocr_pipeline(image):
    text, status = local_ocr(image)
    if text: return text, status
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='JPEG')
    return cloud_ocr(image_bytes.getvalue())

# Sidebar
with st.sidebar:
    st.header("🎤 Working Voices")
    selected_voice = st.selectbox("Real Voices:", list(VOICES.keys()), index=0)
    speed_note = st.info("**Speed**: Fast/Slow via voice selection")
    st.caption("`pip install streamlit pytesseract gtts pillow requests`")

# Main app (same as before)
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📸 Webcam / Upload")
    # camera_input = st.camera_input("Point at text!")
    uploaded_file = st.file_uploader("Or upload...", type=['png','jpg','jpeg'])
    
    current_image = None
    # if camera_input:
    #     current_image = Image.open(io.BytesIO(camera_input.getvalue()))
    #     st.image(current_image, caption="📷 Captured", width=400)
    # elif uploaded_file:
    #     current_image = Image.open(uploaded_file)
    #     st.image(current_image, caption="📁 Uploaded", width=400)

    if uploaded_file:
        current_image = Image.open(uploaded_file)
        st.image(current_image, caption="📁 Uploaded", width=400)

with col2:
    st.subheader("📄 Results")
    if 'results' in st.session_state:
        st.text_area(st.session_state.results['text'], height=250, disabled=True)
        st.info(f"**{st.session_state.results['status']}**")
    else:
        st.info("👆 Take photo first")

if st.button("🔍 Extract Text", type="primary", use_container_width=True):
    if current_image:
        with st.spinner("🔍 Scanning..."):
            text, status = safe_ocr_pipeline(current_image)
            if text:
                st.session_state.results = {'text': text, 'status': status}
                st.success("✅ Extracted!")
                st.rerun()
            else:
                st.error("❌ No text found!")

# FIXED SPEECH BUTTON - Real gTTS voices
if st.button("🔊 Read Aloud", type="secondary", use_container_width=True, disabled='results' not in st.session_state):
    if 'results' in st.session_state and st.session_state.results['text']:
        with st.spinner("🎤 Speaking..."):
            raw_text = st.session_state.results['text']

            clean_text = raw_text.replace('\n', ' ').replace('\r', '')

            clean_text = " ".join(clean_text.split())

            tld, slow = VOICES[selected_voice]
            tts = gTTS(
                clean_text, 
                lang='en',
                slow=slow,    # ✅ Works!
                tld=tld       # ✅ Works!
            )
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp:
                tts.save(tmp.name)
                st.audio(tmp.name)
            st.balloons()
            st.success(f"✅ **{selected_voice}** speaking!")

if st.button("🗑️ Clear", use_container_width=True):
    if 'results' in st.session_state:
        del st.session_state.results
    st.rerun()
