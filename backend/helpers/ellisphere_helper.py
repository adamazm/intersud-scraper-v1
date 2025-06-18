import requests
import xml.etree.ElementTree as ET
import json
import os

ellisphere_api_url = "https://services.data-access-gateway.com/1/rest/svcOnlineOrder"


def get_year_request(siren):
    # 101021 for get year

    return f"""<svcOnlineOrderRequest lang="FR" version="2.2">
        <admin>
        <client>
            <contractId>49120</contractId>
            <userPrefix>GEOCOM</userPrefix>
            <userId>NN427944</userId>
            <password>QU1WQVPGZZJ6</password>
        </client>
        <context>
            <appId version="1">WSPRO</appId>
            <date>2011-12-13T17:38:15+01:00</date>
        </context>
    </admin>
    <request>
        <id type="register" idName="SIREN">{siren}</id>
        <product range="101021" version="1" />
        <orderOptions>
            <financials>
                <year>
                    <date>2021</date>
                    <option>ALL</option>
                </year>
            </financials>
            <monitoringRequested>false</monitoringRequested>
        </orderOptions>
        <deliveryOptions>
            <outputMethod>raw</outputMethod>
        </deliveryOptions>
    </request>
</svcOnlineOrderRequest>"""


def get_detailed_report_request(siren, year):
    # 101021 for get detailed report

    return f"""<svcOnlineOrderRequest lang="FR" version="2.2">
        <admin>
        <client>
            <contractId>49120</contractId>
            <userPrefix>GEOCOM</userPrefix>
            <userId>NN427944</userId>
            <password>QU1WQVPGZZJ6</password>
        </client>
        <context>
            <appId version="1">WSPRO</appId>
            <date>2011-12-13T17:38:15+01:00</date>
        </context>
    </admin>
    <request>
        <id type="register" idName="SIREN">{siren}</id>
        <product range="101021" version="1" /> 
        <orderOptions>
            <financials>
                <year>
                    <date>{year}</date>
                    <option>ALL</option>
                </year>
            </financials>
            <monitoringRequested>false</monitoringRequested>
        </orderOptions>
        <deliveryOptions>
            <outputMethod>raw</outputMethod>
        </deliveryOptions>
    </request>
</svcOnlineOrderRequest>"""


# example call
siren = 552134736


def get_year_data(siren):
    """
    Make a POST request to get year data for a given SIREN

    Args:
        siren: The company SIREN number

    Returns:
        dict: A response dictionary with 'success', 'data', and 'error' keys
    """
    try:
        headers = {'Content-Type': 'application/xml'}
        response = requests.post(
            ellisphere_api_url,
            data=get_year_request(siren),
            headers=headers,
            timeout=30  # Add timeout to prevent hanging
        )

        if response.status_code == 200:
            return {
                'success': True,
                'data': response.text,
                'error': None
            }
        else:
            error_msg = f"API returned status code {response.status_code}"
            if response.text:
                error_msg += f": {response.text}"
            return {
                'success': False,
                'data': None,
                'error': error_msg
            }
    
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'data': None,
            'error': f"Network error: {str(e)}"
        }
    except Exception as e:
        return {
            'success': False,
            'data': None,
            'error': f"Unexpected error: {str(e)}"
        }


def get_detailed_report_data(siren, year):
    """
    Make a POST request to get detailed report data for a given SIREN and year

    Args:
        siren: The company SIREN number
        year: The year for which to get the detailed report

    Returns:
        dict: A response dictionary with 'success', 'data', and 'error' keys
    """
    try:
        headers = {'Content-Type': 'application/xml'}
        response = requests.post(
            ellisphere_api_url,
            data=get_detailed_report_request(siren, year),
            headers=headers,
            timeout=30  # Add timeout to prevent hanging
        )

        if response.status_code == 200:
            return {
                'success': True,
                'data': response.text,
                'error': None
            }
        else:
            error_msg = f"API returned status code {response.status_code}"
            if response.text:
                error_msg += f": {response.text}"
            return {
                'success': False,
                'data': None,
                'error': error_msg
            }
    
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'data': None,
            'error': f"Network error: {str(e)}"
        }
    except Exception as e:
        return {
            'success': False,
            'data': None,
            'error': f"Unexpected error: {str(e)}"
        }


def get_years_from_ellisphere(xml: str) -> list:
    """
    Extracts years from <date> tags within <financialsDisclaimer code="PUBLIC"> elements.

    Args:
        xml (str): XML content as a string.

    Returns:
        List[str]: A list of years (as strings).
    """
    try:
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
    
    except ET.ParseError as e:
        print(f"XML parsing error: {str(e)}")
        return []
    except Exception as e:
        print(f"Error extracting years: {str(e)}")
        return []


