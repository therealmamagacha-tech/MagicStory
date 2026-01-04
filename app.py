import streamlit as st
import google.generativeai as genai
import markdown
import asyncio
import edge_tts

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="MagicStory", page_icon="🌙", layout="centered")

# --- 2. DESIGN ---
st.markdown("""
<style>
    .stApp {
        background-color: #0f2027;
        background-image: linear-gradient(315deg, #0f2027 0%, #203a43 74%, #2c5364 100%);
        color: #ecf0f1;
    }
    h1, h3 { color: #f1c40f !important; font-family: 'Comic Sans MS', cursive; text-shadow: 0px 2px 5px rgba(0,0,0,0.5); }
    label, p { color: #bdc3c7 !important; }
    .stButton>button {
        background-color: #e67e22; color: white; font-weight: bold; border-radius: 10px; border: none; padding: 12px; width: 100%;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3); transition: all 0.3s;
    }
    .stButton>button:hover { background-color: #d35400; transform: translateY(-2px); }
    
    .book-container { margin-top: 20px; padding: 10px; }
    .book-page {
        background-color: #fcf8e3; color: #2c3e50; padding: 50px; border-radius: 5px 15px 15px 5px;
        box-shadow: inset 30px 0 50px rgba(0,0,0,0.05), 0 10px 30px rgba(0,0,0,0.5);
        border-left: 8px solid #8d6e63; font-family: 'Georgia', serif; line-height: 1.9; font-size: 18px;
    }
    .book-page h1, .book-page h2 { color: #c0392b !important; text-align: center; font-family: 'Brush Script MT', cursive; margin-bottom: 25px; }
    .book-page p { color: #2c3e50 !important; text-align: justify; }
    
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 3. API ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ Clé API manquante.")
    st.stop()

# --- 4. FONCTION VOCALE (VOIX HUMAINE) ---
async def generate_audio_file(text):
    """Génère un fichier audio avec une voix neurale naturelle"""
    # Voix disponibles : 'fr-FR-VivienneMultilingualNeural' (Femme), 'fr-FR-RemyMultilingualNeural' (Homme)
    VOICE = "fr-FR-VivienneMultilingualNeural" 
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save("story_audio.mp3")

# --- 5. INTERFACE ---
st.title("🌙 MagicStory")
st.markdown("*(Le générateur d'histoires du soir)*")

with st.form("story_form"):
    st.markdown("### 1. Le Héros")
    c1, c2 = st.columns(2)
    with c1:
        child_name = st.text_input("Prénom", placeholder="Ex: Lucas")
        age = st.slider("Âge", 2, 12, 5)
    with c2:
        companion = st.text_input("Compagnon", placeholder="Ex: Un ours")
        object_magic = st.text_input("Objet spécial (Optionnel)", placeholder="Surprise...")

    st.markdown("### 2. L'Aventure")
    c3, c4 = st.columns(2)
    with c3:
        place = st.text_input("Lieu", placeholder="Ex: La lune")
        villain = st.text_input("Méchant / Obstacle (Optionnel)", placeholder="Surprise...")
    with c4:
        theme = st.selectbox("Leçon", ["Le Courage", "Le Partage", "La Patience", "L'Amitié", "La Curiosité"])
        style = st.select_slider("Style", options=["Calme 💤", "Aventure ⚔️", "Rigolo 😂"])

    st.write("")
    submitted = st.form_submit_button("✨ Écrire l'histoire")

# --- 6. GÉNÉRATION ---
if submitted:
    if not child_name or not place:
        st.warning("⚠️ Prénom et Lieu obligatoires !")
    else:
        with st.spinner("🌙 L'IA écrit l'histoire..."):
            try:
                model='gemini-1.5-flash',
                
                # Prompt
                villain_prompt = villain if villain else "Un obstacle surprenant"
                object_prompt = object_magic if object_magic else "Un objet mystérieux"
                companion_prompt = companion if companion else "Un ami imaginaire"

                prompt = f"""
                Rédige une histoire pour un enfant de {age} ans.
                - Héros : {child_name} ({age} ans)
                - Ami : {companion_prompt}
                - Objet : {object_prompt}
                - Lieu : {place}
                - Obstacle : {villain_prompt}
                - Morale : {theme}
                - Ton : {style}
                
                Format Markdown. Titre avec émoji. ~300 mots. Fin douce.
                """
                
                response = model.generate_content(prompt)
                story_text = response.text
                html_story = markdown.markdown(story_text)
                
                # --- AFFICHAGE LIVRE ---
                st.markdown(f"""
                <div class="book-container"><div class="book-page">
                    {html_story}
                    <br><hr style="border: 1px dashed #dcdcdc;">
                    <center style="color: #7f8c8d; font-size: 14px;">Histoire pour {child_name}</center>
                </div></div>
                """, unsafe_allow_html=True)
                st.balloons()
                
                # --- AUDIO NEURAL (REALISTE) ---
                with st.spinner("🎙️ La conteuse prépare sa voix (c'est beaucoup plus joli !)..."):
                    # Nettoyage du texte pour la lecture
                    clean_text = story_text.replace("#", "").replace("*", "").replace("-", "")
                    
                    # Appel asynchrone pour générer l'audio
                    asyncio.run(generate_audio_file(clean_text))
                    
                    st.write("")
                    st.success("🎧 Écouter la conteuse :")
                    st.audio("story_audio.mp3", format='audio/mp3')

                # --- TÉLÉCHARGEMENT ---
                st.write("")
                st.download_button(
                    label="📥 Télécharger l'histoire (Texte)",
                    data=story_text,
                    file_name=f"histoire_{child_name}.md",
                    mime="text/markdown"
                )

            except Exception as e:
                st.error(f"Erreur : {e}")