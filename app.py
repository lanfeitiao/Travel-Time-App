import streamlit as st
import pydeck as pdk
import requests
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from geopy.geocoders import Nominatim

# Setting the page config to wide mode
st.set_page_config(layout='wide')

st.title('Travel Time Web Application')

# Load environment variables from .env file
load_dotenv()

# Fuction to fetch reachable destinations 
def fetch_destinations(start_point, travel_time):
    client = OpenAI()
    prompt = f"What are some destinations (towns, cities) within {travel_time} minutes of travel by public transport from {start_point}? Please include their coordinates as well."

    try:
        response = client.chat.completions.create(
            model='gpt-3.5-turbo',
            response_format={ "type": "json_object" },
            messages=[
                { "role": "system", "content": "You are a travel guide designed to output JSON." },
                { "role": "user", "content": prompt }
            ]
        )

        # Extracting the response text
        destinations_json =  response.choices[0].message.content
        print(destinations_json) # For debugging, to view the raw response 

        # Parsing the JSON response 
        destinations_data = json.loads(destinations_json)

        # Extracting names and coordinates from the parsed JSON
        destination_info = [{
            'name' : dest['name'],
            'coordinates': [dest['coordinates']['longitude'],dest['coordinates']['latitude']]
        } for dest in destinations_data['destinations']]
        print(destination_info)
        return destination_info
    except Exception as e:
        print(f"An error occured: {e}")
        return []

# Set up the sidebar for user inputs
st.sidebar.header('Travel Time Settings')
starting_point = st.sidebar.text_input('Enter starting point', 'Amsterdam')
travel_time = st.sidebar.slider('Select travel time (minutes)', min_value=5, max_value=120, value=30)

# # Sample destinations_info data
# destinations_info = [
#     {'name': 'Haarlem', 'coordinates': [52.3874, 4.6375]},
#     {'name': 'Rotterdam', 'coordinates': [51.9225, 4.4792]}
# ]

# API call to get destinations
destinations_info = fetch_destinations(starting_point, travel_time)

# Display destinations in the sidebar 
st.sidebar.header(f'Destinations within {travel_time} minutes from {starting_point}: ')
for destination in destinations_info:
    st.sidebar.write(f"{destination['name']} at coordinates {destination['coordinates']}")

# Setting up the map
INITIAL_VIEW_STATE = pdk.ViewState(
    latitude=52.3676,
    longitude=4.9041,
    zoom=8,
    pitch=50
)

# RGBA value generated in Javascript by deck.gl's Javascript expression parser
GET_COLOR_JS = [
    "255 * (1 - (start[2] / 10000) * 2)",
    "128 * (start[2] / 10000)",
    "255 * (start[2] / 10000)",
    "255 * (1 - (start[2] / 10000))",
]

# Define the scatterplot layer
scatter_layer = pdk.Layer(
    'ScatterplotLayer',
    data=destinations_info,
    radius_scale=20,
    get_position="coordinates",
    get_fill_color=[255, 140, 0],
    get_radius=30,
    pickable=True,
)

# Define lines data for directions
geolocator = Nominatim(user_agent="travel_app")
starting_city = geolocator.geocode(starting_point)
starting_point_coordinates = [starting_city.longitude, starting_city.latitude]

lines_data = [{
    'start': starting_point_coordinates,
    'end': dest['coordinates']
} for dest in destinations_info]

# Define the line layer
line_layer = pdk.Layer(
    'LineLayer',
    data= lines_data,
    get_source_position='start',
    get_target_position='end',
    get_color=[253, 128, 93],
    get_width=5,
    # highlight_color=[255, 255, 0],
    # picking_radius=10,
    # auto_highlight=True,
    # pickable=True,
)

# Render the map
st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state=INITIAL_VIEW_STATE,
    layers=[scatter_layer, line_layer]
))
