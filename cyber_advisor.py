import streamlit as st
from groq import Groq
import sqlite3
import hashlib
import re

# --- CONFIGURATION DU DESIGN (Layout) ---
st.set_page_config(
    page_title="Cyber-Sentinel V3",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS PERSONNALISÉ (LE GROS CHANGEMENT FRONT-END) ---
# On injecte du CSS avancé pour un look Cyberpunk Premium
custom_css = """
    <style>
    /* --- Masquer les éléments Streamlit par défaut --- */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* --- Fond Global Animé (Optionnel : si trop lourd, retirer le linear-gradient) --- */
    .stApp {
        background: linear-gradient(to bottom right, #0a0e17, #1a1f35);
    }

    /* --- TYPOGRAPHIE & TITRES --- */
    h1, h2, h3 {
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 800;
        letter-spacing: 1px;
        color: #ffffff !important;
        text-shadow: 0 0 10px rgba(0, 229, 255, 0.5); /* Effet Neon Glow */
    }
    
    /* --- BOUTONS CYBER --- */
    /* On cible tous les boutons pour leur donner un look futuriste */
    .stButton > button {
        width: 100%;
        background: linear-gradient(45deg, #00c6ff, #0072ff);
        border: none;
        color: white;
        padding: 12px 24px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        font-weight: bold;
        margin: 4px 2px;
        transition-duration: 0.4s;
        cursor: pointer;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(0, 198, 255, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(45deg, #0072ff, #00c6ff);
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.7); /* Lueur intense au survol */
        transform: translateY(-2px);
    }

    /* --- CHAMPS DE SAISIE (INPUTS) --- */
    /* Style "terminal" sombre avec bordure néon au focus */
    .stTextInput > div > div > input, .stPasswordInput > div > div > input, .stTextArea > div > div > textarea {
        background-color: #131c2e !important;
        color: #00e5ff !important; /* Texte couleur cyan */
        border: 1px solid #2c3e50;
        border-radius: 5px;
    }
    
    /* Quand on clique dans un champ */
    .stTextInput > div > div > input:focus, .stPasswordInput > div > div > input:focus {
        border-color: #00e5ff !important;
        box-shadow: 0 0 10px rgba(0, 229, 255, 0.5);
    }

    /* --- SIDEBAR (Barre latérale) --- */
    section[data-testid="stSidebar"] {
        background-color: #0d1321;
        border-right: 1px solid #1e2a3a;
        box-shadow: 5px 0 15px rgba(0,0,0,0.3);
    }

    /* --- TABS (Onglets Connexion/Inscription) --- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #131c2e;
        border-radius: 8px;
        color: #8892b0;
        border: 1px solid transparent;
        transition: all 0.3s ease;
    }

    .stTabs [aria-selected="true"] {
        background-color: rgba(0, 229, 255, 0.1) !important;
        color: #00e5ff !important;
        border: 1px solid #00e5ff !important;
        box-shadow: inset 0 0 10px rgba(0, 229, 255, 0.2);
    }
    
    /* --- MESSAGES CHATBOT --- */
    .stChatMessage {
        background-color: rgba(19, 28, 46, 0.8);
        border: 1px solid #2c3e50;
        border-radius: 10px;
        padding: 15px;
    }
    /* Différencier User et Assistant */
    [data-testid="stChatMessageAvatarUser"] {
        background-color: #0072ff;
    }
    [data-testid="stChatMessageAvatarAssistant"] {
        background-color: #00e5ff;
    }

    </style>
    """
st.markdown(custom_css, unsafe_allow_html=True)

# --- IDENTITÉ DU CRÉATEUR ---
CREATOR_NAME = "Lionnel (Cyber-Expert)" 
CREATOR_EMAIL = "contact@cybersentinel.com"

# --- GESTION DE LA BASE DE DONNÉES (Inchangé) ---
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)

def create_user(username, password):
    if not is_valid_email(username):
        return "EMAIL_INVALID"
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    hashed_pw = hash_password(password)
    try:
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_pw))
        conn.commit()
        return "SUCCESS"
    except sqlite3.IntegrityError:
        return "EXISTS"
    finally:
        conn.close()

