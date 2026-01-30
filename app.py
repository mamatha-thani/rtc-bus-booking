import streamlit as st
from datetime import date
import psycopg2
import os

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="RTC Bus Ticket Booking", layout="centered")

# ---------------- DATABASE FUNCTIONS ----------------
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        database=os.getenv("DB_NAME", "rtc_booking"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "NewStrong@123"),
        port=5432
    )

def get_available_seats():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT seat_no FROM seats WHERE status='AVAILABLE'")
    seats = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return seats

def book_seats(seat_list):
    conn = get_db_connection()
    cur = conn.cursor()
    for seat in seat_list:
        cur.execute(
            "UPDATE seats SET status='BOOKED' WHERE seat_no=%s",
            (seat,)
        )
    conn.commit()
    cur.close()
    conn.close()

# ---------------- SESSION STATE ----------------
if "step" not in st.session_state:
    st.session_state.step = 1
if "selected_seats" not in st.session_state:
    st.session_state.selected_seats = []
if "passengers" not in st.session_state:
    st.session_state.passengers = []

# ---------------- TITLE ----------------
st.title("🚌 RTC Bus Ticket Booking System")

# ---------------- STEP 1: SEARCH BUS ----------------
if st.session_state.step == 1:
    st.subheader("🔍 Search Bus")

    from_city = st.selectbox("From City", ["Hyderabad", "Vijayawada", "Bangalore"])
    to_city = st.selectbox("To City", ["Chennai", "Bangalore", "Hyderabad"])
    journey_date = st.date_input("Journey Date", min_value=date.today())

    if st.button("Search Buses"):
        st.session_state.from_city = from_city
        st.session_state.to_city = to_city
        st.session_state.journey_date = journey_date
        st.session_state.step = 2
        st.rerun()

# ---------------- STEP 2: BUS LIST ----------------
elif st.session_state.step == 2:
    st.subheader("🚌 Available Buses")

    buses = [
        {"name": "TSRTC Super Luxury", "time": "08:00 AM", "price": 700},
        {"name": "APSRTC Express", "time": "10:30 AM", "price": 600},
        {"name": "TSRTC Garuda Plus", "time": "09:00 PM", "price": 900},
    ]

    for bus in buses:
        with st.container(border=True):
            st.write(f"**Bus:** {bus['name']}")
            st.write(f"**Departure Time:** {bus['time']}")
            st.write(f"**Price per Seat:** ₹{bus['price']}")

            if st.button(f"Select {bus['name']}"):
                st.session_state.bus = bus
                st.session_state.step = 3
                st.rerun()

# ---------------- STEP 3: SEAT SELECTION ----------------
elif st.session_state.step == 3:
    st.subheader("💺 Select Seats")

    available_seats = get_available_seats()

    if not available_seats:
        st.error("❌ All seats are already booked")
        st.stop()

    selected = st.multiselect("Choose seats", available_seats)

    if st.button("Confirm Seats"):
        if not selected:
            st.error("Please select at least one seat")
        else:
            st.session_state.selected_seats = selected
            st.session_state.step = 4
            st.rerun()

# ---------------- STEP 4: PASSENGER DETAILS ----------------
elif st.session_state.step == 4:
    st.subheader("👤 Passenger Details")

    st.session_state.passengers = []

    for i, seat in enumerate(st.session_state.selected_seats):
        st.markdown(f"**Seat {seat}**")
        name = st.text_input(f"Name ({seat})", key=f"name_{i}")
        age = st.number_input(f"Age ({seat})", min_value=1, max_value=100, key=f"age_{i}")
        gender = st.selectbox(f"Gender ({seat})", ["Male", "Female"], key=f"gender_{i}")

        st.session_state.passengers.append({
            "seat": seat,
            "name": name,
            "age": age,
            "gender": gender
        })

    if st.button("Proceed to Payment"):
        st.session_state.step = 5
        st.rerun()

# ---------------- STEP 5: PAYMENT ----------------
elif st.session_state.step == 5:
    st.subheader("💳 Payment")

    total_amount = len(st.session_state.selected_seats) * st.session_state.bus["price"]

    st.write(f"**Total Seats:** {len(st.session_state.selected_seats)}")
    st.write(f"**Total Amount:** ₹{total_amount}")

    payment_method = st.radio("Select Payment Method", ["UPI", "Debit Card", "Credit Card"])

    if st.button("Pay Now"):
        book_seats(st.session_state.selected_seats)

        st.success("Payment Successful!")
        st.session_state.total_amount = total_amount
        st.session_state.step = 6
        st.rerun()

# ---------------- STEP 6: TICKET CONFIRMATION ----------------
elif st.session_state.step == 6:
    st.subheader("🎫 Ticket Confirmation")

    st.write("✅ **Booking Confirmed**")
    st.write(f"**Bus:** {st.session_state.bus['name']}")
    st.write(f"**From:** {st.session_state.from_city}")
    st.write(f"**To:** {st.session_state.to_city}")
    st.write(f"**Journey Date:** {st.session_state.journey_date}")
    st.write(f"**Seats:** {', '.join(st.session_state.selected_seats)}")
    st.write(f"**Total Paid:** ₹{st.session_state.total_amount}")

    st.subheader("Passenger Details")
    for p in st.session_state.passengers:
        st.write(f"{p['seat']} - {p['name']} ({p['age']} yrs, {p['gender']})")

    if st.button("Book Another Ticket"):
        st.session_state.step = 1
        st.session_state.selected_seats = []
        st.session_state.passengers = []
        st.rerun()
