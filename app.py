from flask import Flask, render_template, request, redirect, url_for
import qrcode
import os
import json
from datetime import datetime

app = Flask(__name__)
BOOKINGS_FILE = "data/bookings.json"

# Ensure directories exist
os.makedirs("static/qr_codes", exist_ok=True)
os.makedirs("data", exist_ok=True)

# Load bookings
def load_bookings():
    if not os.path.exists(BOOKINGS_FILE):
        return []
    with open(BOOKINGS_FILE, "r") as f:
        return json.load(f)

# Save bookings
def save_bookings(bookings):
    with open(BOOKINGS_FILE, "w") as f:
        json.dump(bookings, f, indent=4)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/book", methods=["GET", "POST"])
def book():
    if request.method == "POST":
        name = request.form["name"]
        seat = request.form["seat"]
        booking_id = f"{name[:3].upper()}{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Create booking record
        booking = {
            "id": booking_id,
            "name": name,
            "seat": seat,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Save to file
        bookings = load_bookings()
        bookings.append(booking)
        save_bookings(bookings)

        # Generate QR code
        qr = qrcode.make(booking_id)
        qr_path = f"static/qr_codes/{booking_id}.png"
        qr.save(qr_path)

        return render_template("ticket.html", booking=booking, qr_path=qr_path)

    return render_template("booking.html")

@app.route("/validate", methods=["GET", "POST"])
def validate():
    if request.method == "POST":
        booking_id = request.form["booking_id"]
        bookings = load_bookings()
        for booking in bookings:
            if booking["id"] == booking_id:
                return f"✅ Ticket Valid: {booking['name']} (Seat {booking['seat']})"
        return "❌ Invalid Ticket!"
    return render_template("validate.html")

if __name__ == "__main__":
    app.run(debug=True)