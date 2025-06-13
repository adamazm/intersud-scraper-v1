def infogreffe_task(company_id, id_type):
    """
    Infogreffe scraping task to retrieve company information.

    :param company_id: The identification of the company to scrape data for.
    :param id_type: The type of ID (e.g. Name, SIREN, SIRET) to be used for scraping.
    :return: A formatted string with instructions for scraping Infogreffe.
    """

    return f"""Follow these steps to efficiently retrieve company information from Infogreffe:

    CRITICAL INSTRUCTIONS:
    - You MUST complete ALL steps below and extract the actual company data
    - You MUST return the final result as valid JSON format only
    - DO NOT stop at intermediate steps or return status messages
    - The final output should be the extracted company data in the JSON format specified in step 5

    1. Go to https://www.infogreffe.fr/ and accept cookies if prompted.

    2. Locate the search bar, ensure it is active, and enter the company's identifications: {company_id}, which is the company's {id_type}, then press Enter or click the search button.

    3. Wait for the results to load and click on the first relevant result to access the company profile.

    4. Scroll to the top of the page and expand all sections to ensure all information is visible.

    5. Extract and organize useful information from the following sections and return the data in JSON format:

    {{
        "source": "infogreffe.fr",
        "company_id": "{company_id}",
        "id_type": "{id_type}",
        "identite": {{
            "denomination_sociale": "...",
            "siret": "...",
            "dirigeant": "...",
            "chiffre_affaires": "...",
            "effectif": "...",
            "inscription": "...",
            "activite_code_naf": "...",
            "forme_juridique": "..."
        }},
        "dirigeants": [
            {{
                "nom_complet": "...",
                "fonction": "..."
            }}
        ],
        "analyse_financiere": {{
            "derniers_chiffres_cles": {{
                "2023": {{
                    "chiffre_affaires": "...",
                    "resultat": "...",
                    "effectif": "..."
                }},
                "2022": {{
                    "chiffre_affaires": "...",
                    "resultat": "...",
                    "effectif": "..."
                }}
            }},
            "rapports_performance": [
                {{
                    "nom_rapport": "...",
                    "description": "..."
                }}
            ]
        }},
        "etablissements": [
            {{
                "nom": "...",
                "type": "...",
                "siret": "...",
                "adresse": "..."
            }}
        ]
    }}

    6. If a section is missing or unparseable, set the value to null or empty array as appropriate and continue.

    Important Notes:
    - SKIP THE DOCUMENTS SECTION!
    - Ensure all sections are expanded before extracting data.
    - Extract all years present in the financial analysis.
    - Use null for missing values, empty arrays [] for missing lists.
    - If multiple items exist in a section (dirigeants, etablissements), include all in the respective arrays.
    - Return ONLY valid JSON format - no additional text or formatting.
    - Ensure all JSON keys use snake_case format.
    - DO NOT include any explanatory text, headers, or markdown formatting.
    - DO NOT mention the source in text format - it's already in the JSON.
    - Your response should start with {{ and end with }}.
    
    REMEMBER: The output must be parseable JSON that starts with {{ and ends with }}. No other text should be included!
    """
