import streamlit as st
from groq import Groq

# 1. Configuration de la page
st.set_page_config(page_title="Cyber-Advisor AI", page_icon="🛡️")
st.title("🛡️ Cyber-Advisor")
st.caption("Assistant Expert en Cybersécurité (Red & Blue Team)")

# 2. Récupération de la clé API
try:
    api_key = st.secrets["GROQ_API_KEY"]
except:
    st.error("Erreur : Clé API introuvable. Configurez les secrets.")
    st.stop()

# 3. Connexion au moteur IA
client = Groq(api_key=api_key)

# 4. Gestion de la mémoire
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "Tu es un expert en cybersécurité (SISR). Tu aides les administrateurs et auditeurs. Tes réponses sont techniques, précises et en français."}
    ]

# 5. Affichage des anciens messages
for msg in st.session_state.messages:
    if msg["role"] != "system":
        st.chat_message(msg["role"]).write(msg["content"])

# 6. Zone de discussion
if prompt := st.chat_input("Pose ta question cyber..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    msg_container = st.chat_message("assistant")
    
    try:
        # On demande la réponse à Groq
        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=st.session_state.messages,
            stream=True,
        )

        # --- LE CORRECTIF EST ICI ---
        # On crée un petit générateur pour extraire juste le texte du JSON
        def generate_text():
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        # On affiche le texte propre
        response = msg_container.write_stream(generate_text())
        
        # Enregistrer la réponse
        st.session_state.messages.append({"role": "assistant", "content": response})
        
    except Exception as e:
        st.error(f"Erreur technique : {e}")
