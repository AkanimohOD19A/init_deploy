## Import Libraries
# import openai
import io
import os
import base64
import cohere
import tempfile
import logging
import numpy as np
from PIL import Image as pimg
import streamlit as st
from dotenv import load_dotenv
from reportlab.pdfgen import canvas
from reportlab.platypus import Image
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from pdfminer.high_level import extract_text

# Load .env file
load_dotenv()

# Access the variables
cohere_key = os.getenv('COHERE_KEY')

#  Set Logging to WARNING
st_logger = logging.getLogger('streamlit')
st_logger.setLevel(logging.WARNING)

## SetUp Dependencies
### Extract Text
## Function to extract text from PDF with caching
# @st.cache(allow_output_mutation=True)
@st.cache_data
def extract_text_from_pdf(pdf_path):
    return extract_text(pdf_path)


## Handling PDF Output: Type yourself
# Define maximum characters per line
max_chars_per_line = 90  # Adjust this value as needed


@st.cache_data
def wrap_text(text):
    """
    Wraps text to fit within the defined max_chars_per_line limit.
    Args:
        text: The string to be wrapped.

    Returns:
        A list of strings representing the wrapped text lines.
    """

    personal_details_lines = []
    current_line = ""

    for word in text.split():
        if len(current_line + word) <= max_chars_per_line:
            current_line += " " + word
        else:
            personal_details_lines.append(current_line.strip())
            current_line = word
    personal_details_lines.append(current_line.strip())
    return personal_details_lines


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
    c.save()


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

    # Embedding PDF in HTML
    pdf_display = f"""<iframe src="data:application/pdf;base64,{base64_pdf}" width="400" height="100%"
    type="application/pdf" style="height:50vh; width:100%" > </iframe>"""

    # pdf_display = f"""<embed
    # class="pdfobject"
    # type="application/pdf"
    # title="Embedded PDF"
    # src="data:application/pdf;base64,{base64_pdf}"
    # style="overflow: auto; width: 100%; height: 100%;">"""

    # pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" \
    # width="700" \
    # height="100%" \
    # type="application/pdf" style="overflow: auto; height:50vh; width:100%" ></iframe>'

    # Displaying File
    st.markdown(pdf_display, unsafe_allow_html=True)


## Temperature Settings
temp_settings = {
    "Super Formal": np.random.uniform(0.0, 0.2),
    "Formal": np.random.uniform(0.2, 0.5),
    "Business Casual": np.random.uniform(0.5, 0.9)
}


