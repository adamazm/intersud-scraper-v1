def pappers_scrape_task(company_id: str, id_type):
    """
    Pappers scraping task to retrieve company information.

    :param company_id: The identification of the company to scrape data for.
    :param id_type: The type of ID (e.g. Name, SIREN, SIRET) to be used for scraping.
    :return: A formatted string with instructions for scraping Pappers.
    """

    return f"""Follow these steps to scrape the data:

    1. Go to https://www.pappers.fr/

    2. Locate the search bar and input the company's identifications: {company_id}, which is the company's {id_type}, then press Enter to initiate the search.

    3. From the search results, click on the first result to access the company details.

    4. Once on the company page, extract and organize the following information:

        - **Informations juridiques de ...**: Include all relevant legal information.
        - **Activité de ...**: List all the details.
        - **Etablissement de l'entreprise**: List details about the company's establishments.
        - **Dirigeants et représentants de ...**: Provide information on the company's executives and representatives.
        - **Documents juridiques de...**: Summarize the available legal documents.
        - **Annonces BODACC de ...**: Include all BODACC announcements.
        - **Comptes annuels de ...**: Present the annual financial statements.
        - **Cartographie de ...**: Describe the company’s structure and relationships.
        - **Comment contacter ...**: Provide available contact information.
        - **Entreprises citées de ...**: List referenced companies if available.

    5. Structure the output in a clear, readable format with section titles and bullet points for each detail and indicate at the top of the document that the info is scraped from pappers.fr. For example:
        From Pappers.fr:
        
        Informations juridiques de ...:
        - Forme juridique: ...
        - Capital social: ...
        - Numéro SIREN: ...

        Etablissement de l'entreprise:
        - Adresse principale: ...
        - Autres établissements: ...

        Dirigeants et représentants de ...:
        - Nom: ...
        - Fonction: ...

    6. If information for a section is unavailable or unparseable, skip that section and continue.

    The final output should be a well-organized, human-readable text document containing all available information and indicate at the top of the document that the info is scraped from pappers.fr."""
