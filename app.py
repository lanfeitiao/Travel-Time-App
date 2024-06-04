import streamlit as st
import pydeck as pdk
import requests

st.title('Travel Time Web Application')

# Fuction to fetch reachable destinations 
# TO DO: replace it with actual API
def fetch_destinations(start_point, travel_time):
    # This should be replaced with a call to a real API
    # Returning a fixed location for demonstration purposes
    return [{'latitude': 52.3676, 'longitude': 4.9041}]

# Set up the sidebar for user inputs
st.sidebar.header('Travel Time Settings')
starting_point = st.sidebar.text_input('Enter starting point', 'Amsterdam')
travel_time = st.sidebar.slider('Select travel time (minutes)', min_value=5, max_value=120, value=30)

# API call to get destinations
destinations = fetch_destinations(starting_point, travel_time)

# Map initialization
st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state=pdk.ViewState(
        latitude=52.3676,
        longitude=4.9041,
        zoom=11,
        pitch=50,
    ),
    layers=[
        pdk.Layer(
            'ScatterplotLayer',
            data=destinations,
            get_position='[longitude, latitude]',
            get_color='[200, 30, 0, 160]',
            get_radius=200,
        ),
    ],
))
st.write(f'Destinations within {travel_time} minutes from {starting_point}: ')
for destination in destinations:
    st.write(destination)