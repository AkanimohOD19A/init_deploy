## Import Libraries
# import openai
import base64
import cohere
import streamlit as st
from pdfminer.high_level import extract_text
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Image
from reportlab.lib.units import inch


## SetUp Dependencies
### Extract Text
def extract_text_from_pdf(pdf_path):
    return extract_text(pdf_path)


## Handling PDF Output: Type yourself
# Define maximum characters per line
max_chars_per_line = 90  # Adjust this value as needed


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
    base64_pdf = base64.b64encode(file.read()).decode("utf-8")

    # Embedding PDF in HTML
    pdf_display = f"""<iframe src="data:application/pdf;base64,{base64_pdf}" width="400" height="100%" type="application/pdf"
                        style="height:50vh; width:100%"
                    >
                    </iframe>"""

    # Displaying File
    st.markdown(pdf_display, unsafe_allow_html=True)


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
    st.subheader("PDF Extractor")

    ## User Inputs
    st.sidebar.subheader("Please enter relevant Information")
    ### - Upload
    uploaded_file_resume = st.sidebar.file_uploader("Upload a PDF Resume", type=["pdf"], key=123)
    st.sidebar.divider()
    uploaded_file_job_desc = st.sidebar.file_uploader("Upload a PDF Job Description", type=["pdf"], key=234)

    if uploaded_file_resume and uploaded_file_job_desc:
        # with st.sidebar:
        #     disp_resume = st.toggle("Display Resume (Before running)")
        #     if disp_resume:
        #         display_pdf(uploaded_file_resume)

        ## Enter OpenAI key
        st.sidebar.divider()
        col1, col2 = st.columns(2)

        resume_data = extract_text_from_pdf(uploaded_file_resume)
        if col1.toggle("Show Extracted Text:"):
            col1.text_area("Resume", resume_data, height=500)

        job_description_data = extract_text_from_pdf(uploaded_file_job_desc)
        if col2.toggle("Show Extracted Resume:"):
            col2.text_area("Job Description", job_description_data, height=500)

        st.sidebar.header(f"Set your Cohere API Key")
        st.sidebar.link_button("get one @ Cohere 🔗", "https://dashboard.cohere.com/api-keys")
        cohere_key = st.sidebar.text_input("Cohere API Key", type="password", label_visibility="collapsed")

        if cohere_key and len(cohere_key) >= 30:
            co = cohere.Client(str(cohere_key))

            temperature_value = st.sidebar.slider("Temprature - (Deterministic to Random)",
                                                  0.0, 0.9, 0.2, 0.1)
            setting_the_scene = f"""
                            Refine resume provided for the job_description role. 
                            Prioritize tech skills, maintain clarity & tone, and stay true to original content
                            """

            run_button = st.sidebar.button("Run")
            if run_button:
                disp_resume = None
                st.sidebar.success("Running ...")
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

                        def extract_pd(self):
                            section = f"**Personal details (if found)**\n" \
                                      f"Search for First Name, Last Name, and Contact " \
                                      f"info (City, Country, " \
                                      f"Phone, Email) from the assigned resume. "

                            response_setting = co.chat(
                                message=section,
                                model="command",
                                temperature=temperature_value,
                                prompt_truncation='AUTO',
                                documents=[{"content": self.extracted_resume_text}]
                            )

                            p_details = remove_helper_text(response_setting.text)

                            return p_details

                        def extract_ps(self):
                            section = f"**Personal summary (if found)**\n" \
                                      f"{self.setting_the_scene} and draft a single concise personal summary " \
                                      f"from the assigned resume."

                            response_setting = co.chat(
                                message=section,
                                model="command",
                                temperature=temperature_value,
                                prompt_truncation='AUTO',
                                documents=[{"content": self.extracted_resume_text}]
                            )

                            p_summary = remove_helper_text(response_setting.text)

                            return p_summary

                        def extract_exp(self):
                            section = f"**Experience (if found)**\n" \
                                      f"{self.setting_the_scene} Analyze the assigned resume to identify relevant " \
                                      f"experiences (titles & duties) " \
                                      f"for the assigned job description (tech focus). Prioritize & list them."

                            response_setting = co.chat(
                                message=section,
                                model="command",
                                temperature=temperature_value,
                                prompt_truncation='AUTO',
                                documents=[
                                    {"content": self.extracted_job_description_text},
                                    {"content": self.extracted_resume_text}
                                ]
                            )

                            experience = remove_helper_text(response_setting.text)

                            return experience

                        def extract_ed(self):
                            section = f"**Education (if found)**\n" \
                                      f"Search for education details (University, Degree, Major, Location, Dates)" \
                                      f" from the assigned resume. List chronologically (newest first)."

                            response_setting = co.chat(
                                message=section,
                                model="command",
                                temperature=temperature_value,
                                prompt_truncation='AUTO',
                                documents=[{"content": self.extracted_resume_text}]
                            )

                            education = remove_helper_text(response_setting.text)

                            return education

                        def extract_skills(self):
                            section = f"**Skills (if found)**\n" \
                                      f"{self.setting_the_scene} Analyze the assigned resume & the assigned job description " \
                                      f"to identify relevant skills (tech focus). Prioritize & list them."

                            response_setting = co.chat(
                                message=section,
                                model="command",
                                temperature=temperature_value,
                                prompt_truncation='AUTO',
                                documents=[
                                    {"content": self.extracted_job_description_text},
                                    {"content": self.extracted_resume_text}
                                ]
                            )

                            skill = remove_helper_text(response_setting.text)

                            return skill

                    ### - Enhancement & Combination
                    ## Call Class
                    r1 = Resume(resume_data, job_description_data)

                    st.session_state['display_personal_details'] = r1.extract_pd()  # Update session state
                    st.session_state['display_personal_summary'] = r1.extract_ps()
                    st.session_state['display_experience'] = r1.extract_exp()
                    st.session_state['display_education'] = r1.extract_ed()
                    st.session_state['display_skills'] = r1.extract_skills()

                    ### - Export
                    st.divider()
                    # Display extracted text with editable areas
                    st.header("Best fitted data:")

                    personal_details = st.text_area("Personal Details", st.session_state['display_personal_details'],
                                                    height=250)
                    personal_summary = st.text_area("Personal Summary", st.session_state['display_personal_summary'],
                                                    height=250)
                    candidate_experience = st.text_area("Experience", st.session_state['display_experience'],
                                                        height=250)
                    candidate_education = st.text_area("Education", st.session_state['display_education'], height=250)
                    candidate_skills = st.text_area("Skills", st.session_state['display_skills'], height=250)

                    # name_section = st.text_area("Name", personal_details['Name'], height=5)
                    # contact_section = st.text_area("Contact Number", personal_details['Job Title'], height=5)
                    # skills_section = st.text_area("Skills", "\n".join(skills), height=150)

                    ## Assuming skills_section contains the user-submitted text
                    user_input_text = candidate_skills
                    skills_list = user_input_text.split("\n")
                    # cleaned_skills = [skill.strip() for skill in skills_list]
                    # print(cleaned_skills)

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
                    # pdf_content.save()
                    pdf_add_logo(pdf_content, logo_path='assets/logo.png')

                    # Read and display the PDF file
                    modified_file = open("new_pdf.pdf", "rb")
                    display_pdf(modified_file)

                    # Close the file
                    modified_file.close()

                    # display_pdf("new_pdf.pdf")
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
        else:
            st.sidebar.error("Please enter a valid credential")
            st.stop()


if __name__ == "__main__":
    main()
