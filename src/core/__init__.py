
from openai import OpenAI
from PyPDF2 import PdfReader

def createChatCompletion(text_input, system_prompt):
    """
    Generates a completion response from the OpenAI API based on user input.

    Args:
        text_input (str): The user-provided input text to be processed by the language model.

    Returns:
        str: The AI-generated response content based on the provided input.
    """
    client = OpenAI()
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text_input
             }])
    return completion.choices[0].message.content


def getTextFromPDF(file):
    """
    Extracts text content from each page of a PDF file.

    Args:
        file (str or file-like object): The PDF file to be read. Can be a file path or a file-like object.

    Returns:
        str: The combined text content of all pages in the PDF.
    """
    reader = PdfReader(file)
    pdf_text = ' '.join([page.extract_text() for page in reader.pages])
    return pdf_text
