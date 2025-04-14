web_result_instruction = """
1. Based on the compiled results given by multiple agents, create a clean, human-readable document in paragraph format and bullet points for lists if needed.

2. Analyze the texts and try to group up the information by sections, and fill up the sections with the relevant information, written in paragraphs, in French.

3. For the financial part, make it a bit detailed as possible.

4. Example for the final result:

TITRE

(paragraph related to the title)

TITRE 2

(paragraph related to the title 2)

...

CONCLUSION
(a paragraph to conclude the document)

"""

ellisphere_result_instruction = """
1. Given the data from from multiple sources, create a clean, human-readable document in paragraph/bullet point format if needed for the financial data by year.

2. Translate the document into French.

Important:
- Just give the French translated document, do not provide the English version.
"""
