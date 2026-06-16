import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
import requests

# =====================================================================
# 1. API KEY SETUP
# =====================================================================
API_KEY = "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" 
client = Groq(api_key=API_KEY)

# =====================================================================
# 2. NAVIGATION (SIDEBAR)
# =====================================================================
choice = st.sidebar.radio("Choose a Tool:", ["Chatbot", "Image Generator"])

# =====================================================================
# 3. CHATBOT INTERFACE
# =====================================================================
if choice == "Chatbot":
    st.header("Chat with shivbu's AI Assistance")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_prompt = None

    # --- INPUT 1: TEXT BOX ---
    text_input = st.chat_input("What is on your mind?")
    if text_input:
        user_prompt = text_input

    # --- INPUT 2: MIC RECORDER ---
    st.write("---")
    st.write("Voice Command use karein:")
    audio = mic_recorder(
        start_prompt="🎤 Record",
        stop_prompt="🛑 Stop",
        key='recorder'
    )

    if audio and "last_audio_id" not in st.session_state:
        st.session_state.last_audio_id = None

    if audio and audio['id'] != st.session_state.last_audio_id:
        st.session_state.last_audio_id = audio['id']
        audio_bytes = audio['bytes']
        with open("temp_audio.wav", "wb") as f:
            f.write(audio_bytes)
        
        try:
            with open("temp_audio.wav", "rb") as file:
                transcription = client.audio.transcriptions.create(
                    file=("temp_audio.wav", file.read()),
                    model="whisper-large-v3",
                )
            user_prompt = transcription.text
        except Exception as e:
            st.error(f"Audio samajhne mein dikkat aayi: {e}")

    # --- RESPONSE GENERATION ---
    if user_prompt:
        with st.chat_message("user"):
            st.markdown(user_prompt)
        st.session_state.messages.append({"role": "user", "content": user_prompt})

        with st.chat_message("assistant"):
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=st.session_state.messages
                )
                bot_response = response.choices[0].message.content
                st.markdown(bot_response)
                st.session_state.messages.append({"role": "assistant", "content": bot_response})
                st.rerun()
            except Exception as e:
                st.error(f"Groq API Error: {e}")

# =====================================================================
# 4. REAL IMAGE GENERATOR INTERFACE (NO-TOKEN SUPER FAST ENGINE)
# =====================================================================
elif choice == "Image Generator":
    st.header("AI Image Generator")
    st.write("Describe the image you want to create:")
    
    image_prompt = st.text_input("Enter image prompt:", placeholder="e.g., A beautiful nature view")
    generate_btn = st.button("Generate Image")
    
    if generate_btn and image_prompt:
        status_placeholder = st.empty()
        status_placeholder.info("⏳ Generating your image via Pollinations AI Engine...")
        
        try:
            # Pollinations AI direct URL format (Isme koi token ya key nahi lagti, block nahi hota)
            formatted_prompt = image_prompt.replace(" ", "%20")
            IMAGE_URL = f"https://image.pollinations.ai/prompt/{formatted_prompt}?width=1024&height=1024&nologo=true"
            
            # Direct Image stream generate karna
            response = requests.get(IMAGE_URL, timeout=90)
            status_placeholder.empty()

            if response.status_code == 200:
                st.success("🎉 Image generated successfully!")
                st.image(response.content, caption=image_prompt)
            else:
                st.error(f"😞 Server error code: {response.status_code}. Please try again.")
                
        except Exception as e:
            status_placeholder.empty()
            st.error(f"🤯 External connection issue: {e}. Ek baar mobile hotspot connect karke dekhein.")