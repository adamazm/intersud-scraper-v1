import streamlit as st
from api.api_client import ApiClient
from constants import *
import json


def safe_currency_format(value, default=0):
    """
    Safely format a value as currency, handling None and non-numeric values.
    
    Args:
        value: The value to format (could be None, int, float, or string)
        default: Default value to use if value is None or invalid
    
    Returns:
        str: Formatted currency string
    """
    if value is None:
        value = default
    
    try:
        # Convert to float if it's a string
        if isinstance(value, str):
            value = float(value)
        
        # Format as currency
        if value == 0:
            return "€0"
        else:
            return f"€{value:,.0f}"
    except (ValueError, TypeError):
        return f"€{default:,.0f}" if default != 0 else "€0"


def safe_number_format(value, default=0):
    """
    Safely format a number, handling None and non-numeric values.
    
    Args:
        value: The value to format (could be None, int, float, or string)
        default: Default value to use if value is None or invalid
    
    Returns:
        float: The numeric value or default
    """
    if value is None:
        return default
    
    try:
        if isinstance(value, str):
            return float(value)
        return float(value)
    except (ValueError, TypeError):
        return default


def init_session_state():
    if "selected_company" not in st.session_state:
        st.session_state.selected_company = None
    if "scraping_results" not in st.session_state:
        st.session_state.scraping_results = None


def render_search_tab():
    st.header("Chercher une entreprise")
    company_id = st.text_input("ID de l'entreprise")
    id_type = st.selectbox("Type d'Identifiant", ["Nom", "SIREN", "SIRET"])

    if st.button("Rechercher"):
        st.session_state.id_type = id_type
        display_searched_company(company_id, id_type)

    # Display selected company info in the search tab
    if st.session_state.selected_company is not None:
        st.divider()
        st.header("Entreprise sélectionnée")
        display_company_info()


def display_searched_company(company_id, id_type: str):
    if id_type == "Nom":
        try:
            response = api_client.get_societe_api_results(company_id)
            if response.status_code == 200:
                result = response.json()
                companies = result.get("data", [])

                if companies:
                    for company in companies:
                        with st.expander(f"{company.get('nomcommercial', 'N/A')}"):
                            st.write(f"SIREN: {company.get('siren', 'N/A')}")
                            st.write(f"Ville: {company.get('cpville', 'N/A')}")

                            st.button("Select", key=f"{company.get('siren', '')}",
                                      on_click=select_company, args=(company, id_type))
                else:
                    st.error(NO_COMPANIES_FOUND_ERROR)
            else:
                st.error(f"Erreur: {response.status_code}")
        except Exception as e:
            st.error(
                f"Erreur lors de la récupération des entreprises: {str(e)}")
    else:
        st.write("## Confirmer l'entreprise:")
        st.write(f"{id_type}: **{company_id}**")
        st.button("Confirmer", key=f"{company_id}",
                  on_click=select_company, args=(company_id, id_type))


def display_company_info():
    if st.session_state.selected_company["id_type"] == "Nom":
        company = st.session_state.selected_company["company_id"]
        st.write(
            f"**Nom de l'entreprise:** {company.get('nomcommercial', 'N/A')}")
        st.write(f"**SIREN:** {company.get('siren', 'N/A')}")
        st.write(f"**Ville:** {company.get('cpville', 'N/A')}")
    else:
        st.write(
            f"**{st.session_state.selected_company['id_type']}: **{st.session_state.selected_company['company_id']}")

    if st.button("Commencer"):
        progress_container = st.container()
        scrape_company(st.session_state.selected_company, progress_container)


def scrape_company(company, progress_container):
    if company["id_type"] == "Nom":
        company_id = company["company_id"]["siren"]
    else:
        company_id = company["company_id"]

    with progress_container.status("Récupération des résultats...", state="running", expanded=True):
        try:
            st.write("- Démarrage du processus de scraping...")
            # Get the task ID
            response = api_client.scrape_company(
                company_id, company["id_type"])

            # Create progress bar
            my_bar = progress_container.progress(0.0)

            if response.status_code != 200:
                st.error(SCRAPE_FAILED)
                return False

            result = response.json()
            task_data = result.get("data", {})
            task_id = task_data.get("task_id")

            st.write(f"- ID de la tâche: {task_id}")
            st.write("- Lancement des scrapers...")

            # Poll with progress bar
            result = api_client.poll_task_status(
                task_id, progress_container, my_bar)

            if result:
                my_bar.progress(1.0)
                st.write("- Tous les scrapers ont été exécutés avec succès!")

                # Store results in session state
                st.session_state.scraping_results = result.get("data", {})

                # Switch to results tab automatically (optional)
                st.success(
                    "Scraping terminé! Vérifiez l'onglet Résultats pour voir les données.")
                return True
            else:
                st.error(SCRAPE_FAILED)
                return False

        except Exception as e:
            st.error(f"{SCRAPE_FAILED}: {e}")
            return False


