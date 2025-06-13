def google_task(parsed_info):
    return f"""
    By reading the parsed info: {parsed_info}, find the company's name and go to https://www.google.com/.

    Enter the company's name in the search bar and click on the most relevant result.

    Then make a conclusion about the company with what you found on the page in FRENCH.

    The final output should be a human readable text.

    IMPORTANT:
    - If no website is found, return "Pas de site web trouvé"
    """
