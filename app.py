import streamlit as st
from datetime import date
import psycopg2
import os
import time

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="RTC Bus Ticket Booking", layout="centered")

# ---------------- DATABASE CONNECTION ----------------
def get_db_connection():
    for i in range(5):  # retry logic (important)
        try:
            conn = psycopg2.connect(
                host=os.environ.get("DB_HOST", "rtc-db"),
                database=os.environ.get("DB_NAME", "rtc_booking"),
                user=os.environ.get("DB_USER", "postgres"),
                password=os.environ.get("DB_PASSWORD", "NewStrong@123"),
                port=5432
            )
            return conn
        except Exception as e:
            time.sleep(2)
    st.error("Database connection failed ❌")
    st.stop()

# ---------------- DATABASE INIT ----------------
def initialize_database():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS seats (
            seat_no VARCHAR(10) PRIMARY KEY,
            status VARCHAR(20) DEFAULT 'AVAILABLE'
        )
    """)

    cur.execute("SELECT COUNT(*) FROM seats")
    if cur.fetchone()[0] == 0:
        cur.execute("""
            INSERT INTO seats (seat_no) VALUES
            ('S1'),('S2'),('S3'),('S4'),('S5'),
            ('S6'),('S7'),('S8'),('S9'),('S10')
        """)

    conn.commit()
    cur.close()
    conn.close()

initialize_database()

# ---------------- DB OPERATIONS ----------------
def get_available_seats():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT seat_no FROM seats WHERE status='AVAILABLE' ORDER BY seat_no")
    seats = [row[0] for row in cur.fetchall()]

    cur.close()
    conn.close()
    return seats

def book_seats(seats):
    conn = get_db_connection()
    cur = conn.cursor()

    for seat in seats:
        cur.execute("UPDATE seats SET status='BOOKED' WHERE seat_no=%s", (seat,))

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

# ---------------- STEP 1 ----------------
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

# ---------------- STEP 2 ----------------
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
            st.write(f"**Time:** {bus['time']}")
            st.write(f"**Price:** ₹{bus['price']}")

            if st.button(f"Select {bus['name']}"):
                st.session_state.bus = bus
                st.session_state.step = 3
                st.rerun()

# ---------------- STEP 3 ----------------
elif st.session_state.step == 3:
    st.subheader("💺 Select Seats")

    seats = get_available_seats()
    selected = st.multiselect("Available Seats", seats)

    if st.button("Confirm Seats"):
        st.session_state.selected_seats = selected
        st.session_state.step = 4
        st.rerun()

# ---------------- STEP 4 ----------------
elif st.session_state.step == 4:
    st.subheader("👤 Passenger Details")

    st.session_state.passengers = []

    for i, seat in enumerate(st.session_state.selected_seats):
        name = st.text_input(f"Name ({seat})", key=f"name{i}")
        age = st.number_input(f"Age ({seat})", 1, 100, key=f"age{i}")
        gender = st.selectbox(f"Gender ({seat})", ["Male", "Female"], key=f"gender{i}")

        st.session_state.passengers.append(
            {"seat": seat, "name": name, "age": age, "gender": gender}
        )

    if st.button("Proceed to Payment"):
        st.session_state.step = 5
        st.rerun()

# ---------------- STEP 5 ----------------
elif st.session_state.step == 5:
    st.subheader("💳 Payment")

    total = len(st.session_state.selected_seats) * st.session_state.bus["price"]
    st.write(f"Total Amount: ₹{total}")

    if st.button("Pay Now"):
        book_seats(st.session_state.selected_seats)
        st.session_state.total_amount = total
        st.session_state.step = 6
        st.rerun()

# ---------------- STEP 6 ----------------
elif st.session_state.step == 6:
    st.subheader("🎫 Ticket Confirmation")

    st.success("Booking Confirmed 🎉")
    st.write(f"Seats: {', '.join(st.session_state.selected_seats)}")
    st.write(f"Amount Paid: ₹{st.session_state.total_amount}")

    if st.button("Book Another Ticket"):
        st.session_state.step = 1
        st.session_state.selected_seats = []
        st.session_state.passengers = []
        st.rerun()