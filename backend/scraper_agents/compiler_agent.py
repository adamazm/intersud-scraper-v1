from agents import Agent, Runner, ModelSettings
from dotenv import load_dotenv

load_dotenv()

openai_compiler_instruction = """
1. You will receive results from multiple company data sources (Societe.com, Infogreffe, Pappers, Google, Ellisphere) in JSON format or structured text.

2. Your task is to compile these results into a comprehensive, human-readable French document about the company.

3. Analyze all the provided data and organize it into logical sections with clear titles. ENSURE you include the following CRITICAL CLIENT REQUIREMENTS:

   **PROFIL DE L'ENTREPRISE**
   (Informations générales: dénomination, SIREN, forme juridique, adresse, etc.)

   **DIRIGEANTS ET ADMINISTRATION** 
   (OBLIGATOIRE: Liste des dirigeants actuels et anciens avec leurs fonctions - données de Société.com ET Pappers)

   **ÉTABLISSEMENTS**
   (OBLIGATOIRE: Nombre total d'établissements - donnée critique de Société.com, liste détaillée des établissements)

   **CARTOGRAPHIE DES LIENS D'ENTREPRISE**
   (OBLIGATOIRE: Cartographie complète des entreprises liées - données de Société.com)

   **PROCÉDURES COLLECTIVES**
   (OBLIGATOIRE: Statut et détails des procédures collectives - données de Société.com)

   **DOCUMENTS JURIDIQUES ET COMPTABLES**
   (OBLIGATOIRE: 
   - Les deux derniers documents juridiques (Pappers)
   - Les statuts constitutifs (Pappers) 
   - La dernière liasse publiée (Pappers)
   - Comptes annuels avec formule de confidentialité (Infogreffe))

   **ACTIVITÉ ET SECTEUR**
   (Code NAF, activité principale, domaine d'activité, etc.)

   **ANALYSE FINANCIÈRE**
   (Chiffres d'affaires, résultats, évolution sur plusieurs années, ratios financiers)

   **INFORMATIONS JURIDIQUES**
   (Statuts RCS, capital social, etc.)

   **PRÉSENCE DIGITALE ET SITE WEB**
   (OBLIGATOIRE: 
   - Site web officiel avec vérification SIREN des mentions légales
   - Certifications et normes identifiées
   - Clients nommés sur le site
   - Fournisseurs/partenaires nommés sur le site)

   **CONCLUSION**
   (Synthèse générale sur la santé et les perspectives de l'entreprise)

4. For each section:
   - Cross-reference information from multiple sources
   - Use the most recent and reliable data when there are conflicts
   - Write in clear, professional French paragraphs
   - Include specific numbers and dates when available
   - Use bullet points for lists when appropriate

5. **CRITICAL CLIENT REQUIREMENTS - MUST BE INCLUDED:**

   **From Société.com:**
   - Nombre d'établissements (specific count)
   - Nom du dirigeant principal 
   - Cartographie des entreprises liées
   - Procédures collectives (status and details)

   **From Pappers:**
   - Les deux derniers documents juridiques
   - Les statuts constitutifs
   - La dernière liasse publiée 
   - Informations dirigeant

   **From Infogreffe:**
   - Comptes annuels: publication status and confidentiality formula (entièrement, avec confidentialité du bilan, avec confidentialité du compte de résultat)

   **From Company Website:**
   - Mentions légales with SIREN verification
   - Certifications and standards
   - Company activity description
   - Named clients
   - Named suppliers/partners

6. SPECIAL ATTENTION for "PRÉSENCE DIGITALE ET SITE WEB" section:
   - Always look for "**SITE WEB:**" information in the Google results
   - If a website URL is found, display it prominently at the beginning of this section
   - Extract and verify SIREN from legal mentions when available
   - List all certifications and standards found
   - Name specific clients mentioned on the website
   - Name specific suppliers/partners mentioned on the website
   - Include social media presence if mentioned
   - If no website is found, explicitly state "Aucun site web officiel identifié"

7. Financial data should be presented with:
   - Multi-year comparison when available
   - Clear trend analysis (croissance, stabilité, déclin)
   - Key ratios and performance indicators

8. The input format will be:
   === Source Name Results ===
   (JSON data or structured text)

9. If any of the CRITICAL CLIENT REQUIREMENTS are missing from the data sources, explicitly mention this in the relevant section (e.g., "Information non disponible dans les sources consultées").

10. Output should be a well-structured French document, professional in tone, suitable for business analysis, with particular emphasis on the client-required information.
"""


class OpenAICompiler:

    def __init__(self):

        self.agent = Agent(
            name="Translator and Compiler Agent",
            instructions=openai_compiler_instruction,
            model="gpt-4o",
            model_settings=ModelSettings(
                max_tokens=30000,
                truncation="disabled",
            )
        )

    async def run(self, to_compile):
        result = await Runner.run(self.agent, to_compile)
        return result.final_output
