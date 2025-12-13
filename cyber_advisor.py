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
    st.error("Erreur : Clé API introuvable. Configurez les secrets.")
    st.stop()

# 3. Connexion au moteur IA
client = Groq(api_key=api_key)

# 4. Gestion de la mémoire (Historique de chat)
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "Tu es un expert en cybersécurité (SISR). Tu aides les administrateurs et auditeurs. Tes réponses sont techniques, précises et en français. Si tu donnes du code, commente-le pour expliquer la sécurité."}
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

    # Générer la réponse via Groq (Llama 3)
    msg_container = st.chat_message("assistant")
    stream = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=st.session_state.messages,
        stream=True,
    )
    response = msg_container.write_stream(stream)
    
    # Enregistrer la réponse
    st.session_state.messages.append({"role": "assistant", "content": response})
