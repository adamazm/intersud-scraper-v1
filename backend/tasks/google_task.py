import random
import time


def google_task(parsed_info):
    return f"""
    By reading the parsed info: {parsed_info}, find the company's name and go to https://www.google.com/.

    Follow these steps to imitate human behavior:
    1. Wait 2-4 seconds before typing the company name
    2. Type the company name with random delays between keystrokes (0.1-0.3 seconds)
    3. Wait 1-2 seconds before clicking the search button
    4. After search results appear, scroll down slowly and pause occasionally
    5. Wait 2-3 seconds before clicking on the most relevant result
    6. On the target website, scroll naturally and pause to read content
    7. Take 3-5 seconds to analyze the content

    Then make a conclusion about the company with what you found on the page in FRENCH.

    The final output should be a human readable text.

    IMPORTANT:
    - If no website is found, return "Pas de site web trouvé"
    - Use random delays between actions to appear more human-like
    - Scroll naturally through pages instead of jumping directly to content
    """