def check_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    hashed_pw = hash_password(password)
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, hashed_pw))
    result = c.fetchone()
    conn.close()
    return result is not None

init_db()

# --- GESTION DE L'ÉTAT (SESSION) (Inchangé) ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "Tu es un expert senior en cybersécurité (SISR). Réponds de manière technique, concise et professionnelle. Utilise du markdown pour formater tes réponses."}
    ]
if "feedbacks" not in st.session_state:
    st.session_state.feedbacks = []

def login_success(username):
    st.session_state.authenticated = True
    st.session_state.username = username
    st.rerun()

def logout():
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.rerun()

# --- PAGE D'AUTHENTIFICATION (Design amélioré) ---
def show_auth_page():
    # Utilisation de conteneurs pour centrer et styliser
    col_spacer1, col_main, col_spacer2 = st.columns([1, 2, 1])

    with col_main:
        st.markdown(f"<h1 style='text-align: center;'>🛡️ CYBER-SENTINEL V3</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: #00e5ff;'>Developed by {CREATOR_NAME}</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        # Utilisation d'une image plus "tech"
        st.image("https://img.freepik.com/free-vector/dark-gradient-background-with-copy-space_53876-99345.jpg?t=st=1715000000~exp=1715003600~hmac=123", 
                 caption="Secure Gateway Access Protocol", use_container_width=True)

        
        st.info("🔒 Accès restreint. Identifiant = Email obligatoire.")

        tab1, tab2 = st.tabs(["🔑 Authentification", "📝 Initialisation Compte"])

        with tab1:
            st.subheader("Connexion au terminal")
            login_user = st.text_input("Email", key="login_user", placeholder="agent@cybersentinel.com")
            login_pass = st.text_input("Mot de passe", type="password", key="login_pass")
            st.write("") # Spacer
            if st.button("❯ INITIALISER LA CONNEXION", key="btn_login"):
                if check_user(login_user, login_pass):
                    login_success(login_user)
                else:
                    st.error("⛔ Échec d'authentification.")

        with tab2:
            st.subheader("Création de profil d'agent")
            new_user = st.text_input("Votre Email (Obligatoire)", key="new_user", placeholder="nouveau.membre@email.com")
            new_pass = st.text_input("Mot de passe", type="password", key="new_pass")
            confirm_pass = st.text_input("Confirmer le mot de passe", type="password")
            
            st.write("") # Spacer
            if st.button("❯ GÉNÉRER LES ACCÈS", key="btn_signup"):
                if new_pass != confirm_pass:
                    st.warning("⚠️ Erreur de concordance des mots de passe.")
                elif new_user == "":
                    st.warning("⚠️ Champ email vide.")
                else:
                    status = create_user(new_user, new_pass)
                    if status == "SUCCESS":
                        st.success("✅ Profil agent créé avec succès. Connectez-vous.")
                    elif status == "EMAIL_INVALID":
                        st.error("❌ Format d'email invalide détecté.")
                    elif status == "EXISTS":
                        st.error("⛔ Cet identifiant est déjà actif dans la base.")

# --- APPLICATION PRINCIPALE (Design amélioré) ---
def show_main_app():
    # --- Sidebar ---
    with st.sidebar:
        st.title("🌐 CONTROL PANEL")
        st.markdown(f"Agent connecté :  \n**<span style='color:#00e5ff'>{st.session_state.username}</span>**", unsafe_allow_html=True)
        st.caption("Niveau d'accréditation : ALPHA")
        
        st.markdown("---")
        st.subheader("📞 Support Ops")
        contact_body = f"Bonjour {CREATOR_NAME}, requête de support niveau 2..."
        # Bouton HTML personnalisé pour le mail
        st.markdown(f"""
            <a href="mailto:{CREATOR_EMAIL}?subject=Support Cyber-Sentinel&body={contact_body}" 
            style="text-decoration:none; width:100%;">
            <div style="background: linear-gradient(45deg, #2ecc71, #27ae60); color:white; padding:12px; 
                text-align:center; border-radius:8px; font-weight:bold; box-shadow: 0 4px 10px rgba(46, 204, 113, 0.3);">
                ✉️ CONTACTER LE HQ
            </div></a>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        if st.button("❯ TERMINER LA SESSION"):
            logout()
            
        st.subheader("💬 Flux de Feedback")
        with st.expander("Soumettre un rapport"):
            with st.form("feedback_form"):
                note = st.slider("Niveau de satisfaction", 1, 5, 5)
                comment = st.text_area("Message du rapport")
                if st.form_submit_button("Envoyer au commandement"):
                    st.session_state.feedbacks.append({
                        "user": st.session_state.username, 
                        "note": note, 
                        "comment": comment
                    })
                    st.success("Rapport transmis.")
        
        if st.session_state.feedbacks:
            st.write("---")
            st.markdown("**<span style='color:#00e5ff'>Derniers rapports :</span>**", unsafe_allow_html=True)
            for f in st.session_state.feedbacks[::-1]:
                st.markdown(f"""
                    <div style='background-color: #131c2e; padding: 10px; border-radius: 5px; margin-bottom: 10px; border-left: 3px solid #00e5ff;'>
                        <small style='color: #8892b0;'>Agent: {f['user']} ({f['note']}⭐)</small><br>
                        {f['comment']}
                    </div>
                    """, unsafe_allow_html=True)

    # --- Zone Principale ---
    st.markdown(f"<h1 style='text-align: left;'>🤖 CYBER-SENTINEL AI <span style='font-size:0.5em; color:#00e5ff;'>V3.1</span></h1>", unsafe_allow_html=True)
    st.caption(f"Interface neuronale propulsée par Groq & Llama 3 - Design et architecture par {CREATOR_NAME}")

    # --- Upload ---
    with st.expander("📂 MODULE D'INGESTION DE DONNÉES (Logs, ZIP, PDF)", expanded=False):
        uploaded_file = st.file_uploader("Glissez vos fichiers preuves ici pour analyse", type=['pdf', 'zip', 'txt', 'log', 'csv'])
        if uploaded_file is not None:
            st.markdown(f"""
                <div style='background-color: rgba(46, 204, 113, 0.1); padding: 10px; border-radius: 5px; border: 1px solid #2ecc71;'>
                    ✅ <b>Fichier ingéré dans le tampon mémoire :</b> {uploaded_file.name} <br>
                    Taille: {uploaded_file.size} bytes | Type: {uploaded_file.type}
                </div>
                """, unsafe_allow_html=True)

    st.divider()

    # --- Chatbot Section ---
    # Conteneur pour les messages avec une hauteur max et scroll (pour éviter que la page ne s'étire trop)
    chat_container = st.container(height=500)

    with chat_container:
        for msg in st.session_state.messages:
            if msg["role"] != "system":
                st.chat_message(msg["role"]).write(msg["content"])

    # Zone de saisie (Input en bas)
    if prompt := st.chat_input("Entrez votre requête d'analyse ou commande..."):
        # On écrit le message user dans le conteneur
        with chat_container:
             st.chat_message("user").write(prompt)
             msg_container = st.chat_message("assistant")
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        try:
            # Tentative de récupération de clé silencieuse
            api_key = st.secrets.get("GROQ_API_KEY", None)
            if not api_key:
                 with chat_container:
                    st.error("⚠️ Erreur Critique : Clé d'API Groq non détectée dans les secrets.")
                    st.stop()
            
            client = Groq(api_key=api_key)

            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=st.session_state.messages,
                stream=True,
            )
            def generate_text():
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            
            # On écrit la réponse dans le conteneur
            with chat_container:
                response = msg_container.write_stream(generate_text())
            
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
             with chat_container:
                st.error(f"❌ Erreur de communication neuronale : {e}")

# Lancement conditionnel
if st.session_state.authenticated:
    show_main_app()
else:
    show_auth_page()
