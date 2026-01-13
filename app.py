import streamlit as st
import requests

# ======================================================
# KONFIGURASI HALAMAN
# ======================================================
st.set_page_config(
    page_title="My AI Chatbot",
    page_icon="💬",
    layout="centered"
)

# ======================================================
# STYLE CHAT (Bubble Chat UI)
# ======================================================
st.markdown("""
<style>
div[data-testid="stChatMessage"] {
    margin-bottom: 14px;
}

/* Pesan dari user (kanan) */
div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    flex-direction: row-reverse;
}

div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) .stMarkdown {
    background: #4f46e5;
    color: white;
    padding: 14px 18px;
    border-radius: 18px 18px 6px 18px;
}

/* Pesan dari AI (kiri) */
div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) .stMarkdown {
    background: #1f2937;
    color: white;
    padding: 14px 18px;
    border-radius: 18px 18px 18px 6px;
}
</style>
""", unsafe_allow_html=True)

# ======================================================
# FUNGSI PEMBERSIH OUTPUT AI
# ======================================================
def clean_ai_response(text: str) -> str:
    """
    Membersihkan token aneh yang kadang muncul
    dari output model OpenRouter (Mistral, DeepSeek, dll)
    """
    unwanted_tokens = [
        "<s>",
        "</s>",
        "[/s]",
        "[OUTST]",
        "[OUT]",
        "<s> [OUTST]"
    ]

    for token in unwanted_tokens:
        text = text.replace(token, "")

    return text.strip()

# ======================================================
# SIDEBAR (Pengaturan Chatbot)
# ======================================================
with st.sidebar:
    st.header("⚙️ Pengaturan Chatbot")

    api_key = st.text_input(
        "OpenRouter API Key",
        type="password",
        placeholder="sk-or-v1-..."
    )

    model = st.selectbox(
        "Model AI",
        [
            "mistralai/mistral-7b-instruct:free",
            "deepseek/deepseek-chat-v3-0324:free",
            "meta-llama/llama-3.1-8b-instruct:free"
        ]
    )

    if st.button("🔄 Reset Chat"):
        st.session_state.chat_log = []
        st.rerun()

# ======================================================
# HEADER UTAMA
# ======================================================
st.title("💬 My AI Chatbot")
st.caption("Chatbot AI sederhana menggunakan Streamlit dan OpenRouter")

# ======================================================
# SESSION STATE
# ======================================================
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []

if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = {
        "role": "system",
        "content": "Kamu adalah AI assistant yang ramah, jelas, dan membantu mahasiswa."
    }

# ======================================================
# CEK API KEY
# ======================================================
if not api_key:
    st.info("Masukkan API Key OpenRouter terlebih dahulu.")
    st.stop()

# ======================================================
# TAMPILKAN RIWAYAT CHAT
# ======================================================
for message in st.session_state.chat_log:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ======================================================
# INPUT PESAN USER
# ======================================================
user_message = st.chat_input("Tulis pesan kamu...")

if user_message:
    # tampilkan pesan user
    with st.chat_message("user"):
        st.markdown(user_message)

    st.session_state.chat_log.append({
        "role": "user",
        "content": user_message
    })

    # ambil 10 pesan terakhir agar tidak boros token
    recent_messages = st.session_state.chat_log[-10:]

    payload = {
        "model": model,
        "messages": [
            st.session_state.system_prompt,
            *recent_messages
        ],
        "temperature": 0.7,
        "max_tokens": 800
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "My Streamlit AI Chatbot"
    }

    with st.chat_message("assistant"):
        with st.spinner("AI sedang menjawab..."):
            try:
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                response.raise_for_status()

                raw_answer = response.json()["choices"][0]["message"]["content"]
                ai_answer = clean_ai_response(raw_answer)

            except requests.exceptions.RequestException:
                ai_answer = "⚠️ Terjadi gangguan koneksi ke AI. Silakan coba lagi."

            st.markdown(ai_answer)

    st.session_state.chat_log.append({
        "role": "assistant",
        "content": ai_answer
    })
