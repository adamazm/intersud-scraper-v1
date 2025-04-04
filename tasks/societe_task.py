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

    5. Scroll to the top of the screen first then extract and organize all available information about the company. Present the information in a **clear, readable format**.

    6. Skip sections with images, ads or non-textual content.

    If the director name is found, perform the following additional steps:

    7. Return to the **top of the page** and ensure the search bar is visible.

    8. **Locate the search bar for the first time and click it again.** Ensure that the search bar is active before entering the director's name, then press Enter.

    9. If the search bar is unavailable, return to the homepage (https://www.societe.com/) and repeat the process to activate the search bar before entering the director's name.

    10. Scroll to the **top of the results page** and examine the search results. Identify the correct profile by matching the company name: {company_id}.

    11. Once you find the correct director, extract and organize all available information about the director in a **clear, readable format**.

    12. Compile the company and director information into a **well-organized document** with clear section headers and bullet points. For example:

        Company Information:
        - Company Name: ...
        - Address: ...
        - Secondary Addresses: ...

        Director Information:
        - Full Name: ...
        - Position: ...
        - Company Name: ...

    Important Notes:
    - Always scroll to the top before performing searches or analyzing results.
    - If information for a section is unavailable or unparseable, skip that section and continue.
    - If the director name is not provided, only extract the company information.
    - The final output should be a **human-readable document** containing all available information with clear section titles and bullet points.
    """
