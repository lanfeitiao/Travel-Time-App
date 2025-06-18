# Travel-Time-App

A Streamlit app that recommends family-friendly destinations reachable by public transport within a selected time from your starting point.

## Features

- Generates destination suggestions using OpenAI's language model.
- Displays travel times and suggested activities for each location.
- Visualizes routes and destinations on an interactive map with PyDeck.

## Setup

1. Create a virtual environment (optional).
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Provide your OpenAI API key as an environment variable named `OPENAI_API_KEY` (for example in a `.env` file).

## Running the App

Run the Streamlit application with:

```bash
streamlit run app.py
```

A browser window will open where you can enter your starting city, travel time, and the age of your child to receive destination suggestions.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
