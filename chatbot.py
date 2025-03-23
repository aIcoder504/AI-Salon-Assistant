import streamlit as st
from board import conversational_ai

st.title("💬 AI Salon Assistant")
st.write("Hello! I am your AI Salon Assistant. Click 'Start Talking' to begin.")

# ✅ Add session state to track if AI is listening
if "listening" not in st.session_state:
    st.session_state.listening = False

# 🎙️ Start Talking Button
if st.button("🎙️ Start Talking"):
    st.session_state.listening = True
    st.write("🎙️ Listening... Speak now.")

# 🛑 Stop Talking Button
if st.button("🛑 Stop Talking"):
    st.session_state.listening = False
    st.write("👋 Conversation stopped. Click 'Start Talking' to continue.")

# ✅ Auto-loop for continuous conversation (only if listening is True)
while st.session_state.listening:
    user_input = conversational_ai(first_time=False)  # Get user input
    
    if not user_input:  # 🔹 Stop if user stays silent for 5 seconds
        st.write("👋 Conversation ended. Click 'Start Talking' to continue.")
        st.session_state.listening = False
        break  # Exit loop
    
    st.write(f"🗣️ You: {user_input}")  # Show user input