def parse_periods_from_file(company_id=None):
    """
    Parse all periods from the local detailed-reports.xml file.
    
    Args:
        company_id: Not used for file parsing, kept for compatibility
        
    Returns:
        dict: Dictionary with years as keys and parsed period XML as values
        Example: {"2023": "<period>...</period>", "2022": "<period>...</period>"}
    """
    try:
        # Construct the file path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        xml_file_path = os.path.join(current_dir, "..", "ellisphere_reports", "detailed-reports.xml")
        
        # Check if file exists
        if not os.path.exists(xml_file_path):
            return {
                'success': False,
                'data': None,
                'error': f"XML file not found at: {xml_file_path}"
            }
        
        # Read and parse the XML file
        with open(xml_file_path, 'r', encoding='utf-8') as file:
            xml_content = file.read()
        
        root = ET.fromstring(xml_content)
        periods_data = {}
        
        # Find all period elements at the root level
        for period in root.findall('period'):
            date_attr = period.get('date')
            if date_attr:
                # Convert the period element back to XML string
                period_xml = ET.tostring(period, encoding='unicode')
                periods_data[date_attr] = period_xml
        
        if not periods_data:
            return {
                'success': False,
                'data': None,
                'error': "No period elements found in the XML file"
            }
        
        return {
            'success': True,
            'data': periods_data,
            'error': None
        }
        
    except ET.ParseError as e:
        return {
            'success': False,
            'data': None,
            'error': f"XML parsing error: {str(e)}"
        }
    except Exception as e:
        return {
            'success': False,
            'data': None,
            'error': f"Error reading XML file: {str(e)}"
        }


def get_available_years_from_file():
    """
    Get list of available years from the local XML file.
    
    Returns:
        List[str]: List of available years
    """
    try:
        periods_response = parse_periods_from_file()
        if periods_response['success']:
            years = list(periods_response['data'].keys())
            return sorted(years, reverse=True)  # Sort years in descending order (newest first)
        else:
            print(f"Error getting years: {periods_response['error']}")
            return []
    except Exception as e:
        print(f"Error getting available years: {str(e)}")
        return []


def extract_year_xml_content(start_line=3, end_line=1533, file_path="ellisphere_reports/detailed-reports.xml"):
    """
    Extract specific lines from the XML report for a single year.
    
    Args:
        start_line (int): Starting line number (1-indexed)
        end_line (int): Ending line number (1-indexed, inclusive)
        file_path (str): Path to the XML file
    
    Returns:
        str: The extracted XML content as a valid XML string
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        # Convert to 0-indexed and extract the specified range
        extracted_lines = lines[start_line-1:end_line]
        
        # Wrap in root tags for valid XML
        xml_content = '<root>\n' + ''.join(extracted_lines) + '\n</root>'
        
        return xml_content
    except FileNotFoundError:
        print(f"Error: File {file_path} not found")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None


async def parse_year_to_json(start_line=3, end_line=1533, file_path="ellisphere_reports/detailed-reports.xml"):
    """
    Extract a year's financial data and convert it to structured JSON.
    
    Args:
        start_line (int): Starting line number (1-indexed)
        end_line (int): Ending line number (1-indexed, inclusive)
        file_path (str): Path to the XML file
    
    Returns:
        str: JSON formatted financial data
    """
    from scraper_agents.ellisphere_agent import EllisphereAgent
    
    # Extract XML content for the specified year
    xml_content = extract_year_xml_content(start_line, end_line, file_path)
    
    if xml_content is None:
        return None
    
    # Initialize agent and parse to JSON
    agent = EllisphereAgent()
    
    try:
        json_result = await agent.run(xml_content, operation_type="xml_to_json")
        return json_result
    except Exception as e:
        print(f"Error parsing XML to JSON: {e}")
        return None


def get_year_line_ranges(file_path="ellisphere_reports/detailed-reports.xml"):
    """
    Analyze the XML file to find line ranges for each year's data.
    
    Args:
        file_path (str): Path to the XML file
    
    Returns:
        dict: Dictionary with year as key and (start_line, end_line) as value
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        year_ranges = {}
        current_year = None
        start_line = None
        
        for i, line in enumerate(lines, 1):
            if '<period date=' in line:
                # Extract year from the line
                import re
                year_match = re.search(r'date="(\d{4})"', line)
                if year_match:
                    if current_year and start_line:
                        # End of previous year
                        year_ranges[current_year] = (start_line, i-1)
                    
                    current_year = year_match.group(1)
                    start_line = i
        
        # Handle the last year
        if current_year and start_line:
            year_ranges[current_year] = (start_line, len(lines))
        
        return year_ranges
    
    except Exception as e:
        print(f"Error analyzing file: {e}")
        return {}
