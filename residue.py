import streamlit as st
import textwrap
import base64
import requests
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Image
from bs4 import BeautifulSoup


def justify_text(text, max_chars_per_line=120):
    """
    Justifies text to fit within the defined max_chars_per_line limit.
    Args:
        text: The string to be justified.
        max_chars_per_line: Maximum characters per line (default is 70).

    Returns:
        A list of strings representing the justified text lines.
    """

    wrapped_lines = textwrap.fill(text, width=max_chars_per_line)
    justified_lines = [line.ljust(max_chars_per_line) for line in wrapped_lines.splitlines()]
    return justified_lines


def format_candidate_details(details):
    formatted_lines = []
    # Split the details by lines
    lines = details.strip().split('\n')
    for line in lines:
        # Check if the line contains contact information
        if line.strip().startswith('-'):
            # Indent the contact information
            formatted_lines.append('   ' + line.strip())
        else:
            formatted_lines.append(line.strip())
    return formatted_lines


def format_experience(experience_text):
    """
    Formats experience text into a list of lines with consistent styling.

    Args:
        experience_text (str): The experience text to be formatted.

    Returns:
        list: A list of formatted experience lines.
    """
    formatted_lines = []
    # Split the experience text by line breaks
    lines = experience_text.strip().split('\n')
    # Iterate through each line
    for line in lines:
        # Check if the line contains the job title
        if line.strip().startswith('Title:'):
            # Add the job title as a bold line
            formatted_lines.append(f"**{line.strip()}**")
        # Check if the line contains the organization name
        elif line.strip().startswith('Organization:'):
            # Add the organization name with bold formatting
            formatted_lines.append(f"  *{line.strip()}*")
        else:
            # Add achievements with indentation
            formatted_lines.append('  - ' + line.strip())
    return formatted_lines


def pdf_add_logo(pdf_content, logo_path, default_width=120, default_height=60):
    ## Fetch Pdf Content
    c = pdf_content
    logo = Image(logo_path, width=default_width, height=default_height)
    ## Fix Weight and Height
    page_width, page_height = letter
    ## Define x and y length
    x = 0.5 * (page_width - logo.drawWidth)
    y = page_height - logo.drawWidth + 50

    ## Fix Logo
    logo.drawOn(c, x, y)

    ## Update pdf_content


#     c.save()


def remove_helper_text(text):
    """Removes first and last paragraphs (helper text) from the text.
  Args:
      text: The text to process.
  Returns:
      The text with first and last paragraphs removed.
  """

    paragraphs = text.split("\n\n")  # Split by two newlines (common for helper text)
    if len(paragraphs) > 2:  # Check if at least 3 paragraphs
        # Remove first and last paragraphs (helper text)
        return "\n\n".join(paragraphs[1:-1])
    else:
        return text  # Return original text if less than 3 paragraphs


def display_pdf(file):
    # Opening file from file path
    st.markdown("### PDF Preview")

    with open(file, "rb") as file:
        base64_pdf = base64.b64encode(file.read()).decode("utf-8")

    pdf_display = f"""<embed
    class="pdfobject"
    type="application/pdf"
    title="Embedded PDF"
    src="data:application/pdf;base64,{base64_pdf}" 
    width="400" 
    height="100%"
    style="height:50vh; width:100%">"""

    # Displaying File
    st.markdown(pdf_display, unsafe_allow_html=True)


def read_webpage(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        divs = soup.find_all('div')
        div_values = [div.text for div in divs]

        return div_values
    except requests.exceptions.RequestException as e:
        st.error(f"Error reading webpage: {e}")
        return None
