import streamlit as st
from groq import Groq
import time

# --- 1. CONFIGURATION GLOBALE ---
st.set_page_config(
    page_title="Cyber-Sentinel",
    page_icon="🛡️",
    layout="wide", # On passe en mode large pour un look plus pro
    initial_sidebar_state="expanded"
)

# --- 2. GESTION DE LA SESSION (MÉMOIRE) ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "Tu es un expert senior en cybersécurité (SISR). Réponds de manière technique et précise."}
    ]
if "feedbacks" not in st.session_state:
    st.session_state.feedbacks = [] # Pour stocker les avis

# --- 3. FONCTIONS UTILITAIRES ---

def check_login(username, password):
    """Vérifie les identifiants (Simple pour la démo)"""
    # Dans la vraie vie, on utilise st.secrets ou une base de données
    if username == "admin" and password == "sio2025":
        st.session_state.authenticated = True
        st.rerun() # Recharge la page pour afficher le chat
    else:
        st.error("🛑 Identifiants incorrects (Essayez admin / sio2025)")

def logout():
    st.session_state.authenticated = False
    st.rerun()

# --- 4. PAGE DE CONNEXION (DESIGN) ---
def show_login_page():
    # CSS Personnalisé pour centrer et embellir le login
    st.markdown("""
        <style>
            .login-container {
                padding: 2rem;
                border-radius: 10px;
                background-color: #f0f2f6;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .stButton>button {
                width: 100%;
                background-color: #FF4B4B;
                color: white;
            }
        </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        # Image Cybernétique (URL publique)
        st.image("https://images.unsplash.com/photo-1550751827-4bd374c3f58b", 
                 caption="Secure Access Gateway", use_container_width=True)

    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True) # Espacement
        st.title("🔒 Portail Cyber-Sentinel")
        st.markdown("Veuillez vous authentifier pour accéder à l'IA SecOps.")
        
        username = st.text_input("Identifiant")
        password = st.text_input("Mot de passe", type="password")
        
        if st.button("Se connecter 🚀"):
            check_login(username, password)

# --- 5. PAGE PRINCIPALE (CHATBOT) ---
def show_main_app():
    # --- Sidebar (Menu Latéral) ---
    with st.sidebar:
        st.title("🛡️ Tableau de bord")
        st.success(f"Connecté en tant que : Admin")
        
        # Bouton Déconnexion
        if st.button("Se déconnecter"):
            logout()
            
        st.divider()
        
        # --- SYSTÈME D'AVIS ---
        st.subheader("⭐ Votre avis nous intéresse")
        with st.form("feedback_form"):
            note = st.slider("Notez la pertinence de l'IA", 1, 5, 5)
            commentaire = st.text_area("Commentaire (Optionnel)")
            submit_avis = st.form_submit_button("Envoyer l'avis")
            
            if submit_avis:
                # On enregistre l'avis dans la session
                st.session_state.feedbacks.append({"note": note, "comment": commentaire})
                st.toast("Merci pour votre retour !", icon="✅")

        # Affichage des statistiques d'avis (Simulation)
        if st.session_state.feedbacks:
            avg = sum(f['note'] for f in st.session_state.feedbacks) / len(st.session_state.feedbacks)
            st.metric("Note moyenne des utilisateurs", f"{avg:.1f}/5")

    # --- Zone Centrale (Chat) ---
    st.title("🤖 Cyber-Sentinel AI")
    st.caption("Assistant connecté au modèle Llama 3 via Groq LPU")

    # Connexion API
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        client = Groq(api_key=api_key)
    except:
        st.error("Erreur de clé API. Vérifiez les secrets.")
        st.stop()

    # Affichage historique
    for msg in st.session_state.messages:
        if msg["role"] != "system":
            st.chat_message(msg["role"]).write(msg["content"])

    # Zone de saisie
    if prompt := st.chat_input("Analysez un log, un script, une vulnérabilité..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        msg_container = st.chat_message("assistant")
        
        try:
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=st.session_state.messages,
                stream=True,
            )
            
            # Générateur de texte
            def generate_text():
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content

            response = msg_container.write_stream(generate_text())
            st.session_state.messages.append({"role": "assistant", "content": response})
            
        except Exception as e:
            st.error(f"Erreur API : {e}")

# --- 6. LOGIQUE DE NAVIGATION ---
if st.session_state.authenticated:
    show_main_app()
else:
    show_login_page()
