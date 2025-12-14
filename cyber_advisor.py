import streamlit as st
from groq import Groq
import sqlite3
import hashlib

# --- 1. CONFIGURATION GLOBALE ---
st.set_page_config(
    page_title="Cyber-Sentinel",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 🔒 SÉCURITÉ : CACHER LE MENU ET LE LOGO GITHUB ---
# C'est ici qu'on injecte du CSS pour masquer l'interface par défaut de Streamlit
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- 2. GESTION BASE DE DONNÉES (SQLite) ---
def init_db():
    """Initialise la base de données locale si elle n'existe pas"""
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
    """Transforme le mot de passe en empreinte SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    hashed_pw = hash_password(password)
    try:
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_pw))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
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

# --- 3. GESTION DE LA SESSION ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "Tu es un expert senior en cybersécurité (SISR). Réponds de manière technique."}
    ]
if "feedbacks" not in st.session_state:
    st.session_state.feedbacks = []

# --- 4. FONCTIONS LOGIN / LOGOUT ---
def login_success(username):
    st.session_state.authenticated = True
    st.session_state.username = username
    st.rerun()

def logout():
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.rerun()

# --- 5. PAGE D'ACCUEIL (LOGIN & SIGNUP) ---
def show_auth_page():
    st.markdown("""
        <style>
            .stTabs [data-baseweb="tab-list"] { gap: 2px; }
            .stTabs [data-baseweb="tab"] {
                height: 50px;
                white-space: pre-wrap;
                background-color: #f0f2f6;
                border-radius: 4px 4px 0px 0px;
                gap: 1px;
                padding-top: 10px;
                padding-bottom: 10px;
            }
            .stTabs [aria-selected="true"] {
                background-color: #FF4B4B;
                color: white;
            }
        </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.image("https://images.unsplash.com/photo-1555949963-ff9fe0c870eb", 
                 caption="Cyber-Sentinel Secure Database", use_container_width=True)

    with col2:
        st.title("🛡️ Portail Cyber-Sentinel")
        st.markdown("Accès restreint aux personnels autorisés.")

        tab1, tab2 = st.tabs(["🔑 Se connecter", "📝 Créer un compte"])

        with tab1:
            st.subheader("Connexion")
            login_user = st.text_input("Nom d'utilisateur", key="login_user")
            login_pass = st.text_input("Mot de passe", type="password", key="login_pass")
            if st.button("Entrer dans le système", key="btn_login"):
                if check_user(login_user, login_pass):
                    login_success(login_user)
                else:
                    st.error("Identifiants incorrects ou compte inexistant.")

        with tab2:
            st.subheader("Nouvel accès")
            new_user = st.text_input("Choisir un identifiant", key="new_user")
            new_pass = st.text_input("Choisir un mot de passe", type="password", key="new_pass")
            confirm_pass = st.text_input("Confirmer le mot de passe", type="password")
            if st.button("Créer le compte", key="btn_signup"):
                if new_pass != confirm_pass:
                    st.warning("Les mots de passe ne correspondent pas.")
                elif new_user == "":
                    st.warning("L'identifiant ne peut pas être vide.")
                else:
                    if create_user(new_user, new_pass):
                        st.success("✅ Compte créé ! Connectez-vous.")
                    else:
                        st.error("Utilisateur déjà existant.")

# --- 6. PAGE PRINCIPALE (APP) ---
def show_main_app():
    with st.sidebar:
        st.title(f"👤 {st.session_state.username}")
        st.caption("Statut : Connecté (Admin)")
        if st.button("Se déconnecter"):
            logout()
            
        st.divider()
        st.subheader("⭐ Feedback")
        with st.form("feedback_form"):
            note = st.slider("Note", 1, 5, 5)
            comment = st.text_area("Avis")
            if st.form_submit_button("Envoyer"):
                st.session_state.feedbacks.append({"user": st.session_state.username, "note": note, "comment": comment})
                st.success("Avis enregistré !")
        
        if st.session_state.feedbacks:
            st.divider()
            st.write("📢 **Derniers avis :**")
            for f in st.session_state.feedbacks[-3:]:
                st.info(f"**{f['user']}** ({f['note']}/5): {f['comment']}")

    st.title("🤖 Cyber-Sentinel AI")
    
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        client = Groq(api_key=api_key)
    except:
        st.error("Erreur Clé API.")
        st.stop()

    for msg in st.session_state.messages:
        if msg["role"] != "system":
            st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input("Votre requête..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        msg_container = st.chat_message("assistant")
        
        try:
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=st.session_state.messages,
                stream=True,
            )
            def generate_text():
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            response = msg_container.write_stream(generate_text())
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"Erreur : {e}")

# --- 7. NAVIGATION ---
if st.session_state.authenticated:
    show_main_app()
else:
    show_auth_page()
