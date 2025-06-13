import streamlit as st
from api.api_client import ApiClient
from constants import *
import json


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
    Render ellisphere results with expandable containers for each report.
    """
    st.subheader("Données Ellisphere")

    if not ellisphere_data:
        st.warning("Aucune donnée retournée par le scraper Ellisphere")
        return

    if isinstance(ellisphere_data, list):
        if len(ellisphere_data) == 0:
            st.warning("Aucun rapport trouvé dans les données Ellisphere")
            return

        st.write(f"**Trouvé {len(ellisphere_data)} rapports:**")

        for i, report in enumerate(ellisphere_data):
            # Create expandable container for each report
            with st.expander(f"Rapport {i + 1}", expanded=False):
                if report:
                    st.write("**Contenu du rapport:**")
                    st.text(report)
                else:
                    st.warning(f"Rapport {i + 1} est vide")
    else:
        # Single report
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

    # Initialize the API client
    global api_client
    api_client = ApiClient()

    # Initialize the session state
    init_session_state()

    # Main UI
    st.title("Intersud AI")

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
