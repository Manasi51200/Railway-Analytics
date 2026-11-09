import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Railway Analytics",
    page_icon="🚆",
    layout="wide"
)

st.title("🚆 Railway Passenger and Reservation Analytics")
st.write("Railway Data Analysis Dashboard")

# Load datasets
passengers = pd.read_csv("Passengers.csv")
trains = pd.read_csv("Trains.csv")
reservations = pd.read_csv("Reservations.csv")
payments = pd.read_csv("Payments.csv")

# KPI section
st.header("Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Passengers", len(passengers))
col2.metric("Total Bookings", len(reservations))
col3.metric("Total Trains", len(trains))
col4.metric("Total Revenue", f"₹{reservations['fare'].sum():,.0f}")

# Passenger analysis
st.header("Passenger Analysis")
city_count = passengers["city"].value_counts()
st.bar_chart(city_count)

# Booking status
st.header("Booking Status Analysis")
booking_status = reservations["ticket_status"].value_counts()
st.bar_chart(booking_status)

# Train-wise bookings
st.header("Train-wise Booking Analysis")
train_bookings = reservations["train_id"].value_counts()
st.bar_chart(train_bookings)

# Payment analysis
st.header("Payment Status Analysis")
payment_status = payments["payment_status"].value_counts()
st.bar_chart(payment_status)

# Revenue analysis
st.header("Train-wise Revenue Analysis")
revenue = reservations.groupby("train_id")["fare"].sum()
st.bar_chart(revenue)

# Dataset preview
st.header("Railway Dataset")
st.dataframe(reservations)

st.success("Railway Analytics Dashboard Loaded Successfully!")