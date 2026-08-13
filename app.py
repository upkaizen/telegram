import streamlit as st
import requests

st.title("UPKAIZEN - Telegram Bot App")

if st.button("Enviar mensaje a Telegram 🚀"):
    try:
        token = st.secrets["TELEGRAM_TOKEN"]
        chat_id = st.secrets["TELEGRAM_CHAT_ID"]
        
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": "🚀 ¡Conexión exitosa desde UPKAIZEN Streamlit!",
            "parse_mode": "Markdown"
        }
        
        res = requests.post(url, json=payload, timeout=5)
        if res.status_code == 200:
            st.success("✅ ¡Mensaje publicado en Telegram!")
        else:
            st.error(f"❌ Error de Telegram: {res.text}")
    except Exception as e:
        st.error(f"❌ Revisa los Secrets en Streamlit: {e}")
