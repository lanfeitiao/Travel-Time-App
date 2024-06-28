import streamlit as st
import pydeck as pdk
import json
from openai import OpenAI
from dotenv import load_dotenv
from geopy.geocoders import Nominatim


st.set_page_config(layout='wide')
# Inject custom CSS to set the width of the sidebar
st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {
            flex: 0 0 50% !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

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

# Fuction to fetch reachable destinations 
def fetch_destinations(start_point, travel_time, child_age):
    prompt = f"""
    Your task is to generate a list of family-friendly destinations (towns and cities)\
    and things to do within {travel_time} (in hours) of travel by public transport\
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
                "things_to_do": ["Activity 1, Activity 2, Activity 3"],
                "travel_time": "travel_time"
            }},
            {{
                "name": "Destination 2",
                "longitude": longitude , 
                "latitude": latitude,
                "things_to_do": ["Activity 1, Activity 2, Activity 3"],
                "travel_time": "travel_time"
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
            'things_to_do': dest['things_to_do'],
            'travel_time': dest['travel_time']
        } for dest in destinations_data['destinations']]
        print(destination_info)
        return destination_info
    except Exception as e:
        print(f"An error occured: {e}")
        return []

# Set up the sidebar for user inputs
st.sidebar.header('Travel Time Settings')
starting_point = st.sidebar.text_input('Enter starting point', 'Amsterdam')

time_selection = ['0.5h', '1h', '1.5h', '2h', '2.5h', '3h'] # in hours
travel_time = st.sidebar.selectbox("Travel time (in hours):", time_selection)

# Child's age selection
age_options = list(range(0,19)) # ages from 0 to 18
child_age = st.sidebar.selectbox("Child's age:", age_options)

st.title(f"Where can I go from {starting_point} within {travel_time} with {child_age}-year-old?")

# API call to get destinations
destinations_info = fetch_destinations(starting_point, travel_time, child_age)

# Display destinations in the sidebar 
st.sidebar.subheader(f"Recommendations")

# Iterate over each destination to format the output
for destination in destinations_info:
    # Use markdown to create card-like styling for each destination
    st.sidebar.markdown(f"""
    <div class="card">
        <h3>{destination['name']}</h3>
        <p><strong>Travel Time:</strong> {destination['travel_time']}</p>
        <p><strong>Activities:</strong></p>
        <ul>
            {''.join(f"<li>{activity}</li>" for activity in destination['things_to_do'])}
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Insert CSS styles to enhance the card-like appearance
st.sidebar.markdown(
    """
    <style>
    .card {
        background-color: #ffffff !important; 
        margin: 10px 0px;
        box-shadow: none;  
        border-radius: 5px; 
        }
    h3 {
        padding: 0.5rem 0.5rem 0.5rem !important;
        font-size: 16px; 
        color: #333; 
    }
    p {
        margin: 0;  
        padding: 0.5rem 0.5rem 0.5rem !important;
        color: #666;  
    }
    ul {
        padding-left: 20px;  
    }
    li {
        margin-bottom: 2px; 
    }

</style>
""", unsafe_allow_html=True)


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
)

# Render the map
st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state=INITIAL_VIEW_STATE,
    layers=[scatter_layer, line_layer]
))