def select_company(company_id, id_type: str):
    st.session_state.selected_company = {
        "company_id": company_id,
        "id_type": id_type
    }


def render_ellisphere_results(ellisphere_data):
    """
    Render ellisphere results with a financial dashboard style for JSON data.
    """
    st.subheader("📊 Données Financières Ellisphere")

    if not ellisphere_data:
        st.warning("Aucune donnée retournée par le scraper Ellisphere")
        return

    if isinstance(ellisphere_data, list):
        if len(ellisphere_data) == 0:
            st.warning("Aucun rapport trouvé dans les données Ellisphere")
            return

        st.write(f"**Trouvé {len(ellisphere_data)} rapports:**")

        for item in ellisphere_data:
            if isinstance(item, dict) and 'year' in item and 'result' in item:
                year = item['year']
                result = item['result']
                
                if result.get('status') == 'success' and result.get('format') == 'json':
                    # Financial Dashboard Style for JSON data
                    data = result['data']
                    if 'company_financial_report' in data:
                        report = data['company_financial_report']
                        
                        # Main header for the year
                        st.header(f"📈 Rapport Financier - {report.get('report_year', year)}")
                        
                        # Basic info in columns
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Année", report.get('report_year', year))
                        with col2:
                            st.metric("Devise", report.get('currency', 'N/A'))
                        with col3:
                            st.metric("Confidentialité", report.get('privacy', 'N/A'))
                        
                        # Process periods
                        periods = report.get('periods', [])
                        if len(periods) >= 2:
                            current = periods[0]
                            previous = periods[1]
                            
                            st.subheader("📊 Comparaison Annuelle")
                            
                            # Key metrics comparison in 4 columns
                            col1, col2, col3, col4 = st.columns(4)
                            
                            # Revenue comparison
                            with col1:
                                current_revenue = safe_number_format(current.get('income_statement', {}).get('net_revenue', 0))
                                previous_revenue = safe_number_format(previous.get('income_statement', {}).get('net_revenue', 0))
                                revenue_change = current_revenue - previous_revenue
                                st.metric(
                                    "Chiffre d'Affaires", 
                                    f"{safe_currency_format(current_revenue)}", 
                                    f"{safe_currency_format(revenue_change)}" if revenue_change != 0 else None
                                )
                            
                            # Assets comparison
                            with col2:
                                current_assets = safe_number_format(current.get('balance_sheet_assets', {}).get('total_assets', 0))
                                previous_assets = safe_number_format(previous.get('balance_sheet_assets', {}).get('total_assets', 0))
                                assets_change = current_assets - previous_assets
                                st.metric(
                                    "Total Actif", 
                                    f"{safe_currency_format(current_assets)}", 
                                    f"{safe_currency_format(assets_change)}" if assets_change != 0 else None
                                )
                            
                            # Equity comparison
                            with col3:
                                current_equity = safe_number_format(current.get('balance_sheet_liabilities', {}).get('total_equity', 0))
                                previous_equity = safe_number_format(previous.get('balance_sheet_liabilities', {}).get('total_equity', 0))
                                equity_change = current_equity - previous_equity
                                st.metric(
                                    "Capitaux Propres", 
                                    f"{safe_currency_format(current_equity)}", 
                                    f"{safe_currency_format(equity_change)}" if equity_change != 0 else None
                                )
                            
                            # Net income comparison
                            with col4:
                                current_income = safe_number_format(current.get('income_statement', {}).get('net_income', 0))
                                previous_income = safe_number_format(previous.get('income_statement', {}).get('net_income', 0))
                                income_change = current_income - previous_income
                                st.metric(
                                    "Résultat Net", 
                                    f"{safe_currency_format(current_income)}", 
                                    f"{safe_currency_format(income_change)}" if income_change != 0 else None
                                )
                            
                            # Detailed breakdown for each period
                            for i, period in enumerate(periods):
                                period_num = period.get('period_number', i+1)
                                end_date = period.get('end_date', 'N/A')
                                
                                with st.expander(f"📋 Détails Période {period_num} - {end_date}", expanded=i==0):
                                    
                                    # Balance Sheet Assets
                                    st.subheader("💰 Actif du Bilan")
                                    assets = period.get('balance_sheet_assets', {})
                                    
                                    asset_col1, asset_col2 = st.columns(2)
                                    with asset_col1:
                                        st.write(f"**Total Actif:** {safe_currency_format(assets.get('total_assets', 0))}")
                                        st.write(f"**Actif Immobilisé:** {safe_currency_format(assets.get('total_fixed_assets', 0))}")
                                        st.write(f"**Actif Circulant:** {safe_currency_format(assets.get('total_current_assets', 0))}")
                                    with asset_col2:
                                        st.write(f"**Trésorerie:** {safe_currency_format(assets.get('cash_and_equivalents', 0))}")
                                        st.write(f"**Créances Clients:** {safe_currency_format(assets.get('accounts_receivable', 0))}")
                                        st.write(f"**Autres Participations:** {safe_currency_format(assets.get('other_investments', 0))}")
                                    
                                    # Balance Sheet Liabilities
                                    st.subheader("🏛️ Passif du Bilan")
                                    liabilities = period.get('balance_sheet_liabilities', {})
                                    
                                    liab_col1, liab_col2 = st.columns(2)
                                    with liab_col1:
                                        st.write(f"**Capital Social:** {safe_currency_format(liabilities.get('share_capital', 0))}")
                                        st.write(f"**Capitaux Propres:** {safe_currency_format(liabilities.get('total_equity', 0))}")
                                    with liab_col2:
                                        st.write(f"**Total Dettes:** {safe_currency_format(liabilities.get('total_debt', 0))}")
                                        st.write(f"**Total Passif:** {safe_currency_format(liabilities.get('total_liabilities', 0))}")
                                    
                                    # Income Statement
                                    st.subheader("📈 Compte de Résultat")
                                    income = period.get('income_statement', {})
                                    
                                    income_col1, income_col2 = st.columns(2)
                                    with income_col1:
                                        st.write(f"**Chiffre d'Affaires:** {safe_currency_format(income.get('net_revenue', 0))}")
                                        st.write(f"**Produits d'Exploitation:** {safe_currency_format(income.get('total_operating_income', 0))}")
                                        st.write(f"**Charges d'Exploitation:** {safe_currency_format(income.get('total_operating_expenses', 0))}")
                                        st.write(f"**Résultat d'Exploitation:** {safe_currency_format(income.get('operating_result', 0))}")
                                    with income_col2:
                                        st.write(f"**Produits Financiers:** {safe_currency_format(income.get('total_financial_income', 0))}")
                                        st.write(f"**Résultat Financier:** {safe_currency_format(income.get('financial_result', 0))}")
                                        st.write(f"**Résultat Net:** {safe_currency_format(income.get('net_income', 0))}")
                                    
                                    st.divider()
                        
                        elif len(periods) == 1:
                            # Single period data
                            period = periods[0]
                            st.subheader(f"📋 Données Financières - {period.get('end_date', 'N/A')}")
                            
                            # Display the single period in the same detailed format
                            assets = period.get('balance_sheet_assets', {})
                            liabilities = period.get('balance_sheet_liabilities', {})
                            income = period.get('income_statement', {})
                            
                            # Key metrics in columns
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("Chiffre d'Affaires", f"{safe_currency_format(income.get('net_revenue', 0))}")
                            with col2:
                                st.metric("Total Actif", f"{safe_currency_format(assets.get('total_assets', 0))}")
                            with col3:
                                st.metric("Capitaux Propres", f"{safe_currency_format(liabilities.get('total_equity', 0))}")
                            with col4:
                                st.metric("Résultat Net", f"{safe_currency_format(income.get('net_income', 0))}")
                        
                        # Raw JSON view (collapsible)
                        with st.expander("🔍 Données JSON Brutes", expanded=False):
                            st.json(data)
                    else:
                        st.error("Format de données JSON invalide")
                    st.json(result['data'])
                
                elif result.get('status') == 'json_parse_failed':
                    # Fallback for failed JSON parsing
                    st.warning(f"⚠️ Échec de l'analyse JSON pour l'année {year}")
                    st.error(f"Erreur: {result.get('error', 'Erreur inconnue')}")
                    
                    with st.expander(f"📄 Données Brutes - Année {year}", expanded=False):
                        st.text(result.get('data', 'Aucune donnée disponible'))
                
                else:
                    # Handle other formats or errors
                    with st.expander(f"📄 Rapport {year}", expanded=False):
                        if result.get('data'):
                            if result.get('format') == 'french_text':
                                st.write("**Rapport en français:**")
                                st.text(result['data'])
                            else:
                                st.write("**Contenu du rapport:**")
                                st.text(result['data'])
                        else:
                            st.warning(f"Rapport {year} est vide ou contient une erreur")
                            if result.get('error'):
                                st.error(f"Erreur: {result['error']}")
            else:
                # Fallback for old format
                with st.expander(f"Rapport {len(ellisphere_data)}", expanded=False):
                    if item:
                        st.write("**Contenu du rapport:**")
                        st.text(item)
                    else:
                        st.warning("Rapport vide")
    else:
        # Handle single report (old format)
        st.write("**Rapport unique:**")
        st.text(ellisphere_data)


