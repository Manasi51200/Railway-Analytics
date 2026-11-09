import streamlit as st
import pandas as pd
from pymongo import MongoClient
from datetime import date

st.set_page_config(
    page_title="Railway Management System",
    page_icon="🚆",
    layout="wide"
)

# MongoDB connection
@st.cache_resource
def connect_database():
    client = MongoClient(st.secrets["MONGO_URI"])
    client.admin.command("ping")
    return client["RailwayDB"]

try:
    db = connect_database()
except Exception as e:
    st.error("Database connection failed. Please check your MongoDB credentials and connection.")
    st.stop()

# Page title
st.title("🚆 Railway Management System")
st.caption("Passenger Management | Train Management | Reservations | Payments")

# Sidebar navigation
st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select a section",
    [
        "Home",
        "Passengers",
        "Trains",
        "Reservations",
        "Payments",
        "Analytics"
    ]
)

def get_data(collection):
    return list(db[collection].find({}, {"_id": 0}))

# HOME
if page == "Home":
    st.header("Welcome to Railway Management System")
    st.write("Manage railway passengers, trains, reservations and payments.")

    passengers = get_data("Passengers")
    trains = get_data("Trains")
    reservations = get_data("Reservations")
    payments = get_data("Payments")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Passengers", len(passengers))
    c2.metric("Total Trains", len(trains))
    c3.metric("Total Reservations", len(reservations))

    revenue = sum(float(x.get("amount", 0)) for x in payments)
    c4.metric("Total Revenue", f"₹{revenue:,.0f}")

    st.subheader("System Overview")
    st.info("Use the navigation menu to manage railway records.")

# PASSENGERS
elif page == "Passengers":
    st.header("👥 Passenger Management")

    data = get_data("Passengers")
    df = pd.DataFrame(data)

    search = st.text_input("Search passenger by name or ID")

    if not df.empty:
        if search:
            df = df[
                df.astype(str).apply(
                    lambda row: row.str.contains(
                        search, case=False
                    ).any(), axis=1
                )
            ]

        st.dataframe(df, use_container_width=True)

    with st.expander("➕ Add New Passenger"):
        with st.form("passenger_form"):
            pid = st.text_input("Passenger ID")
            name = st.text_input("Passenger Name")
            age = st.number_input("Age", min_value=1, max_value=120)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            city = st.text_input("City")
            state = st.text_input("State")
            category = st.text_input("Passenger Category")

            submitted = st.form_submit_button("Add Passenger")

            if submitted:
                if pid and name and city and state:
                    if db.Passengers.find_one({"passenger_id": pid}):
                        st.error("Passenger ID already exists.")
                    else:
                        db.Passengers.insert_one({
                            "passenger_id": pid,
                            "name": name,
                            "age": age,
                            "gender": gender,
                            "city": city,
                            "state": state,
                            "passenger_category": category,
                            "registration_date": str(date.today())
                        })
                        st.success("Passenger added successfully!")
                        st.rerun()
                else:
                    st.warning("Please fill all required fields.")

    with st.expander("🗑️ Delete Passenger"):
        delete_id = st.text_input("Enter Passenger ID to delete")
        if st.button("Delete Passenger"):
            result = db.Passengers.delete_one({"passenger_id": delete_id})
            if result.deleted_count:
                st.success("Passenger deleted!")
                st.rerun()
            else:
                st.error("Passenger not found.")

# TRAINS
elif page == "Trains":
    st.header("🚆 Train Management")

    df = pd.DataFrame(get_data("Trains"))

    if not df.empty:
        st.dataframe(df, use_container_width=True)

    with st.expander("➕ Add New Train"):
        with st.form("train_form"):
            train_id = st.text_input("Train ID")
            number = st.text_input("Train Number")
            name = st.text_input("Train Name")
            source = st.text_input("Source")
            destination = st.text_input("Destination")
            departure = st.text_input("Departure Time")
            arrival = st.text_input("Arrival Time")
            seats = st.number_input("Total Seats", min_value=1)

            submitted = st.form_submit_button("Add Train")

            if submitted:
                if train_id and number and name and source and destination:
                    if db.Trains.find_one({"train_id": train_id}):
                        st.error("Train ID already exists.")
                    else:
                        db.Trains.insert_one({
                            "train_id": train_id,
                            "train_number": number,
                            "train_name": name,
                            "source": source,
                            "destination": destination,
                            "departure_time": departure,
                            "arrival_time": arrival,
                            "total_seats": seats
                        })
                        st.success("Train added successfully!")
                        st.rerun()
                else:
                    st.warning("Fill all required fields.")

