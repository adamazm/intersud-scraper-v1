def google_scrape_task(company_id: str, id_type):
    """
    Task function to scrape Google search results for a given company name.
    """
    return f"""Perform a general Google search to gather the following information about the company using the company's identifications: {company_id}, which is the company's {id_type}":

    The company's phone number.

    The official website, if available.

    Relevant articles, news coverage, or press releases, particularly if the company is well-known or large.

    Find 5 relevants links and go through them to extract the information.

    Present the extracted information in human readable format, such as bullet points
    
    """
