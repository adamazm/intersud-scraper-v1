def societe_scrape_task(company_id: str, id_type):
    """
    Societe scraping task to retrieve company and director information.

    :param company_id: The identification of the company to scrape data for.
    :param id_type: The type of ID (e.g. Name, SIREN, SIRET) to be used for scraping.
    :return: A formatted string with instructions for scraping Societe.
    """
    return f"""Follow these steps:
    Go to https://www.societe.com/

    1.  Accept cookies if prompted.

    2. **Locate the search bar for the first time and click it.** Ensure that the search bar is active and ready for input before proceeding. Only after confirming the search bar is active, enter the company's identifications: {company_id}, which is the company's {id_type}, and press Enter.

    3. Wait for the search results to load to ensure all results are correctly loaded.

    4. Click on the first relevant result to access the company's profile.

    5. Scroll to the top of the screen first then extract and organize all available information about the company following this example:
        - **Identité**:
            - SIREN: ...
            - Date de création: ...
            - Forme juridique: ...
            - Statut: ... (example: Active, Inactive)
            - Adresse: ...
            - Dirigeants: ...
            - Code NAF ou APE: ...
            - Source d'information: ...
        
        - **Récapitulatif**:
            - Dernière modification le: ...
            - Procédures collective: ...
            - Solvabilité: ... (if available)
            - Publications des comptes: ...
            - Score Extra-financier: ... (if available)
            - Score Carbone: ... (if available)
            - Taille de l'entreprise: ... (if available)
            - Effectif: ... (if available)

        - **Présentation**:
            - (Take all available information from this section as it is. For example, if the section is a paragraph, extract the entire paragraph. If it contains a list, extract the entire list. Ignore the buttons to download documents.)

        - **Légal**:
            - Identité entreprise:
                - Date de création: ...
                - Forme juridique: ...
                - Nom commerciaux: ...
                - Adresse postale: ...
                - Téléphone: ...
            
            - Numéros d'identification:
                - Numéro SIREN: ...
                - Numéro SIRET du siège: ...
                - Numéro TVA intracommunautaire: ...
                - Numéro RCS: ...

            - Informations commerciales:
                - Activité (Code NAF ou APE): ...
                - Activité principale déclarée: ...
                - Convention collective déduite: ...
            
            - Taille de l'entreprise:
                - Capital social: ...
                - Effectif: ... (if available)
                - Chiffre d'affaires: ... (if available)

            - Informations juridiques:
                - Statut RCS: ...
                - Statut INSEE: ...
                - Statut RNE: ...
            
            - Juridictions:
                - Greffe de Paris: ... (if available)
                - Numéro de dossier: ... (if available)
                - Code greffe: ... (if available)

        - **Entreprises Liées**:
            - Nombre de sociétés liées: ... (if available)

            - Entreprises liées mentionnées:
                - Nom de l'entreprise/personne: ...
                - SIREN: ... (if available)
                - SIRET: ... (if available)

                - (Other entreprises liées if available)

        - **Dirigeants**:
            - Statut: ... (example: Actuel, Ancien)
            - Depuis le: ... (if available)
            - Nom Complet: ...
            - Fonction: ...

        - **Établissements**:
            - Statut: ... (example: Ouvert, Fermé)
            - Depuis le: ... (if available)
            - Nom: ...
            - Type: ... (example: Siège, Établissement secondaire)
            - SIRET: ...
            - Activité: ... (if available)
            - Adresse: ...

            - (Other établissements if available)

    6. Skip sections with images, ads or non-textual content.

    If the director name is found, perform the following additional steps:

    7. Go back to societe.com homepage (https://www.societe.com/) and accept cookies if prompted.

    8. **Locate the search bar for the first time and find it and click it again.** Ensure that the search bar is active before entering the director's name, then press Enter.

    9. Scroll to the **top of the results page** and examine the search results. Identify the correct profile by matching the company's name.

    10. Once you find the correct director, extract and organize all available information about the director, for example:

        - **Identité**:
            - Nom Complet: ...
            - Date de naissance: ...
            - Entreprises: ... (if available)
            - Activité: ... (if available)
            - Comandataire: ... (if available)
        
        - **Entreprise(s) de (the director's name)**:
            - Statut: ... (example: Actuel, Ancien)
            - Depuis le: ... (if available)
            - Nom de l'entreprise: ...
            - Fonction: ... (if available)
            - SIREN: ... (if available)
            - SIRET: ... (if available)
            - Adresse: ... (if available)
            - Secteur d'activité: ... (if available)

            - (Other entreprises if available)

    Important Notes:
    - Always scroll to the top before performing searches or analyzing results.
    - If the section contains an expander, ensure to expand it before extracting data. For example in the **Légal** section, expand the **Taille de l'entreprise** section to extract the **Capital social** and **Effectif** information.
    - If information for a section is unavailable or unparseable, skip that section and continue.
    - If the director name is not provided, only extract the company information.
    - If the information is a list, ensure to extract all items and present them in a readable format.
    - If the information is a paragraph, extract the entire paragraph.

    The final output should be a clean, human-readable document containing all of the extracted and organized information and indicate at the top of the document that the info is scraped from Societe.com.
    
    """