def main():
    ## Initiate Sessions
    if 'display_personal_details' not in st.session_state:
        st.session_state['display_personal_details'] = ""

    if 'display_personal_summary' not in st.session_state:
        st.session_state['display_personal_summary'] = ""

    if 'display_experience' not in st.session_state:
        st.session_state['display_experience'] = ""

    if 'display_education' not in st.session_state:
        st.session_state['display_education'] = ""

    if 'display_skills' not in st.session_state:
        st.session_state['display_skills'] = ""

    # global resume_data, job_description_data

    st.title("CV LAB")
    st.subheader("Proof of Concept")
    st.divider()

    st.write("Some Description in Long form")

    # st.subheader("PDF Extractor")

    ## User Inputs

    st.sidebar.subheader("Please enter relevant Information")
    ### - Upload

    uploaded_cv_logo = st.sidebar.file_uploader("Upload a logo - cvlabs will be used by default",
                                                type=["jpg", "png", "jpeg"], key=111)
    st.sidebar.divider()
    uploaded_file_resume = st.sidebar.file_uploader("Upload a PDF Resume", type=["pdf"], key=123)
    st.sidebar.divider()
    uploaded_file_job_desc = st.sidebar.file_uploader("Upload a PDF Job Description", type=["pdf"], key=234)

    if uploaded_file_resume and uploaded_file_job_desc:
        st.sidebar.divider()
        # col1, col2 = st.columns(2)

        resume_data = extract_text_from_pdf(uploaded_file_resume)
        print("Extracted Resume", "\n\n")
        print(resume_data)
        job_description_data = extract_text_from_pdf(uploaded_file_job_desc)

        print("Extracted Job Description", "\n\n")
        print(job_description_data, "\n\n")

        setting_the_scene = f"""
                            Refine resume provided for the job_description role. 
                            Prioritize tech skills, maintain clarity & tone, and stay true to original content
                            """

        temp_value = st.sidebar.selectbox(f"Select Temperature", list(temp_settings.keys()))
        temperature_value = temp_settings[temp_value]

        ## Call Cohere Key from environment
        co = cohere.Client(str(cohere_key))

        ## Placeholder for Dynamic button
        button_placeholder = st.sidebar.empty()

        ## Dynamic Run Button I
        run_button = button_placeholder.button("Run")

        # Create a placeholder for the status text
        status_placeholder = st.sidebar.empty()

        if run_button:
            ## Dynamic Run Button II
            button_placeholder.empty()
            status_placeholder.warning("Running ...")

            print(f"Running: {temp_value} - mapping to: {temperature_value}", "\n\n")
            try:
                #### => Class Object
                class Resume:
                    def __init__(self, resume, job_description):
                        self.extracted_resume_text = resume
                        self.extracted_job_description_text = job_description
                        self.setting_the_scene = setting_the_scene
                        # self.iron_grip = iron_grip
                        # self.personal_details_retrieval = [{"content": resume_text}]
                        # self.skill_extraction_retrieval = [
                        #     {"content": job_description_text},
                        #     {"content": resume_text}
                        # ]

                    @st.cache_resource
                    def extract_pd(_self):
                        section = f"**Personal details (if found)**\n" \
                                  f"Search for First Name, Last Name, and Contact " \
                                  f"info (City, Country, " \
                                  f"Phone, Email) from the assigned resume. "

                        response_setting = co.chat(
                            message=section,
                            model="command",
                            temperature=temperature_value,
                            prompt_truncation='AUTO',
                            documents=[{"content": _self.extracted_resume_text}]
                        )

                        p_details = remove_helper_text(response_setting.text)

                        return p_details

                    @st.cache_resource
                    def extract_ps(_self):
                        section = f"**Personal summary (if found)**\n" \
                                  f"{_self.setting_the_scene} and draft a single concise personal summary " \
                                  f"from the assigned resume."

                        response_setting = co.chat(
                            message=section,
                            model="command",
                            temperature=temperature_value,
                            prompt_truncation='AUTO',
                            documents=[{"content": _self.extracted_resume_text}]
                        )

                        p_summary = remove_helper_text(response_setting.text)

                        return p_summary

                    @st.cache_resource
                    def extract_exp(_self):
                        section = f"**Experience (if found)**\n" \
                                  f"{_self.setting_the_scene} Analyze the assigned resume to identify relevant " \
                                  f"experiences (titles & duties) " \
                                  f"for the assigned job description (tech focus). Prioritize & list them."

                        response_setting = co.chat(
                            message=section,
                            model="command",
                            temperature=temperature_value,
                            prompt_truncation='AUTO',
                            documents=[
                                {"content": _self.extracted_job_description_text},
                                {"content": _self.extracted_resume_text}
                            ]
                        )

                        experience = remove_helper_text(response_setting.text)

                        return experience

                    @st.cache_resource
                    def extract_ed(_self):
                        section = f"**Education (if found)**\n" \
                                  f"Search for education details (University, Degree, Major, Location, Dates)" \
                                  f" from the assigned resume. List chronologically (newest first)."

                        response_setting = co.chat(
                            message=section,
                            model="command",
                            temperature=temperature_value,
                            prompt_truncation='AUTO',
                            documents=[{"content": _self.extracted_resume_text}]
                        )

                        education = remove_helper_text(response_setting.text)

                        return education

                    @st.cache_resource
                    def extract_skills(_self):
                        section = f"**Skills (if found)**\n" \
                                  f"{_self.setting_the_scene} Analyze the assigned resume & the assigned job description " \
                                  f"to identify relevant skills (tech focus). Prioritize & list them."

                        response_setting = co.chat(
                            message=section,
                            model="command",
                            temperature=temperature_value,
                            prompt_truncation='AUTO',
                            documents=[
                                {"content": _self.extracted_job_description_text},
                                {"content": _self.extracted_resume_text}
                            ]
                        )

                        skill = remove_helper_text(response_setting.text)

                        return skill

                st.snow()

                ### - Enhancement & Combination
                ## Call Class

                r1 = Resume(resume_data, job_description_data)
                st.snow()
                st.session_state['display_personal_details'] = r1.extract_pd()  # Update session state
                st.snow()
                st.session_state['display_personal_summary'] = r1.extract_ps()
                st.snow()
                st.session_state['display_experience'] = r1.extract_exp()
                st.snow()
                st.session_state['display_education'] = r1.extract_ed()
                st.snow()
                st.session_state['display_skills'] = r1.extract_skills()
                st.snow()

                ## Dynamic Run Button III
                status_placeholder.success("Completed - Rendering Document...")

                ### - Export
                st.divider()

                # Display extracted text with editable areas
                st.header("Best fitted data:")

                personal_details = st.text_area("Personal Details",
                                                st.session_state['display_personal_details'],
                                                height=250)

                personal_summary = st.text_area("Personal Summary",
                                                st.session_state['display_personal_summary'],
                                                height=250)

                candidate_experience = st.text_area("Experience",
                                                    st.session_state['display_experience'],
                                                    height=250)

                candidate_education = st.text_area("Education",
                                                   st.session_state['display_education'],
                                                   height=250)

                candidate_skills = st.text_area("Skills",
                                                st.session_state['display_skills'],
                                                height=250)

                ## Assuming skills_section contains the user-submitted text
                user_input_text = candidate_skills
                # skills_list = user_input_text.split("\n")

                # Define margins and spacing values (in inches)
                margin_left = 0.5
                margin_top = -9.5
                line_spacing = 0.2

                # Create PDF content
                pdf_content = canvas.Canvas("new_pdf.pdf", pagesize=letter)
                # Starting y position (adjust based on page size and margins)
                # y_position = margin_top * inch
                # Define fixed page height (adjust as needed)

                page_height = 11.7  # Inches (standard letter size)
                # Starting y position (calculate based on top margin and first element height)
                first_line_height = pdf_content.stringWidth("Welcome to CV Lab!") * 0.1  # Assuming 0.1 is font size
                y_position = page_height - margin_top * inch - first_line_height

                # Text elements with wrapping
                sections = [
                    # ("Welcome to CV Lab!", ""),
                    ("Personal Details:", personal_details),
                    ("Personal Summary", personal_summary),
                    ("Experience:", candidate_experience),
                    ("Education", candidate_education),
                    ("Skills:", candidate_skills),  # Assuming no wrapping needed for skills header
                ]

                for title, text in sections:
                    pdf_content.drawString(margin_left * inch, y_position, title)
                    y_position -= line_spacing * inch  # Update y position
                    # Wrap and add text content (if any)
                    if text:
                        wrapped_lines = wrap_text(text)
                        for line in wrapped_lines:
                            pdf_content.drawString(margin_left * inch + 0.25 * inch, y_position, line)
                            y_position -= line_spacing * inch
                # pdf_content.save()

                if uploaded_cv_logo:
                    # Open Image File
                    uploaded_logo = pimg.open(uploaded_cv_logo)

                    ## Temporary Directory
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                        temp_path = temp_file.name
                        uploaded_logo.save(temp_path)

                    # Close the image explicitly
                    uploaded_logo.close()

                    # Pdf operation
                    pdf_add_logo(pdf_content, logo_path=temp_path)

                    # Remove the temporary file
                    os.unlink(temp_path)
                else:
                    pdf_add_logo(pdf_content, logo_path='assets/logo.png')

                # Read and display the PDF file
                modified_file = open("new_pdf.pdf", "rb")
                # Close the file
                modified_file.close()
                display_pdf("new_pdf.pdf")

                with open("new_pdf.pdf", "rb") as file:
                    st.download_button(
                        label="Download PDF",
                        data=file,
                        file_name="test_pdf.pdf",
                        mime="application/octest-stream"
                    )

            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.stop()


if __name__ == "__main__":
    main()
