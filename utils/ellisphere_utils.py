import xml.etree.ElementTree as ET


def get_years_from_ellisphere(xml: str) -> list:
    """
    Extracts years from <date> tags within <financialsDisclaimer code="PUBLIC"> elements.

    Args:
        xml (str): XML content as a string.

    Returns:
        List[str]: A list of years (as strings).
    """
    root = ET.fromstring(xml)
    years = []

    public_disclaimers = root.findall(
        ".//financialsDisclaimer[@code='PUBLIC']")

    for disclaimer in public_disclaimers:
        date_elem = disclaimer.find(".//date")
        if date_elem is not None and date_elem.text:
            date_text = date_elem.text.strip()
            year = date_text.split("-")[0]
            years.append(year)

    return years


# example
