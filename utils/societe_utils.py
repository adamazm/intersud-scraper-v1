from dotenv import load_dotenv
import os
import requests

load_dotenv()

soc_api_url = "https://api.societe.com/api/v1/entreprise/search?nom={name}&nbrep={nbrep}&token={token}"
token = os.getenv('SOC_API_TOKEN')


def get_companies(company_name, nbrep=5):
    # Format the URL with the company name and token
    url = soc_api_url.format(name=company_name, nbrep=nbrep, token=token)

    try:
        # Send GET request to the API
        response = requests.get(url)

        # Check if the request was successful
        response.raise_for_status()

        # Parse the JSON response
        data = response.json()

        # siren = data["data"]["results"][0]["siren"]

        # return siren

        return data["data"]["results"]

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None
