from dotenv import load_dotenv
from agents import Agent, Runner

load_dotenv()


instructions = f"""
    When given an XML, try to parse, extract and organize the data in a structured format and translate to French. Mention on top of the document that the report is an organized data for Ellisphere.
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
                if '�' in fixed_text:
                    fixed_text = text.encode(
                        'latin-1', errors='ignore').decode(encoding, errors='ignore')
                return fixed_text
        except (UnicodeEncodeError, UnicodeDecodeError):
            continue

    # If all attempts fail, return original text with errors ignored
    return text.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')


class EllisphereAgent:
    def __init__(self, cancel_event=None):
        """
        Initialize the EllisphereAgent with OpenAI's Agent and instructions.
        """
        self.agent = Agent(
            name="Ellisphere's XML Parser",
            instructions=instructions,
            model="gpt-4o",
        )
        self.cancel_event = cancel_event

    async def run(self, xml_content):
        result = await Runner.run(self.agent, xml_content)
        final_output = result.final_output

        # Fix encoding issues in the final_output string
        fixed_output = fix_encoding(final_output)

        # Use the fixed output
        # with open("parsed_response_2023.txt", "w", encoding="utf-8") as f:
        #     f.write(fixed_output)

        # Return the fixed output for passing to other functions
        return fixed_output
