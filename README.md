# Intersud AI Scraper

This project is an AI-powered web scraper designed to gather company information from multiple sources using AI agents. The scraper extracts data from websites such as Societe.com, Infogreffe.fr, and Pappers.fr and Ellisphere.

## Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/jrenouard/intersud-ai-scrapper
   cd intersud-ai-scrapper
   ```

2. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Install Playwright

```sh
   playwright install
```

## Running the API

To start the API locally, run:

```sh
cd backend
python app.py
```

This will launch the API, which can be accessed locally.

## Running the Streamlit UI

To launch the Streamlit interface for visualization and interaction, run:

```sh
cd frontend
streamlit run app.py
```

## About

The scrapers operate using `browser-use` along with Playwright to extract data efficiently.
The prompts for the agents are located in the `backend/tasks/` folder if modifications are needed.
