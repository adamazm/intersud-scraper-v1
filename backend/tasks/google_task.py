import random
import time


def google_task(parsed_info):
    return f"""
    By reading the parsed info: {parsed_info}, extract the COMPANY NAME using this priority order:
    
    COMPANY NAME EXTRACTION RULES:
    1. **PRIMARY:** Look for "noms_commerciaux" in legal > identite_entreprise > noms_commerciaux
    2. **SECONDARY:** Look for "denomination_sociale" in any identite section
    3. **TERTIARY:** Look for "nomcommercial" in main data
    4. **FALLBACK:** Look for "siren" or "siret" if no company name is found
    
    DO NOT USE:
    - Director names from "dirigeants" sections
    - Personal names that appear to be individuals
    - Address information
    
    EXAMPLE EXTRACTION:
    From: legal > identite_entreprise > noms_commerciaux: COMELSE
    Use: COMELSE as the search term
    
    Once you have the correct COMPANY NAME, go to https://duckduckgo.com.

    HUMAN-LIKE BEHAVIOR INSTRUCTIONS:
    - Move mouse naturally between actions (not instant jumps)
    - Add random pauses between 1-3 seconds between major actions
    - Simulate reading time by pausing before clicking
    - Vary typing speed (not too fast, not too slow)
    - Scroll in small increments, not large jumps
    - Move mouse slightly while "reading" content

    Follow these steps with REALISTIC HUMAN BEHAVIOR:

    1. **Navigate to DuckDuckGo:**
       - Go to https://duckduckgo.com
       - Wait 2-4 seconds for page to fully load
       - Move mouse around slightly as if looking at the page

    2. **Handle any pop-ups/consents:**
       - If any cookie consent or privacy notices appear, handle them naturally
       - Take 1-2 seconds to "read" before accepting/declining

    3. **Search preparation:**
       - Move mouse toward the search bar (don't click immediately)
       - Hover over the search bar for 0.5-1 second
       - Click on the search bar and wait briefly for cursor to appear

    4. **Typing the search query:**
       - Use ONLY the EXTRACTED COMPANY NAME from the rules above
       - Type ONLY the company name (example: "KREANCIA" not "KREANCIA site:domain.com")
       - Type with realistic human typing speed
       - Add occasional brief pauses (0.1-0.3 seconds) between words
       - If you make a "typo", backspace and correct it naturally
       - Pause 1-2 seconds after finishing typing
       - VERIFY you're searching for the company, not a person's name

    5. **Initiating search:**
       - Look for the search button or press Enter key
       - If using search button, move mouse to it and pause briefly before clicking
       - Wait 2-4 seconds for search results to load completely

    6. **Analyzing search results:**
       - Scroll down slowly to see all results (small increments)
       - Move mouse over different results as if reading titles
       - Pause 1-2 seconds on each result you're considering
       - Look for official company websites (avoid directories, social media as primary choice)

    7. **Selecting and visiting the website:**
       - Move mouse to the most relevant result (usually the official company website)
       - Hover for 1-2 seconds before clicking
       - Click on the result and wait for new page to load (3-5 seconds)

    **IMPORTANT: Once you click on the company website, DO NOT go back to DuckDuckGo. Stay on the company website and complete all the following steps on that site.**

    8. **Exploring the company website (STAY ON THIS SITE):**
       - You are now on the company's website - do not return to search
       - Scroll down slowly in small increments (100-200px at a time)
       - Pause every 2-3 scrolls to "read" content (2-4 seconds)
       - Move mouse occasionally to different parts of visible content
       - Look for key information: About page, contact info, services, etc.
       - If you see navigation menus, briefly hover over them
       - Spend 15-20 seconds total exploring the main site

    9. **Search for Legal Mentions within the website (DO NOT use search engines):**
       - Look for "Mentions légales", "Legal", or footer links on the current website
       - Click on legal mentions page if found within the website navigation
       - Search for SIREN number to verify company identity
       - Note any legal information found on the website
       - Spend 5-10 seconds reading this section

    10. **Search for Certifications and Standards within the website:**
        - Navigate within the website to find "Certifications", "Normes", "Quality", "Standards" pages
        - Check for logos or mentions of: ISO certifications, quality standards, industry certifications
        - Navigate to relevant pages using the website's own navigation menu
        - Note any certifications, accreditations, or standards mentioned on the site

    11. **Explore Company Activity within the website:**
        - Visit "About", "Services", "Produits", "Activités" pages using the site's navigation
        - Look for detailed descriptions of business activities on the website
        - Note main business sectors and services offered
        - Check for any specific industry focus or specializations

    12. **Search for Named Clients within the website:**
        - Look for "Clients", "References", "Témoignages", "Case Studies", "Portfolio" pages on the site
        - Check for client logos, testimonials, or project references on the website
        - Note any specifically named clients or partner companies mentioned on the site
        - Look in project descriptions or success stories on the website

    13. **Search for Named Suppliers/Partners within the website:**
        - Look for "Partenaires", "Fournisseurs", "Partners", "Suppliers" pages on the site
        - Check footer areas for partner logos or links within the website
        - Note any specifically mentioned suppliers, distributors, or business partners on the site
        - Look for technology partners or strategic alliances mentioned on the website

    14. **Gathering comprehensive information from the website:**
        - Focus on company description, services, contact information found on the site
        - Note the official website URL from the address bar
        - Look for any social media links or additional contact methods on the site
        - Compile all the specific information requested from the website content

    **CRITICAL: Complete all steps 8-14 on the company website. Do not return to DuckDuckGo or any search engine.**

    Your final output MUST follow this EXACT format in FRENCH:

    **SITE WEB:** [URL du site web principal de l'entreprise - ou "Pas de site web trouvé" si aucun site n'est trouvé]

    **MENTIONS LÉGALES & SIREN:**
    [Information trouvée dans les mentions légales, incluant la vérification du SIREN si trouvé - ou "Pas de mentions légales trouvées" si aucune information]

    **CERTIFICATIONS & NORMES:**
    [Liste des certifications, normes, standards mentionnés sur le site - ou "Aucune certification trouvée" si aucune information]

    **ACTIVITÉ:**
    [Description détaillée de l'activité de l'entreprise basée sur le site web]

    **CLIENTS NOMMÉS:**
    [Liste des clients spécifiquement nommés ou mentionnés - ou "Aucun client nommé trouvé" si aucune information]

    **FOURNISSEURS/PARTENAIRES NOMMÉS:**
    [Liste des fournisseurs ou partenaires spécifiquement nommés - ou "Aucun fournisseur/partenaire nommé trouvé" si aucune information]

    **PRÉSENCE DIGITALE:**
    [Description de la présence en ligne de l'entreprise]

    **INFORMATIONS COMPLÉMENTAIRES:**
    [Toute autre information pertinente trouvée sur le site web]

    CRITICAL REQUIREMENTS:
    - Start your response with "**SITE WEB:**" followed by the main website URL
    - If no official website is found, write "**SITE WEB:** Pas de site web trouvé"
    - Extract the exact URL from the search results or the website you visit
    - The website URL should be the main company website (usually domain.com or domain.fr)
    - NEVER rush through actions - always simulate realistic human timing
    - Vary your interaction patterns to avoid appearing robotic
    - If the website seems unrelated to the company, try the next search result
    - Be thorough in searching for the specific information requested on the company website
    - If information is not found in a category, clearly state so using the suggested phrases
    - DO NOT perform additional searches after finding the company website - stay on the site and scrape it thoroughly
    """
