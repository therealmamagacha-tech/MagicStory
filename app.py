import streamlit as st
from google import genai
import markdown
import asyncio
import edge_tts
import os

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="MagicStory", page_icon="🌙", layout="centered")

# --- 2. TEXTES (Langues) ---
CONTENT = {
    "Français": {
        "title": "🌙 MagicStory",
        "subtitle": "*(Le générateur d'histoires du soir)*",
        "section_hero": "### 1. Le Héros",
        "lbl_name": "Prénom",
        "ph_name": "Ex: Lucas",
        "lbl_age": "Âge",
        "lbl_companion": "Compagnon",
        "ph_companion": "Ex: Un ours",
        "lbl_object": "Objet spécial (Optionnel)",
        "ph_object": "Surprise...",
        "section_adventure": "### 2. L'Aventure",
        "lbl_place": "Lieu",
        "ph_place": "Ex: La lune",
        "lbl_villain": "Méchant / Obstacle (Optionnel)",
        "ph_villain": "Surprise...",
        "lbl_theme": "Leçon",
        "lbl_style": "Style",
        "btn_submit": "✨ Écrire l'histoire",
        "warning": "⚠️ Prénom et Lieu obligatoires !",
        "spinner_write": "🌙 L'IA écrit l'histoire...",
        "spinner_audio": "🎙️ La conteuse prépare sa voix...",
        "success_audio": "🎧 Écouter l'histoire :",
        "download": "📥 Télécharger l'histoire (Texte)",
        "story_for": "Histoire pour",
        "themes": ["Le Courage", "Le Partage", "La Patience", "L'Amitié", "La Curiosité"],
        "styles": ["Calme 💤", "Aventure ⚔️", "Rigolo 😂"],
        "voice": "fr-FR-VivienneMultilingualNeural",
        "lang_code": "Français"
    },
    "English": {
        "title": "🌙 MagicStory",
        "subtitle": "*(The Bedtime Story Generator)*",
        "section_hero": "### 1. The Hero",
        "lbl_name": "Name",
        "ph_name": "Ex: Lucas",
        "lbl_age": "Age",
        "lbl_companion": "Companion",
        "ph_companion": "Ex: A bear",
        "lbl_object": "Special Object (Optional)",
        "ph_object": "Surprise...",
        "section_adventure": "### 2. The Adventure",
        "lbl_place": "Location",
        "ph_place": "Ex: The Moon",
        "lbl_villain": "Villain / Obstacle (Optional)",
        "ph_villain": "Surprise...",
        "lbl_theme": "Lesson",
        "lbl_style": "Style",
        "btn_submit": "✨ Write the story",
        "warning": "⚠️ Name and Location are required!",
        "spinner_write": "🌙 The AI is writing the story...",
        "spinner_audio": "🎙️ Preparing the voice...",
        "success_audio": "🎧 Listen to the story:",
        "download": "📥 Download Story (Text)",
        "story_for": "Story for",
        "themes": ["Courage", "Sharing", "Patience", "Friendship", "Curiosity"],
        "styles": ["Calm 💤", "Adventure ⚔️", "Funny 😂"],
        "voice": "en-US-AvaMultilingualNeural",
        "lang_code": "English"
    }
}

# --- 3. DESIGN ---
st.markdown("""
<style>
    .stApp {
        background-color: #0f2027;
        background-image: linear-gradient(315deg, #0f2027 0%, #203a43 74%, #2c5364 100%);
        color: #ecf0f1;
    }
    h1, h3 { color: #f1c40f !important; font-family: 'Comic Sans MS', cursive; }
    label, p { color: #bdc3c7 !important; }
    .stButton>button {
        background-color: #e67e22; color: white; font-weight: bold; border-radius: 10px; border: none; padding: 12px; width: 100%;
    }
    .book-container { margin-top: 20px; padding: 10px; }
    .book-page {
        background-color: #fcf8e3; color: #2c3e50; padding: 50px; border-radius: 5px 15px 15px 5px;
        box-shadow: inset 30px 0 50px rgba(0,0,0,0.05), 0 10px 30px rgba(0,0,0,0.5);
        border-left: 8px solid #8d6e63; font-family: 'Georgia', serif; line-height: 1.9; font-size: 18px;
    }
    .book-page h1 { color: #c0392b !important; text-align: center; font-family: 'Brush Script MT', cursive; }
</style>
""", unsafe_allow_html=True)

