import streamlit as st
from groq import Groq

# 1. Configuration de la page
st.set_page_config(page_title="Cyber-Advisor AI", page_icon="🛡️")
st.title("🛡️ Cyber-Advisor")
st.caption("Assistant Expert en Cybersécurité (Red & Blue Team)")

# 2. Récupération de la clé API (via les Secrets Streamlit)
try:
    api_key = st.secrets["GROQ_API_KEY"]
except:
    st.error("Erreur : Clé API introuvable. Avez-vous bien configuré les Secrets dans Streamlit ?")
    st.stop()

# 3. Connexion au moteur IA
client = Groq(api_key=api_key)

# 4. Gestion de la mémoire (Historique de chat)
if "messages" not in st.session_state:
    st.session_state.messages = [
        # Le prompt système définit la personnalité de l'IA
        {"role": "system", "content": "Tu es un expert senior en cybersécurité (SISR). Tu aides les administrateurs systèmes et les pentesters. Tes réponses sont techniques, précises et sécurisées. Tu parles français. Si tu donnes du code, commente-le pour expliquer les aspects sécurité."}
    ]

# 5. Affichage des anciens messages
for msg in st.session_state.messages:
    if msg["role"] != "system":
        st.chat_message(msg["role"]).write(msg["content"])

# 6. Zone de discussion
if prompt := st.chat_input("Pose ta question cyber..."):
    # Afficher la question de l'utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Générer la réponse via Groq
    msg_container = st.chat_message("assistant")
    try:
        stream = client.chat.completions.create(
            # Utilisation du dernier modèle stable (Llama 3.3 Versatile)
            model="llama-3.3-70b-versatile",
            messages=st.session_state.messages,
            stream=True,
        )
        response = msg_container.write_stream(stream)
        
        # Enregistrer la réponse
        st.session_state.messages.append({"role": "assistant", "content": response})
        
    except Exception as e:
        st.error(f"Erreur technique : {e}")
