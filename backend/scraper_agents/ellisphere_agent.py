from dotenv import load_dotenv
from agents import Agent, Runner, ModelSettings

load_dotenv()


xml_parser_instructions = """
When given an XML financial report from Ellisphere, extract and organize the data into a structured JSON format.

For each <period> tag in the XML, extract the following key information:

1. **Period Information:**
   - Date (from date attribute)
   - Privacy level (from privacy attribute) 
   - Category (from category attribute)
   - Period type (from period attribute)

2. **Key Financial Metrics:**
   Extract the most important financial elements with their values for both periods (current and previous year):
   
   **Balance Sheet Assets:**
   - Total actif immobilisé (BJ3) - Total fixed assets
   - Total actif circulant (CJ3) - Total current assets  
   - Total général actif (CO3) - Total assets
   - Disponibilités (CF3) - Cash and equivalents
   - Clients et comptes rattachés (BX3) - Accounts receivable
   - Autres participations (CU3) - Other investments
   
   **Balance Sheet Liabilities:**
   - Capital social (DA/FP01) - Share capital
   - Total capitaux propres (FP00) - Total equity
   - Total dettes (TD00) - Total debt
   - Total général passif (TP00) - Total liabilities
   
   **Income Statement:**
   - Chiffres d'affaires nets (CA00) - Net revenue
   - Total des produits d'exploitation (PE00) - Total operating income
   - Total des charges d'exploitation (CE00) - Total operating expenses
   - Résultat d'exploitation (RE00) - Operating result
   - Total des produits financiers (PF00) - Total financial income
   - Résultat financier (RF00) - Financial result
   - Bénéfice ou perte (RN00) - Net income/loss

3. **Currency and Period Details:**
   - Currency code and unit
   - Sector information
   - Duration of the reporting period

Return ONLY raw JSON (no markdown, no code blocks, no ```json formatting). Start directly with { and end with }. Use this exact structure:

{
  "company_financial_report": {
    "report_year": "YYYY",
    "privacy": "PUBLIC/PRIVATE",
    "category": "report category",
    "currency": "EUR",
    "periods": [
      {
        "period_number": 1,
        "end_date": "YYYY-MM-DD",
        "duration_months": 12,
        "balance_sheet_assets": {
          "total_fixed_assets": 0.00,
          "total_current_assets": 0.00,
          "total_assets": 0.00,
          "cash_and_equivalents": 0.00,
          "accounts_receivable": 0.00,
          "other_investments": 0.00
        },
        "balance_sheet_liabilities": {
          "share_capital": 0.00,
          "total_equity": 0.00,
          "total_debt": 0.00,
          "total_liabilities": 0.00
        },
        "income_statement": {
          "net_revenue": 0.00,
          "total_operating_income": 0.00,
          "total_operating_expenses": 0.00,
          "operating_result": 0.00,
          "total_financial_income": 0.00,
          "financial_result": 0.00,
          "net_income": 0.00
        }
      },
      {
        "period_number": 2,
        "end_date": "YYYY-MM-DD",
        "duration_months": 12,
        "balance_sheet_assets": { /* same structure */ },
        "balance_sheet_liabilities": { /* same structure */ },
        "income_statement": { /* same structure */ }
      }
    ]
  }
}

Critical requirements:
- Return PURE JSON only - no markdown formatting, no ```json blocks, no explanatory text
- Start response with { and end with }
- Extract actual numeric values from the XML (remove .00 if they are zeros)
- Include both current year (period 1) and previous year (period 2) data when available
- Handle missing values gracefully (use null or 0)
- Keep all amounts in the original currency format
- Focus on the most significant financial indicators for business analysis
"""

compiler_instructions = """
1. Given the data from multiple sources, create a clean, human-readable document in paragraph/bullet point format if needed for the financial data by year.

2. Translate the document into French.

Important:
- Just give the French translated document, do not provide the English version.
"""


def fix_encoding(text):
    """Fix encoding issues with accented characters."""
    # Try to detect and fix common encoding issues
    encodings_to_try = ['latin-1', 'windows-1252', 'iso-8859-1']

    for encoding in encodings_to_try:
        try:
            # Try to encode as bytes then decode with the proper encoding
            if isinstance(text, str):
                fixed_text = text.encode(
                    'utf-8').decode('utf-8', errors='ignore')
                # If there are still encoding issues, try more aggressive approach
                if '' in fixed_text:
                    fixed_text = text.encode(
                        'latin-1', errors='ignore').decode(encoding, errors='ignore')
                return fixed_text
        except (UnicodeEncodeError, UnicodeDecodeError):
            continue

    # If all attempts fail, return original text with errors ignored
    return text.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')


class EllisphereAgent:
    def __init__(self):
        """
        Initialize the unified EllisphereAgent with both XML parsing and compilation capabilities.
        """
        # XML Parser Agent
        self.xml_parser_agent = Agent(
            name="Ellisphere XML Parser",
            instructions=xml_parser_instructions,
            model="gpt-4o",
        )

        # Compiler Agent
        self.compiler_agent = Agent(
            name="Ellisphere Translator And Compiler Agent",
            instructions=compiler_instructions,
            model="gpt-4o",
            model_settings=ModelSettings(
                max_tokens=30000,
                truncation="disabled",
            )
        )

    async def parse_xml_to_json(self, xml_content):
        """
        Parse XML content and return structured JSON data.
        """
        result = await Runner.run(self.xml_parser_agent, xml_content)
        final_output = result.final_output

        # Fix encoding issues in the final_output string
        fixed_output = fix_encoding(final_output)

        return fixed_output

    async def parse_xml(self, xml_content):
        """
        Parse XML content and translate to French.
        """
        result = await Runner.run(self.xml_parser_agent, xml_content)
        final_output = result.final_output

        # Fix encoding issues in the final_output string
        fixed_output = fix_encoding(final_output)

        return fixed_output

    async def compile_data(self, data_from_multiple_sources):
        """
        Compile data from multiple sources and translate to French.
        """
        result = await Runner.run(self.compiler_agent, data_from_multiple_sources)
        final_output = result.final_output

        # Fix encoding issues in the final_output string
        fixed_output = fix_encoding(final_output)

        return fixed_output

    async def run(self, content, operation_type="xml_parse"):
        """
        Unified run method that can handle both operations.

        Args:
            content: The content to process (XML or compiled data)
            operation_type: "xml_parse", "xml_to_json", or "compile" (default: "xml_parse")
        """
        if operation_type == "xml_parse":
            return await self.parse_xml(content)
        elif operation_type == "xml_to_json":
            return await self.parse_xml_to_json(content)
        elif operation_type == "compile":
            return await self.compile_data(content)
        else:
            raise ValueError(
                "operation_type must be either 'xml_parse', 'xml_to_json', or 'compile'")


# Backward compatibility aliases
# EllisphereScraper = EllisphereAgent
# EllisphereCompilerAgent = EllisphereAgent