def render_results_tab():
    if st.session_state.scraping_results is not None:
        st.header("Résultats du scraping")

        results = st.session_state.scraping_results

        # Validate that results is a dictionary
        if not isinstance(results, dict):
            st.error(
                f"Format des résultats invalide. Attendu dictionnaire, obtenu {type(results).__name__}")
            st.write("Résultats bruts:")
            st.write(results)
            return

        # Get all available scraper results dynamically (exclude compiled_report)
        scraper_names = [name for name in results.keys() if name !=
                         "compiled_report"]

        if scraper_names:
            # Create tabs dynamically based on available results
            if len(scraper_names) == 1:
                # Single result - no need for tabs
                scraper_name = scraper_names[0]
                if scraper_name == "ellisphere":
                    render_ellisphere_results(results[scraper_name])
                else:
                    st.subheader(f"{scraper_name.title()} Données")
                    if results[scraper_name]:
                        # Try to parse as JSON for pretty display
                        try:
                            json_data = json.loads(results[scraper_name])
                            st.json(json_data)
                        except (json.JSONDecodeError, TypeError):
                            # Fallback to raw text if not valid JSON
                            st.write("**Données brutes:**")
                            st.text(results[scraper_name])
                    else:
                        st.warning(
                            f"Aucune donnée retournée par le scraper {scraper_name.title()}")
            else:
                # Multiple results - create tabs
                tab_labels = [
                    f"{name.title()} Résultats" for name in scraper_names]
                tabs = st.tabs(tab_labels)

                for i, scraper_name in enumerate(scraper_names):
                    with tabs[i]:
                        if scraper_name == "ellisphere":
                            render_ellisphere_results(results[scraper_name])
                        else:
                            st.subheader(f"Données de {scraper_name.title()}")
                            if results[scraper_name]:
                                # Try to parse as JSON for pretty display
                                try:
                                    json_data = json.loads(
                                        results[scraper_name])
                                    st.json(json_data)
                                except (json.JSONDecodeError, TypeError):
                                    # Fallback to raw text if not valid JSON
                                    st.write("**Données brutes:**")
                                    st.text(results[scraper_name])
                            else:
                                st.warning(
                                    f"Aucune donnée retournée par le scraper {scraper_name.title()}")
        else:
            st.warning("Aucun résultat de scraper trouvé dans les données")

        # Option to clear results
        if st.button("Effacer les résultats"):
            st.session_state.scraping_results = None
            st.rerun()

    else:
        st.info(
            "Aucun résultat de scraping disponible. Veuillez d'abord exécuter une tâche de scraping depuis l'onglet Recherche.")


