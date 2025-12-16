import streamlit as st
from groq import Groq
import sqlite3
import hashlib
import re

st.set_page_config(
    page_title="Cyber-Sentinel V2",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

custom_css = """
    <style>
    /* Masquer le menu Streamlit par défaut */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Design sombre et accents rouges/verts cyber */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    .stTextInput > div > div > input {
        background-color: #262730;
        color: #FAFAFA;
    }
    /* Boutons personnalisés */
    .stButton > button {
        width: 100%;
        border-radius: 5px;
        font-weight: bold;
    }
    </style>
    """
st.markdown(custom_css, unsafe_allow_html=True)

CREATOR_NAME = "Moi (Le Créateur)"
CREATOR_EMAIL = "contact@cybersentinel.com"

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
    """Vérifie que l'identifiant est bien une adresse mail"""
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

def login_success(username):
    st.session_state.authenticated = True
    st.session_state.username = username
    st.rerun()

def logout():
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.rerun()

def show_auth_page():
    col1, col2 = st.columns([1, 1])

    with col1:
        st.image("https://images.unsplash.com/photo-1550751827-4bd374c3f58b", 
                 caption="Developed by " + CREATOR_NAME, use_container_width=True)
        st.info("⚠️ Accès réservé. Identifiant = Email obligatoire.")

    with col2:
        st.title("🛡️ Cyber-Sentinel V2")
        st.markdown(f"**Créé par : {CREATOR_NAME}**")
        
        tab1, tab2 = st.tabs(["🔑 Se connecter", "📝 Inscription"])

        with tab1:
            login_user = st.text_input("Email", key="login_user")
            login_pass = st.text_input("Mot de passe", type="password", key="login_pass")
            if st.button("ACCÉDER AU SYSTÈME", key="btn_login"):
                if check_user(login_user, login_pass):
                    login_success(login_user)
                else:
                    st.error("Identifiants incorrects.")

        with tab2:
            new_user = st.text_input("Votre Email (Obligatoire)", key="new_user")
            new_pass = st.text_input("Mot de passe", type="password", key="new_pass")
            confirm_pass = st.text_input("Confirmer le mot de passe", type="password")
            
            if st.button("🚀 CRÉER MON COMPTE SÉCURISÉ", key="btn_signup"):
                if new_pass != confirm_pass:
                    st.warning("Les mots de passe ne correspondent pas.")
                elif new_user == "":
                    st.warning("L'email est vide.")
                else:
                    status = create_user(new_user, new_pass)
                    if status == "SUCCESS":
                        st.success("✅ Compte créé ! Connectez-vous.")
                    elif status == "EMAIL_INVALID":
                        st.error("❌ Erreur : L'identifiant doit être une adresse email valide.")
                    elif status == "EXISTS":
                        st.error("Cet email est déjà enregistré.")

def show_main_app():
    with st.sidebar:
        st.title("Panel Utilisateur")
        st.write(f"Connecté en tant que : **{st.session_state.username}**")
        
        st.markdown("---")
        st.subheader("📞 Support")
        contact_body = f"Bonjour {CREATOR_NAME}, j'ai besoin d'aide..."
        st.markdown(f"""
            <a href="mailto:{CREATOR_EMAIL}?subject=Support Cyber-Sentinel&body={contact_body}" 
            style="text-decoration:none;">
            <button style="
                background-color:#4CAF50; color:white; padding:10px; 
                width:100%; border:none; border-radius:5px; cursor:pointer;">
                ✉️ Contacter le Créateur
            </button></a>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        if st.button("Se déconnecter"):
            logout()
            
        st.subheader("💬 Commentaires")
        with st.expander("Donner votre avis"):
            with st.form("feedback_form"):
                note = st.slider("Note", 1, 5, 5)
                comment = st.text_area("Votre message")
                if st.form_submit_button("Publier"):
                    st.session_state.feedbacks.append({
                        "user": st.session_state.username, 
                        "note": note, 
                        "comment": comment
                    })
                    st.success("Merci !")
        
        if st.session_state.feedbacks:
            st.write("---")
            st.write("**Derniers avis de la communauté :**")
            for f in st.session_state.feedbacks[::-1]: # Affiche du plus récent au plus vieux
                st.info(f"👤 **{f['user']}** ({f['note']}⭐)\n\n{f['comment']}")

    st.title("🤖 Cyber-Sentinel AI - Analyse")
    st.caption(f"Propulsé par Groq & Llama 3 - Design by {CREATOR_NAME}")

    # --- Upload de fichiers (PDF & ZIP) ---
    with st.expander("📂 Charger des documents (Logs, Rapports, ZIP)", expanded=True):
        uploaded_file = st.file_uploader("Glissez vos fichiers ici", type=['pdf', 'zip', 'txt', 'log'])
        if uploaded_file is not None:
            file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type, "FileSize": uploaded_file.size}
            st.write(file_details)
            st.success(f"Fichier '{uploaded_file.name}' chargé avec succès dans la mémoire tampon.")
            # Ici, tu pourras ajouter le code pour lire le contenu du fichier et l'envoyer à l'IA

    # --- Chatbot ---
    try:
        # Tente de récupérer la clé API
        api_key = st.secrets["GROQ_API_KEY"]
        client = Groq(api_key=api_key)
    except:
        st.error("⚠️ Clé API non trouvée. Configurez .streamlit/secrets.toml")
        st.stop()

    for msg in st.session_state.messages:
        if msg["role"] != "system":
            st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input("Posez votre question de cybersécurité..."):
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
            st.error(f"Erreur de communication : {e}")

# Lancement conditionnel
if st.session_state.authenticated:
    show_main_app()
else:
    show_auth_page()