# RESERVATIONS
elif page == "Reservations":
    st.header("🎫 Reservation Management")

    df = pd.DataFrame(get_data("Reservations"))

    if not df.empty:
        statuses = ["All"] + sorted(
            df["ticket_status"].dropna().astype(str).unique().tolist()
        )
        status = st.selectbox("Filter by Booking Status", statuses)

        if status != "All":
            df = df[df["ticket_status"] == status]

        st.dataframe(df, use_container_width=True)

    with st.expander("➕ Add Reservation"):
        with st.form("reservation_form"):
            booking_id = st.text_input("Booking ID")
            passenger_id = st.text_input("Passenger ID")
            train_id = st.text_input("Train ID")
            journey_date = st.date_input("Journey Date")
            ticket_status = st.selectbox(
                "Ticket Status",
                ["Confirmed", "Waiting List", "Cancelled"]
            )
            fare = st.number_input("Fare", min_value=0.0)
            count = st.number_input("Passenger Count", min_value=1)

            submitted = st.form_submit_button("Create Reservation")

            if submitted:
                if booking_id and passenger_id and train_id:
                    if db.Reservations.find_one({"booking_id": booking_id}):
                        st.error("Booking ID already exists.")
                    elif not db.Passengers.find_one({"passenger_id": passenger_id}):
                        st.error("Passenger ID does not exist.")
                    elif not db.Trains.find_one({"train_id": train_id}):
                        st.error("Train ID does not exist.")
                    else:
                        db.Reservations.insert_one({
                            "booking_id": booking_id,
                            "passenger_id": passenger_id,
                            "train_id": train_id,
                            "booking_date": str(date.today()),
                            "journey_date": str(journey_date),
                            "ticket_status": ticket_status,
                            "fare": fare,
                            "passenger_count": count
                        })
                        st.success("Reservation created!")
                        st.rerun()
                else:
                    st.warning("Fill all required fields.")

# PAYMENTS
elif page == "Payments":
    st.header("💳 Payment Management")

    df = pd.DataFrame(get_data("Payments"))

    if not df.empty:
        st.dataframe(df, use_container_width=True)

    with st.expander("➕ Add Payment"):
        with st.form("payment_form"):
            payment_id = st.text_input("Payment ID")
            booking_id = st.text_input("Booking ID")
            amount = st.number_input("Amount", min_value=0.0)
            method = st.selectbox(
                "Payment Method",
                ["UPI", "Card", "Net Banking", "Cash"]
            )
            status = st.selectbox(
                "Payment Status",
                ["Paid", "Pending", "Refunded"]
            )

            submitted = st.form_submit_button("Add Payment")

            if submitted:
                if payment_id and booking_id:
                    if db.Payments.find_one({"payment_id": payment_id}):
                        st.error("Payment ID already exists.")
                    elif not db.Reservations.find_one({"booking_id": booking_id}):
                        st.error("Booking ID does not exist.")
                    else:
                        db.Payments.insert_one({
                            "payment_id": payment_id,
                            "booking_id": booking_id,
                            "amount": amount,
                            "payment_method": method,
                            "payment_status": status,
                            "payment_date": str(date.today())
                        })
                        st.success("Payment added!")
                        st.rerun()
                else:
                    st.warning("Fill all required fields.")

# ANALYTICS
elif page == "Analytics":
    st.header("📊 Railway Analytics")

    passengers = pd.DataFrame(get_data("Passengers"))
    reservations = pd.DataFrame(get_data("Reservations"))
    payments = pd.DataFrame(get_data("Payments"))

    if not passengers.empty:
        st.subheader("Passenger Count by City")
        st.bar_chart(passengers["city"].value_counts())

    if not reservations.empty:
        st.subheader("Booking Status Analysis")
        st.bar_chart(reservations["ticket_status"].value_counts())

        st.subheader("Train-wise Bookings")
        st.bar_chart(reservations["train_id"].value_counts())

        st.subheader("Train-wise Revenue")
        revenue = reservations.groupby("train_id")["fare"].sum()
        st.bar_chart(revenue)

    if not payments.empty:
        st.subheader("Payment Status Analysis")
        st.bar_chart(payments["payment_status"].value_counts())

    st.success("Analytics updated from MongoDB Atlas!")