from dotenv import load_dotenv
from agents import Agent, Runner, ModelSettings

load_dotenv()


xml_parser_instructions = """
When given an XML, try to parse, extract and organize the data in a structured format and translate to French. Mention on top of the document that the report is an organized data for Ellisphere.
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
            operation_type: "xml_parse" or "compile" (default: "xml_parse")
        """
        if operation_type == "xml_parse":
            return await self.parse_xml(content)
        elif operation_type == "compile":
            return await self.compile_data(content)
        else:
            raise ValueError(
                "operation_type must be either 'xml_parse' or 'compile'")


# Backward compatibility aliases
# EllisphereScraper = EllisphereAgent
# EllisphereCompilerAgent = EllisphereAgent
