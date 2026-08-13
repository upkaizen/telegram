import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

st.set_page_config(page_title="UPKAIZEN Content Copilot", page_icon="⚡")

st.title("⚡ UPKAIZEN - Content Copilot (Telegram)")
st.write("Genera resúmenes ejecutivos optimizados con IA a partir de tu contenido para el canal de Telegram.")

# Configurar Gemini API
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-2.0-flash")
except Exception as e:
    st.error(f"Error configurando la API de Gemini: {e}")

# Selector de Fuente
fuente = st.selectbox(
    "Seleccioná la fuente de contenido:",
    ["Blog (https://upkaizen.com/blog)", 
     "Case Studies (https://upkaizen.com/case-studies/)", 
     "News (https://upkaizen.com/news/)"]
)

url_dict = {
    "Blog (https://upkaizen.com/blog)": "https://upkaizen.com/blog",
    "Case Studies (https://upkaizen.com/case-studies/)": "https://upkaizen.com/case-studies/",
    "News (https://upkaizen.com/news/)": "https://upkaizen.com/news/"
}

target_url = url_dict[fuente]

def extraer_contenido_web(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        
        titulos = [h.get_text(strip=True) for h in soup.find_all(['h1', 'h2', 'h3'])[:5]]
        parrafos = [p.get_text(strip=True) for p in soup.find_all('p')[:10]]
        
        texto_completo = "\n".join(titulos + parrafos)
        return texto_completo if len(texto_completo) > 100 else None
    except Exception as e:
        return None

if st.button("🤖 Generar borrador con IA (Gemini)"):
    with st.spinner("Leyendo web y redactando post con Gemini..."):
        contenido_web = extraer_contenido_web(target_url)
        
        if contenido_web:
            prompt = f"""
            Sos el Chief Content Officer de UPKAIZEN, experto en Excelencia Operacional y Lean.
            Redactá un post impactante y profesional para el canal de Telegram @OperationalExcellenceCommunity basado en este contenido extraído de {target_url}:

            CONTENIDO:
            {contenido_web[:3000]}

            REGLAS:
            1. Usá formato Markdown (negritas, listas).
            2. Título enganchador con emoji.
            3. Resumí los 3 puntos/aprendizajes clave para directores de operaciones.
            4. Incluí CTA invitando a leer completo en {target_url}.
            5. Tono técnico, B2B, directo y de alto valor.
            """
            
            try:
                response = model.generate_content(prompt)
                st.session_state["borrador_post"] = response.text
                st.success("¡Borrador generado con éxito!")
            except Exception as e:
                st.error(f"Error al generar con Gemini: {e}")
        else:
            st.warning(f"No se pudo extraer contenido de {target_url}. Podés ingresar el texto manualmente.")

st.subheader("📝 Borrador para Telegram (Editar antes de publicar)")

contenido_final = st.text_area(
    "Revisá y modificá el mensaje:",
    value=st.session_state.get("borrador_post", "Hacé clic en 'Generar borrador' o escribí tu mensaje acá..."),
    height=280
)

if st.button("🚀 Publicar en Canal de Telegram"):
    if contenido_final.strip():
        try:
            token = st.secrets["TELEGRAM_TOKEN"]
            chat_id = st.secrets["TELEGRAM_CHAT_ID"]
            
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": contenido_final,
                "parse_mode": "Markdown"
            }
            
            res = requests.post(url, json=payload, timeout=5)
            if res.status_code == 200:
                st.balloons()
                st.success("✅ ¡Publicado exitosamente en @OperationalExcellenceCommunity!")
            else:
                st.error(f"❌ Error de Telegram: {res.text}")
        except Exception as e:
            st.error(f"❌ Error de credenciales: {e}")
    else:
        st.warning("El texto está vacío.")
