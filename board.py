import openai
import speech_recognition as sr
import os
import tempfile
import threading
from dotenv import load_dotenv
from gtts import gTTS
from playsound import playsound
from ai_booking import book_appointment  # Import Google Sheets Booking Function

# ===================================
#  🔑 SECTION 1: LOAD API KEY
# ===================================
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    print("🔑 OpenAI API Key not found. Set it in a .env file.")
    exit(1)

# ✅ Initialize OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# ===================================
#  🗣️ SECTION 2: TEXT-TO-SPEECH (MAKE AI TALK)
# ===================================
def speak_text(text):
    """Converts text to speech and plays it."""
    print(f"🤖 AI (Speaking): {text}")  
    tts = gTTS(text=text, lang="en")
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_file.name)
    playsound(temp_file.name)
    os.remove(temp_file.name)

# ===================================
#  🎤 SECTION 3: SPEECH RECOGNITION (LISTEN TO USER)
# ===================================
def record_audio():
    """Records user audio and converts it to text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙️ Listening... (You can stay silent for 5s to stop)")
        recognizer.adjust_for_ambient_noise(source, duration=1.5)
        
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)  # Stop after 5s silence
            print("📝 Recognizing speech...")
            return recognizer.recognize_google(audio).lower()  # Convert to lowercase
        except sr.UnknownValueError:
            return "Sorry, I couldn't understand that."
        except sr.RequestError:
            return "Speech service is unavailable."
        except sr.WaitTimeoutError:  # 🔹 New: Handle silence properly
            return None  # Return None to stop listening

from datetime import datetime
from ai_booking import book_appointment, get_available_slots  # Import functions

# ===================================
#  🕒 FUNCTION TO CONVERT TIME INPUT
# ===================================
def convert_time_format(time_input):
    """
    Converts various time formats into 'HH:MM' (24-hour format) to match available slots.
    Example: '4 PM' → '16:00', '2:30 PM' → '14:30', '1600' → '16:00'
    """
    try:
        # ✅ Check if time is already in correct "HH:MM" format
        if ":" in time_input and len(time_input) <= 5:
            return time_input

        # ✅ Handle 24-hour time format (e.g., "1600" → "16:00")
        if time_input.isdigit() and len(time_input) == 4:
            return f"{time_input[:2]}:{time_input[2:]}"

        # ✅ Convert 12-hour format (e.g., "4 PM" → "16:00")
        parsed_time = datetime.strptime(time_input, "%I %p").strftime("%H:%M")
        return parsed_time

    except ValueError:
        return None  # ❌ Return None if the time format is invalid

# ===================================
#  📅 SECTION 4: AUTOMATED BOOKING HANDLER (FIXED)
# ===================================
def handle_booking():
    """Handles booking fully via voice conversation, ensuring proper slot availability check."""
    speak_text("Let's book your appointment. What's your name?")
    name = record_audio()
    if not name:
        return

    speak_text("What date would you like to book? Say like March 25 or 25th March.")
    date = record_audio()
    if not date:
        return

    available_slots = get_available_slots(date)  # ✅ Get available slots before asking time
    if not available_slots:
        speak_text("Sorry, no slots are available on this date. Please choose another day.")
        return handle_booking()

    # ✅ Fix: Ask for time only from available slots
    while True:
        speak_text(f"Available slots are: {', '.join(available_slots)}. What time would you like?")
        time = record_audio()
        time = convert_time_format(time)  # 🔥 Convert time format before checking

        if time and time in available_slots:  # ✅ Ensure user picks from available slots
            break
        speak_text("That slot is not available or not recognized. Please try again.")

    speak_text("What service do you need? Haircut, Facial, or Massage?")
    service = record_audio()
    if not service:
        return

    # ✅ Store booking automatically
    confirmation = book_appointment(name, date, time, service)
    speak_text(confirmation)
    print(f"✅ {confirmation}")

from web_scraper import search_faiss  # Import FAISS retrieval function

# ===================================
#  🤖 SECTION 5: AI RESPONSE HANDLING (REAL-TIME STREAMING)
# ===================================
from web_scraper import search_faiss

def generate_response_stream(user_input, speak=True):
    """Generates AI responses using retrieved knowledge and streams them while speaking (optional)."""
    model = "gpt-3.5-turbo" if len(user_input) < 50 else "gpt-4"

    # 🔹 Retrieve salon-related data
    retrieved_info = search_faiss(user_input)  

    # 🔹 Ensure AI knows what to do with the retrieved data
    context = f"Here is information from the salon: {retrieved_info}" if retrieved_info else "No specific salon details found."

    # ✅ Call OpenAI API
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a salon booking assistant. Use retrieved salon details in your responses."},
            {"role": "assistant", "content": context},
            {"role": "user", "content": user_input}
        ]
    )

    # ✅ Extract full response
    full_response = response.choices[0].message.content.strip()

    # ✅ Only speak if 'speak' is True
    if speak and full_response:
        speak_text(full_response)  

    return full_response  # Return AI-generated response


def conversational_ai(first_time=True, user_input=None):
    """Handles AI conversation and automated booking."""
    
    if first_time:
        speak_text("Hello! I am your Sally Hershberger. do you need new style?")
    
    if not user_input:
        user_input = record_audio()  # Listen for user input

    if not user_input:
        return "Sorry, I couldn't understand that."

    # 🔥 Detect Booking Intent
    if any(phrase in user_input.lower() for phrase in ["book an appointment", "schedule an appointment", 
                                                       "i need an appointment", "i want to book", "i need a haircut", 
                                                       "can i get a facial appointment", "i want to schedule", 
                                                       "i want a service", "schedule my booking"]):
        return handle_booking()  # Call booking function and return confirmation

    # ✅ If no booking intent, proceed as normal AI chat
    return generate_response_stream(user_input)  # AI response


# ===================================
#  🚀 SECTION 7: RUN THE CHAT SYSTEM
# ===================================
if __name__ == "__main__":
    conversational_ai()  # ✅ Run only when directly executed

