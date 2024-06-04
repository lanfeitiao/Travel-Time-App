import streamlit as st
import pydeck as pdk
import requests
import os
import openai

st.title('Travel Time Web Application')

# Fuction to fetch reachable destinations 

# Load environment variables from .env file
# from dotenv import load_dotenv
# load_dotenv()

# Access the API key 
openai.api_key = os.getenv('OPENAI_API_KEY')


def fetch_destinations(start_point, travel_time):
    #client = OpenAI()
    prompt = f"What are some destinations within {travel_time} minutes of travel by public transport from {start_point}?"

    try:
        response = openai.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[
                { "role": "system", "content": "You are a travel guide." },
                { "role": "user", "content": prompt }
            ]
        )

        # Extracting the response text
        destinations_text =  response.choices[0].message.content
        print(destinations_text) # For debugging, to view the raw response 

        # Assuming the response lists destinations seperated by commas
        destination_names = destinations_text.split(', ')
        return destination_names
    except Exception as e:
        print(f"An error occured: {e}")
        return []


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