def render_compiled_report(compiled_data):
    """
    Render the compiled report in a clean, readable format.
    """
    st.header("📋 Rapport Compilé")

    if not compiled_data:
        st.warning("Aucun rapport compilé disponible")
        return

    # Display the compiled document
    st.markdown(compiled_data)


def main():
    """
    Main function to run the Streamlit app.
    """
    # Set page config including the browser tab title
    st.set_page_config(
        page_title="Intersud AI Scraper",
        page_icon="🤖",
    )

    # Initialize the API client
    global api_client
    api_client = ApiClient()

    # Initialize the session state
    init_session_state()

    # Main UI
    st.title("Intersud AI Scraper")

    # Create main tabs - add Compiled Report tab
    search_tab, results_tab, compiled_report_tab = st.tabs(
        ["Chercher", "Résultats", "Rapport compilé"])

    with search_tab:
        render_search_tab()

    with results_tab:
        render_results_tab()

    with compiled_report_tab:
        if st.session_state.scraping_results is not None and "compiled_report" in st.session_state.scraping_results:
            render_compiled_report(
                st.session_state.scraping_results["compiled_report"])
        else:
            st.info(
                "Aucun rapport compilé disponible. Veuillez d'abord exécuter une tâche de scraping depuis l'onglet Recherche.")


if __name__ == "__main__":
    main()