# --- 4. CONNEXION API (NOUVELLE METHODE) ---
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except Exception:
    st.error("⚠️ Clé API manquante.")
    st.stop()

# --- 5. FONCTION AUDIO ---
async def generate_audio_file(text, filename, voice_id):
    communicate = edge_tts.Communicate(text, voice_id)
    await communicate.save(filename)

# --- 6. INTERFACE ---
with st.sidebar:
    st.markdown("### 🌍 Langue / Language")
    choice = st.radio("", ["🇫🇷 Français", "🇺🇸 English"], label_visibility="collapsed")

lang_key = "Français" if "Français" in choice else "English"
txt = CONTENT[lang_key]

st.title(txt["title"])
st.markdown(txt["subtitle"])

with st.form("story_form"):
    st.markdown(txt["section_hero"])
    c1, c2 = st.columns(2)
    with c1:
        child_name = st.text_input(txt["lbl_name"], placeholder=txt["ph_name"])
        age = st.slider(txt["lbl_age"], 2, 12, 5)
    with c2:
        companion = st.text_input(txt["lbl_companion"], placeholder=txt["ph_companion"])
        object_magic = st.text_input(txt["lbl_object"], placeholder=txt["ph_object"])

    st.markdown(txt["section_adventure"])
    c3, c4 = st.columns(2)
    with c3:
        place = st.text_input(txt["lbl_place"], placeholder=txt["ph_place"])
        villain = st.text_input(txt["lbl_villain"], placeholder=txt["ph_villain"])
    with c4:
        theme = st.selectbox(txt["lbl_theme"], txt["themes"])
        style = st.select_slider(txt["lbl_style"], options=txt["styles"])

    st.write("")
    submitted = st.form_submit_button(txt["btn_submit"])

# --- 7. GÉNÉRATION ---
if submitted:
    if not child_name or not place:
        st.warning(txt["warning"])
    else:
        with st.spinner(txt["spinner_write"]):
            try:
                # Prompt Engineering
                prompt = f"""
                Role: Storyteller for kids. Language: {txt['lang_code']}.
                Target audience age: {age}.
                
                Elements:
                - Hero: {child_name}
                - Companion: {companion if companion else 'Thinking friend'}
                - Magic Object: {object_magic if object_magic else 'Mystery item'}
                - Location: {place}
                - Villain/Obstacle: {villain if villain else 'Surprise obstacle'}
                - Theme: {theme}
                - Tone: {style}
                
                Format: Markdown. Title with emoji. Around 300 words. Gentle ending.
                Important: Write ONLY the story in {txt['lang_code']}.
                """
                
                # APPEL API CORRIGÉ (Modèle 1.5 + Client)
                response = client.models.generate_content(
                    model='gemini-1.5-flash', 
                    contents=prompt
                )
                
                story_text = response.text
                html_story = markdown.markdown(story_text)
                
                # Affiche Livre
                st.markdown(f"""
                <div class="book-container"><div class="book-page">
                    {html_story}
                    <br><hr style="border: 1px dashed #dcdcdc;">
                    <center style="color: #7f8c8d; font-size: 14px;">{txt['story_for']} {child_name}</center>
                </div></div>
                """, unsafe_allow_html=True)
                st.balloons()
                
                # Audio
                with st.spinner(txt["spinner_audio"]):
                    clean_text = story_text.replace("#", "").replace("*", "").replace("-", "")
                    audio_file = "story_audio.mp3"
                    
                    if os.path.exists(audio_file):
                        os.remove(audio_file)

                    asyncio.run(generate_audio_file(clean_text, audio_file, txt["voice"]))
                    
                    st.write("")
                    st.success(txt["success_audio"])
                    st.audio(audio_file)

                # Download
                st.download_button(txt["download"], story_text, f"story_{child_name}.md")

            except Exception as e:
                st.error(f"Error: {e}")
