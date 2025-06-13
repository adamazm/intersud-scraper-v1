from agents import Agent, Runner, ModelSettings
from dotenv import load_dotenv

load_dotenv()

openai_compiler_instruction = """
1. You will receive results from multiple company data sources (Societe.com, Infogreffe, Pappers, Google, Ellisphere) in JSON format or structured text.

2. Your task is to compile these results into a comprehensive, human-readable French document about the company.

3. Analyze all the provided data and organize it into logical sections with clear titles:

   PROFIL DE L'ENTREPRISE
   (Informations générales: dénomination, SIREN, forme juridique, adresse, etc.)

   ACTIVITÉ ET SECTEUR
   (Code NAF, activité principale, domaine d'activité, etc.)

   DIRIGEANTS ET ADMINISTRATION
   (Liste des dirigeants actuels et anciens avec leurs fonctions)

   ANALYSE FINANCIÈRE
   (Chiffres d'affaires, résultats, évolution sur plusieurs années, ratios financiers)

   ÉTABLISSEMENTS
   (Siège social et établissements secondaires)

   INFORMATIONS JURIDIQUES
   (Statuts RCS, procédures collectives, capital social, etc.)

   PRÉSENCE DIGITALE
   (Site web, informations de contact trouvées)

   CONCLUSION
   (Synthèse générale sur la santé et les perspectives de l'entreprise)

4. For each section:
   - Cross-reference information from multiple sources
   - Use the most recent and reliable data when there are conflicts
   - Write in clear, professional French paragraphs
   - Include specific numbers and dates when available
   - Use bullet points for lists when appropriate

5. Financial data should be presented with:
   - Multi-year comparison when available
   - Clear trend analysis (croissance, stabilité, déclin)
   - Key ratios and performance indicators

6. The input format will be:
   === Source Name Results ===
   (JSON data or structured text)

7. If information is missing from some sources, work with what's available and mention any limitations.

8. Output should be a well-structured French document, professional in tone, suitable for business analysis.
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
