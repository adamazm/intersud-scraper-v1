def infogreffe_scrape_task(company_id: str, id_type):
    """
    Infogreffe scraping task to retrieve company information.

    :param company_id: The identification of the company to scrape data for.
    :param id_type: The type of ID (e.g. Name, SIREN, SIRET) to be used for scraping.
    :return: A formatted string with instructions for scraping Infogreffe.
    """

    return f"""Follow these steps to efficiently retrieve company information from Infogreffe:

    1. Go to https://www.infogreffe.fr/ and accept cookies if prompted.

    2. Locate the search bar, ensure it is active, and enter the company's identifications: {company_id}, which is the company's {id_type}, then press Enter or click the search button.

    3. Wait for the results to load and click on the first relevant result to access the company profile.

    4. Scroll to the top of the page and expand all sections to ensure all information is visible.

    5. Extract and organize useful information from the following sections, presenting each in a clear and readable format, for example:

        - **Identité**:
            - Dénomination sociale: ...
            - SIRET: ...
            - Dirigeant: ...
            - Chiffre d'affaires: ...
            - Effectif: ...
            - Incsription: ...
            - Activité (code NAF): ...
            - Forme juridique: ...
        
        - SKIP THE DOCUMENTS SECTION!

        - **Dirigeants, administration, contrôle, associé ou membre**:
            - Nom Complet: ...
            - Fonction: ...
        
        - **Analyse Financière**:
            - Derniers chiffres clés:
                - Annee XXXX:
                    - Chiffre d'affaires: ...
                    - Résultat: ...
                    - Effectif: ...
                - Annee YYYY:
                    - Chiffre d'affaires: ...
                    - Résultat: ...
                    - Effectif: ...
            
            - Rapports de performance (if available):
                - Nom du rapport: ...
                - Description: ...
        
        - **Établissements**:
            - Nom: ...
            - Type: ... (example: Siège et établissement principal)
            - SIRET: ...
            - Adresse: ...


    6. If a section is missing or unparseable, label it as "Not available" and continue.

    Important Notes:
    - SKIP THE DOCUMENTS SECTION!
    - Ensure all sections are expanded before extracting data.
    - Ensure all the years present in the financial analysis are extracted.
    - If a section is unavailable, mark it as "Not available" and move on.
    - If the section has a list of items, ensure to extract all items and present them in a readable format.
    
    
    The final output should be a clean, human-readable document containing all of the extracted and organized information and indicate at the top of the document that the info is scraped from infogreffe.fr.
    """
