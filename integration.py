from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# Authenticate and connect to Google Sheets
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file("salon-454509-b7d02757c977.json", scopes=SCOPES)
client = gspread.authorize(creds)

# Open the Google Sheet
spreadsheet = client.open("Salon Bookings")
worksheet = spreadsheet.sheet1  # Make sure the sheet name is correct

# Read data (Get all rows)
data = worksheet.get_all_records()
print("Sheet Data:", data)

# Generate a unique Booking ID
booking_id = int(datetime.now().timestamp())  # Unique ID

# Ensure headers match: Booking ID, Customer Name, Date, Time, Service, Status
new_booking = [booking_id, "John Doe", "2025-03-23", "14:00", "Haircut", "Confirmed"]

# Append the corrected row
worksheet.append_row(new_booking)

print("✅ Booking added successfully!")

#get available slots

def get_available_slots(date):
    """Finds available slots for a given date."""
    all_bookings = worksheet.get_all_records()

    # Define working hours (Modify as per salon schedule)
    working_hours = ["10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00"]

    # Extract booked time slots
    booked_slots = [entry["Time"] for entry in all_bookings if entry["Date"] == date]

    # Find free slots
    free_slots = [time for time in working_hours if time not in booked_slots]

    return free_slots

# Example Usage
date = "2025-03-23"
free_slots = get_available_slots(date)
print(f"✅ Available slots on {date}: {free_slots}")
def ai_booking_assistant():
    """AI-driven salon booking assistant"""

    name = input("👤 Enter your name: ")
    date = input("📅 Enter booking date (YYYY-MM-DD): ")

    available_slots = get_available_slots(date)
    if not available_slots:
        print("⚠️ No slots available on this date. Try another date.")
        return
    
    print(f"⏳ Available slots: {available_slots}")
    time = input("⏳ Choose a time from available slots: ")

    if time not in available_slots:
        print("⚠️ Invalid time selected!")
        return

    service = input("💇 Enter service type (e.g., Haircut, Facial, etc.): ")

    booking_id = int(datetime.now().timestamp())  # Unique ID
    new_booking = [booking_id, name, date, time, service, "Confirmed"]
    
    worksheet.append_row(new_booking)
    print("✅ Booking confirmed!")

# Run Booking Assistant
ai_booking_assistant()
