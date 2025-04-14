import requests


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
        The response text or None if request fails
    """
    headers = {'Content-Type': 'application/xml'}
    response = requests.post(
        ellisphere_api_url,
        data=get_year_request(siren),
        headers=headers
    )

    if response.status_code == 200:
        return response.text
    else:
        print(f"Error: Status code {response.status_code}")
        return None


def get_detailed_report_data(siren, year):
    """
    Make a POST request to get detailed report data for a given SIREN and year

    Args:
        siren: The company SIREN number
        year: The year for which to get the detailed report

    Returns:
        The response text or None if request fails
    """
    headers = {'Content-Type': 'application/xml'}
    response = requests.post(
        ellisphere_api_url,
        data=get_detailed_report_request(siren, year),
        headers=headers
    )

    if response.status_code == 200:
        return response.text
    else:
        print(f"Error: Status code {response.status_code}")
        return None


# Example call
