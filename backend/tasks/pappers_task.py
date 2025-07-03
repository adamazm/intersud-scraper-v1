def pappers_scrape_task(company_id: str, id_type):
    """
    Pappers scraping task to retrieve company information.

    :param company_id: The identification of the company to scrape data for.
    :param id_type: The type of ID (e.g. Name, SIREN, SIRET) to be used for scraping.
    :return: A formatted string with instructions for scraping Pappers.
    """

    return f"""Follow these steps to scrape the data:

    CRITICAL INSTRUCTIONS:
    - You MUST complete ALL steps below and extract the actual company data
    - You MUST return the final result as valid JSON format only
    - DO NOT stop at intermediate steps or return status messages
    - The final output should be the extracted company data in the JSON format specified in step 12
    - DO NOT take screenshots under any circumstances - they are not needed
    - If ANY error occurs (captcha, timeout, page not found, access denied, etc.), include the error in JSON format and return it immediately
    - If you encounter a CAPTCHA at any point, immediately return the following JSON:
        {{
            "error": "blocked_by_captcha",
            "message": "Access blocked by CAPTCHA verification",
            "company_id": "{company_id}",
            "id_type": "{id_type}"
        }}

    REDIRECT & ERROR HANDLING:
    - If you find yourself on a Google settings page, Google sign-in page, or any page that is NOT pappers.fr, immediately navigate to https://www.pappers.fr/
    - If you get redirected away from pappers.fr at any point (to Google, other websites), immediately try to navigate back to https://www.pappers.fr/
    - If the redirect back to pappers.fr fails or you keep getting redirected away, immediately return this JSON:
        {{
            "error": "chromium_problem",
            "message": "Unable to stay on pappers.fr domain - redirected to external sites",
            "company_id": "{company_id}",
            "id_type": "{id_type}"
        }}
    - If you encounter any other error (page timeout, access denied, server error, etc.), immediately return this JSON:
        {{
            "error": "access_error",
            "message": "Error encountered: [describe the specific error]",
            "company_id": "{company_id}",
            "id_type": "{id_type}"
        }}
    - Always verify you are on pappers.fr domain before proceeding with any actions

    IMPORTANT:
    - Simulate human behavior when navigating through the website:
        - Move mouse to element before clicking
        - Add random delays between actions (3-7 seconds)
        - Scroll the page naturally (not all at once)
        - Move mouse randomly on the page occasionally
        - Wait 5-10 seconds on the initial page load
        - Clear cookies and cache before starting
        - Accept cookies if prompted
        - Use natural typing speed when entering text

    1. Clear browser cookies and cache first.

    2. Go to https://www.pappers.fr/
    
    3. Wait 5-10 seconds on the initial page load.
    
    4. If a cookie consent dialog appears, move mouse to it and click accept.
    
    5. Wait 3-5 seconds after accepting cookies.
    
    6. Move mouse to the search bar, click it, wait 1-2 seconds, then input the company's identifications: {company_id}, which is the company's {id_type}, using natural typing speed.
    
    7. Wait 2-3 seconds after typing, then press Enter to initiate the search.
    
    8. Wait 5-7 seconds for search results to load.
    
    9. From the search results, move mouse to the first relevant result and click it to access the company details.
    
    10. Wait 5-7 seconds for the company page to load.
    
    11. Once on the company page, scroll naturally through the page (not all at once) to load all content.
    
    12. Extract and organize the information and return the data in JSON format:

    {{
        "source": "pappers.fr",
        "company_id": "{company_id}",
        "id_type": "{id_type}",
        "informations_juridiques": {{
            "siren": "...",
            "siret": "...",
            "forme_juridique": "...",
            "numero_tva": "...",
            "inscription_rcs": "...",
            "inscription_rne": "...",
            "numero_rcs": "...",
            "capital_social": "..."
        }},
        "activite": {{
            "activite_principale_declaree": "...",
            "code_naf_ape": "...",
            "domaine_activite": "...",
            "forme_exercice": "...",
            "conventions_collectives_supposees": "...",
            "date_cloture_exercice_comptable": "..."
        }},
        "etablissement": {{
            "type_etablissement": "...",
            "statut": "...",
            "adresse": "...",
            "date_creation": "..."
        }},
        "finances": {{
            "performance": {{
                "2023": {{
                    "chiffre_affaires": "...",
                    "marge_brute": "...",
                    "ebitda_ebe": "...",
                    "resultat_exploitation": "...",
                    "resultat_net": "..."
                }},
                "2022": {{
                    "chiffre_affaires": "...",
                    "marge_brute": "...",
                    "ebitda_ebe": "...",
                    "resultat_exploitation": "...",
                    "resultat_net": "..."
                }}
            }},
            "croissance": {{
                "2023": {{
                    "taux_croissance_ca": "...",
                    "taux_marge_brute": "...",
                    "taux_marge_ebitda": "...",
                    "taux_marge_operationnelle": "..."
                }}
            }},
            "gestion_bfr": {{
                "2023": {{
                    "bfr": "..."
                }}
            }}
        }},
        "dirigeants": [
            {{
                "nom_complet": "...",
                "fonction": "...",
                "age_date_naissance": "..."
            }}
        ],
        "derniers_documents_juridiques": [
            {{
                "type_document": "...",
                "nom_document": "...",
                "date_document": "..."
            }},
            {{
                "type_document": "...",
                "nom_document": "...",
                "date_document": "..."
            }}
        ],
        "statuts_constitutifs": {{
            "nom_document": "...",
            "date_document": "...",
            "details": "..."
        }},
        "derniere_liasse_publiee": {{
            "nom_document": "...",
            "exercice": "...",
            "date_publication": "...",
            "type_document": "..."
        }},
        "documents_juridiques": [
            {{
                "type_document": "...",
                "nom_document": "...",
                "date_document": "..."
            }}
        ],
        "annonces_bodacc": [
            {{
                "contenu": "..."
            }}
        ],
        "comptes_annuels": [
            {{
                "nom_document": "...",
                "date_document": "..."
            }}
        ],
        "contact": {{
            "telephone": "...",
            "email": "...",
            "site_internet": "...",
            "adresse_complete": "..."
        }},
        "entreprises_citees": [
            {{
                "nom_entreprise_personne": "...",
                "nature_relation": "..."
            }}
        ]
    }}

    13. **EXTRACT SPECIFIC DOCUMENTS**: After extracting the general information, look for and extract the following specific documents:
        
        a) **Les deux derniers documents juridiques**: Find the legal documents section and extract the TWO most recent legal documents. For each document, get:
           - Type of document
           - Document name
           - Document date (if available)
           Include this in the "derniers_documents_juridiques" array (limited to 2 items).
        
        b) **Les statuts constitutifs**: Look for the constitutive statutes document. Extract:
           - Document name
           - Document date (if available)
           - Any additional details
           Include this in the "statuts_constitutifs" object.
        
        c) **La dernière liasse publiée**: Find the most recent published financial statements. Extract:
           - Document name
           - Exercise year
           - Publication date (if available)
           - Document type
           Include this in the "derniere_liasse_publiee" object.

    14. If information for a section is unavailable or unparseable, set the value to null or empty array as appropriate and continue.

    CRITICAL: YOUR FINAL OUTPUT MUST BE VALID JSON ONLY!

    Important Notes:
        - If the section/card is scrollable, ensure to scroll to the bottom of the page to load all information before extracting data.
        - Use null for missing values, empty arrays [] for missing lists.
        - If multiple items exist in a section (dirigeants, documents_juridiques), include all in the respective arrays.
        - Extract all available years in financial data.
        - Pay special attention to document sections to extract document names, types, and dates
        - Return ONLY valid JSON format - no additional text or formatting.
        - Ensure all JSON keys use snake_case format.
        - DO NOT include any explanatory text, headers, or markdown formatting.
        - DO NOT mention the source in text format - it's already in the JSON.
        - Your response should start with {{ and end with }}.
        - If you encounter a CAPTCHA at any point, immediately return the CAPTCHA error JSON format specified above.
        
    REMEMBER: The output must be parseable JSON that starts with {{ and ends with }}. No other text should be included!
    """
