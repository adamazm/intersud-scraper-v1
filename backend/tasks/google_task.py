import random
import time


def google_task(parsed_info):
    return f"""
    By reading the parsed info: {parsed_info}, find the company's name and go to https://duckduckgo.com.

    Follow these steps:
    1. Find the search bar input and type the company name.
    2. Then click the search button(Aria-label="Search")
    3. After search results appear, find the most relevant result and click on it.
    4. On the target website, scroll naturally and pause to read content
    5. Take 3-5 seconds to analyze the content

    Your final output MUST follow this EXACT format in FRENCH:

    **SITE WEB:** [URL du site web principal de l'entreprise - ou "Pas de site web trouvé" si aucun site n'est trouvé]

    **PRÉSENCE DIGITALE:**
    [Description de la présence en ligne de l'entreprise]

    **INFORMATIONS TROUVÉES:**
    [Résumé détaillé des informations trouvées sur le site web en français]

    IMPORTANT:
    - Start your response with "**SITE WEB:**" followed by the main website URL
    - If no official website is found, write "**SITE WEB:** Pas de site web trouvé"
    - Extract the exact URL from the search results or the website you visit
    - The website URL should be the main company website (usually domain.com or domain.fr)
    - Use random delays between actions to appear more human-like
    - Scroll naturally through pages instead of jumping directly to content
    """
