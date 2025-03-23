import gspread
from google.oauth2.service_account import Credentials

# 🔹 Load Google Sheets API Credentials
SERVICE_ACCOUNT_FILE = "salon-454509-b7d02757c977.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)

# 🔹 Open the Google Sheet
SPREADSHEET_NAME = "Salon Bookings"
spreadsheet = client.open(SPREADSHEET_NAME)
worksheet = spreadsheet.sheet1  # Assumes the first sheet is used

# ===================================
#  📅 FUNCTION TO GET AVAILABLE SLOTS
# ===================================
def get_available_slots(date):
    """Fetch available slots for a given date from the Google Sheet."""
    try:
        bookings = worksheet.get_all_records()  # ✅ Fetch actual booked slots
        all_slots = ["10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00"]

        # ✅ Get only booked slots for the given date
        booked_slots = [entry["Time"] for entry in bookings if entry["Date"] == date]

        # ✅ Remove booked slots from available ones
        available_slots = [slot for slot in all_slots if slot not in booked_slots]
        
        return available_slots

    except Exception as e:
        print(f"❌ Error fetching available slots: {str(e)}")
        return []  # Return an empty list if there's an error

# ===================================
#  📌 FUNCTION TO BOOK AN APPOINTMENT
# ===================================
def book_appointment(name, date, time, service):
    """Check availability and book an appointment if slot is available."""
    available_slots = get_available_slots(date)

    if time not in available_slots:
        return f"❌ Slot not available. Available slots: {available_slots}"

    # ✅ Append new booking to Google Sheet
    new_booking = [name, date, time, service, "Confirmed"]
    worksheet.append_row(new_booking)
    
    return f"✅ Booking confirmed for {name} on {date} at {time} for {service}."
