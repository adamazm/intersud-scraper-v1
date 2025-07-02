def societe_scrape_task(company_id, id_type):
    return f"""Follow these steps:
    
    CRITICAL INSTRUCTIONS:
    - You MUST complete ALL steps below and extract the actual company data
    - You MUST return the final result as valid JSON format only
    - DO NOT stop at intermediate steps or return status messages
    - The final output should be the extracted company data in the JSON format specified in step 5

    REDIRECT & ERROR HANDLING:
    - If you find yourself on a Google settings page, Google sign-in page, or any page that is NOT societe.com, immediately navigate to https://www.societe.com/
    - If you get redirected away from societe.com at any point (to Google, other websites), immediately try to navigate back to https://www.societe.com/
    - If the redirect back to societe.com fails or you keep getting redirected away, immediately return this JSON:
        {{
            "error": "chromium_problem",
            "message": "Unable to stay on societe.com domain - redirected to external sites",
            "company_id": "{company_id}",
            "id_type": "{id_type}"
        }}
    - Always verify you are on societe.com domain before proceeding with any actions
    
    Go to https://www.societe.com/

    1.  Accept cookies if prompted.

    2. **Locate the search bar for the first time and click it.** Ensure that the search bar is active and ready for input before proceeding. Only after confirming the search bar is active, enter the company's identifications: {company_id}, which is the company's {id_type}, and press Enter.

    3. Wait for the search results to load to ensure all results are correctly loaded.

    4. Click on the first relevant result to access the company's profile.

    5. Scroll to the top of the screen first then extract and organize all available information about the company and return the data in JSON format:
    
    {{
        "source": "societe.com",
        "company_id": "{company_id}",
        "id_type": "{id_type}",
        "identite": {{
            "siren": "...",
            "date_creation": "...",
            "forme_juridique": "...",
            "statut": "...",
            "adresse": "...",
            "dirigeants": "...",
            "code_naf_ape": "...",
            "source_information": "..."
        }},
        "recapitulatif": {{
            "derniere_modification": "...",
            "procedures_collective": "...",
            "solvabilite": "...",
            "publications_comptes": "...",
            "score_extra_financier": "...",
            "score_carbone": "...",
            "taille_entreprise": "...",
            "effectif": "..."
        }},
        "presentation": "...",
        "legal": {{
            "identite_entreprise": {{
                "date_creation": "...",
                "forme_juridique": "...",
                "noms_commerciaux": "...",
                "adresse_postale": "...",
                "telephone": "..."
            }},
            "numeros_identification": {{
                "numero_siren": "...",
                "numero_siret_siege": "...",
                "numero_tva_intracommunautaire": "...",
                "numero_rcs": "..."
            }},
            "informations_commerciales": {{
                "activite_code_naf_ape": "...",
                "activite_principale_declaree": "...",
                "convention_collective_deduite": "..."
            }},
            "taille_entreprise": {{
                "capital_social": "...",
                "effectif": "...",
                "chiffre_affaires": "..."
            }},
            "informations_juridiques": {{
                "statut_rcs": "...",
                "statut_insee": "...",
                "statut_rne": "..."
            }},
            "juridictions": {{
                "greffe_paris": "...",
                "numero_dossier": "...",
                "code_greffe": "..."
            }}
        }},
        "procedures_collectives": {{
            "statut": "...",
            "date_ouverture": "...",
            "type_procedure": "...",
            "details": "...",
            "greffe": "...",
            "reference": "..."
        }},
        "entreprises_liees": {{
            "nombre_societes_liees": "...",
            "entreprises_mentionnees": [
                {{
                    "nom_entreprise_personne": "...",
                    "siren": "...",
                    "siret": "..."
                }}
            ]
        }},
        "dirigeants": [
            {{
                "statut": "...",
                "depuis_le": "...",
                "nom_complet": "...",
                "fonction": "..."
            }}
        ],
        "nombre_etablissements": "...",
        "etablissements": [
            {{
                "statut": "...",
                "depuis_le": "...",
                "nom": "...",
                "type": "...",
                "siret": "...",
                "activite": "...",
                "adresse": "..."
            }}
        ],
        "cartographie": {{
            "entreprises_controlees": [
                {{
                    "nom_entreprise": "...",
                    "siren": "...",
                    "pourcentage_controle": "...",
                    "type_controle": "...",
                    "statut": "..."
                }}
            ],
            "entreprises_controles": [
                {{
                    "nom_entreprise": "...",
                    "siren": "...",
                    "pourcentage_controle": "...",
                    "type_controle": "...",
                    "statut": "..."
                }}
            ],
            "filiales": [
                {{
                    "nom_entreprise": "...",
                    "siren": "...",
                    "pourcentage_participation": "...",
                    "type_participation": "...",
                    "statut": "..."
                }}
            ],
            "participations": [
                {{
                    "nom_entreprise": "...",
                    "siren": "...",
                    "pourcentage_participation": "...",
                    "type_participation": "...",
                    "statut": "..."
                }}
            ]
        }},
        "director_profile": {{
            "identite": {{
                "nom_complet": "...",
                "date_naissance": "...",
                "entreprises": "...",
                "activite": "...",
                "commanditaire": "..."
            }},
            "entreprises": [
                {{
                    "statut": "...",
                    "depuis_le": "...",
                    "nom_entreprise": "...",
                    "fonction": "...",
                    "siren": "...",
                    "siret": "...",
                    "adresse": "...",
                    "secteur_activite": "..."
                }}
            ]
        }}
    }}

    6. Skip sections with images, ads or non-textual content.

    7. **EXTRACT NOMBRE D'ÉTABLISSEMENTS**: Count and extract the total number of establishments (including headquarters and secondary establishments) and include this information in the "nombre_etablissements" field. This count is critical for the client requirements.

    8. **EXTRACT CARTIOGRAPHY DATA**: After completing the company page extraction, look for a button with the text "Explorer la cartographie" on the company's profile page. If found, click on this button to navigate to the cartography page. Extract all available cartography information including:
       - Entreprises contrôlées (controlled companies)
       - Entreprises contrôles (controlling companies) 
       - Filiales (subsidiaries)
       - Participations (participations)
       Include this data in the "cartographie" section of the JSON output above.

    9. **EXTRACT PROCEDURES COLLECTIVES**: Look for the "Les procédures collectives" section on the company's profile page. Extract all available information about collective procedures including:
       - Statut (status)
       - Date d'ouverture (opening date)
       - Type de procédure (procedure type)
       - Détails (details)
       - Greffe (court registry)
       - Référence (reference)
       Include this data in the "procedures_collectives" section of the JSON output above.

    If the director name is found, perform the following additional steps:

    10. Go back to societe.com homepage (https://www.societe.com/) and accept cookies if prompted.

    11. **Locate the search bar for the first time and find it and click it again.** Ensure that the search bar is active before entering the director's name, then press Enter.

    12. Scroll to the **top of the results page** and examine the search results. Identify the correct profile by matching the company's name.

    13. Once you find the correct director, extract and organize all available information about the director and include it in the director_profile section of the JSON above.

    Important Notes:
    - Always scroll to the top before performing searches or analyzing results.
    - If the section contains an expander, ensure to expand it before extracting data.
    - Pay special attention to extracting the COUNT of establishments as this is a specific client requirement
    - Use null for missing values, empty arrays [] for missing lists.
    - If information for a section is unavailable or unparseable, set the value to null or empty array as appropriate.
    - If the director name is not provided, set director_profile to null.
    - If multiple items exist in arrays (dirigeants, etablissements), include all items.
    - Return ONLY valid JSON format - no additional text or formatting.
    - Ensure all JSON keys use snake_case format.
    - DO NOT include any explanatory text, headers, or markdown formatting.
    - DO NOT mention the source in text format - it's already in the JSON.
    - Your response should start with {{ and end with }}.
    
    REMEMBER: The output must be parseable JSON that starts with {{ and ends with }}. No other text should be included!
    """
