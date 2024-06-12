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

# Helper function to get generated outputs from OpenAI model 
client = OpenAI()

def get_completion(prompt, model='gpt-3.5-turbo'):
    messages = [{ "role": "user", "content": prompt }]
    response = client.chat.completions.create(
            model=model,
            response_format={ "type": "json_object" },
            messages=messages,
            temperature=0,
        )
    return response.choices[0].message.content
    # Format your response as a JSON object with "name", "things_to_do", \
    # and "coordinates" as the keys.\
    # If the information isn't present, use "unknown" as the value.
    # Format the coordinates value as an array of longtitude and latitude.
    # Format the things_to_do value as an array.

# Fuction to fetch reachable destinations 
def fetch_destinations(start_point, travel_time, child_age):
    prompt = f"""
    Your task is to generate a list of family-friendly destinations (towns and cities)\
    and things to do within {travel_time} minutes of travel by public transport\
    from {start_point}. And they are recommended for a family trip with\ 
    {child_age} years old child or children.

    Output format as follows: 
    JSON Template:
    {{
        "destinations": [
            {{
                "name": "Destination 1",
                "longitude": longitude , 
                "latitude": latitude,
                "things_to_do": "Activity 1, Activity 2, Activity 3"
            }},
            {{
                "name": "Destination 2",
                "longitude": longitude , 
                "latitude": latitude,
                "things_to_do": "Activity 1, Activity 2, Activity 3"
            }},
            ...
        ]
    }}
    """

    try:
        destinations_json = get_completion(prompt)
        print(destinations_json) # For debugging, to view the raw response 

        # Parsing the JSON response 
        destinations_data = json.loads(destinations_json)

        # Extracting names and coordinates from the parsed JSON
        destination_info = [{
            'name' : dest['name'],
            'lon': dest['longitude'],
            'lat': dest['latitude'],
            'things_to_do': dest['things_to_do']
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
child_age = st.sidebar.slider('Select child\'s age', min_value=1, max_value=18, value=5)

# # Sample destinations_info data
# destinations_info = [
#     {'name': 'Haarlem', 'coordinates': [52.3874, 4.6375]},
#     {'name': 'Rotterdam', 'coordinates': [51.9225, 4.4792]}
# ]

# API call to get destinations
destinations_info = fetch_destinations(starting_point, travel_time, child_age)

# Display destinations in the sidebar 
st.subheader(f"""
             Destinations and Things to Do within {travel_time} minutes\
             from {starting_point} for a {child_age} year old:
             """)
for destination in destinations_info:
    st.write(f"**{destination['name']}**: {destination['things_to_do']}")

# Setting up the map
INITIAL_VIEW_STATE = pdk.ViewState(
    latitude=52.3676,
    longitude=4.9041,
    zoom=8,
    pitch=50
)


# Define the scatterplot layer
scatter_layer = pdk.Layer(
    'ScatterplotLayer',
    data=destinations_info,
    radius_scale=20,
    get_position=['lon', 'lat'],
    get_fill_color=[255, 140, 0],
    get_radius=30,
    pickable=True,
)

# Define lines data for directions
geolocator = Nominatim(user_agent="travel_app")
starting_city = geolocator.geocode(starting_point)
if starting_city:
    starting_point_coordinates = [starting_city.longitude, starting_city.latitude]
    INITIAL_VIEW_STATE.latitude = starting_city.latitude
    INITIAL_VIEW_STATE.longitude = starting_city.longitude
    

lines_data = [{
    'start': starting_point_coordinates,
    'end': [dest['lon'], dest['lat']]
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
