import streamlit as st
import requests
from bs4 import BeautifulSoup
from groq import Groq

st.set_page_config(page_title="UPKAIZEN Content Copilot", page_icon="⚡")

st.title("⚡ UPKAIZEN - Content Copilot (Telegram)")
st.write("Genera resúmenes ejecutivos optimizados con IA a partir de tu contenido para el canal de Telegram.")

# Inicializar cliente de Groq
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error(f"Error configurando la API de Groq: {e}")

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

if st.button("🤖 Generar borrador con IA"):
    with st.spinner("Leyendo web de UPKAIZEN y redactando post..."):
        contenido_web = extraer_contenido_web(target_url)
        
        if contenido_web:
            prompt = f"""
            Sos el Chief Content Officer de UPKAIZEN, experto en Excelencia Operacional y Lean.
            Redactá un post impactante y profesional para el canal de Telegram @OperationalExcellenceCommunity basado en este contenido extraído de {target_url}:

            CONTENIDO:
            {contenido_web[:3000]}

            REGLAS DE FORMATO CRÍTICAS:
            1. Usá texto plano limpio. Podés usar emojis y guiones para listas.
            2. NO uses caracteres especiales de Markdown raros que puedan romper el envío.
            3. Título enganchador con emoji.
            4. Resumí los 3 puntos/aprendizajes clave para directores de operaciones.
            5. Incluí CTA invitando a leer completo en {target_url}.
            6. Tono técnico, B2B, directo y de alto valor.
            """
            
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}]
                )
                st.session_state["borrador_post"] = response.choices[0].message.content
                st.success("¡Borrador generado con éxito!")
            except Exception as e:
                st.error(f"Error al generar con Groq: {e}")
        else:
            st.warning(f"No se pudo extraer contenido de {target_url}. Podés ingresar el texto manualmente.")

st.subheader("📝 Borrador para Telegram (Editar antes de publicar)")

contenido_final = st.text_area(
    "Revisá y modificá el mensaje:",
    value=st.session_state.get("borrador_post", "Hacé clic en 'Generar borrador'..."),
    height=280
)

# Selector de formato para evitar errores de parseo en Telegram
modo_envio = st.checkbox("Desactivar formato especial (Enviar como Texto Plano para evitar errores)", value=True)

if st.button("🚀 Publicar en Canal de Telegram"):
    if contenido_final.strip():
        try:
            token = st.secrets["TELEGRAM_TOKEN"]
            chat_id = st.secrets["TELEGRAM_CHAT_ID"]
            
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            
            payload = {
                "chat_id": chat_id,
                "text": contenido_final
            }
            
            # Solo agregar parse_mode si el usuario no eligió texto plano
            if not modo_envio:
                payload["parse_mode"] = "Markdown"
            
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
