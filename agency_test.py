## Import Libraries
# import openai
import streamlit as st
from pdfminer.high_level import extract_text
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import cohere
from reportlab.lib.units import inch
from PIL import Image
import tempfile
from reportlab.platypus import SimpleDocTemplate, ListFlowable, ListItem


## SetUp Dependencies
### Extract Text
def extract_text_from_pdf(pdf_path):
    return extract_text(pdf_path)


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
    st.title("CV Labs")
    st.subheader("PDF Extractor")

    ## User Inputs
    st.sidebar.subheader("Please enter relevant Information")
    ### - Upload
    uploaded_file_resume = st.sidebar.file_uploader("Upload a PDF Resume", type=["pdf"], key=123)
    st.sidebar.divider()
    uploaded_file_job_desc = st.sidebar.file_uploader("Upload a PDF Job Description", type=["pdf"], key=234)

    if uploaded_file_resume and uploaded_file_job_desc:
        ## Enter OpenAI key
        st.sidebar.divider()
        col1, col2 = st.columns(2)
    
        resume_data = extract_text_from_pdf(uploaded_file_resume)
        col1.write("Extracted text from the PDF:")
        col1.text_area("Resume", resume_data, height=500)
    
        job_description_data = extract_text_from_pdf(uploaded_file_job_desc)
        col2.write("Extracted text from the PDF:")
        col2.text_area("Job Description", job_description_data, height=500)
        
        cohere_key = st.sidebar.text_input("Cohere API Key", type="password")
        co = cohere.Client(str(cohere_key))

        temperature_value = st.sidebar.slider("Temprature - (Deterministic to Random)",
                                              0.0, 0.9, 0.2, 0.1)
        
        setting_the_scene = f"""
                Refine resume provided for the job_description role. 
                Prioritize tech skills, maintain clarity & tone, and stay true to original content
                """

        if st.sidebar.button("Run"):
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
                              f"{self.setting_the_scene} Draft a single concise personal summary " \
                              f"drawing on organized experience, education, " \
                              f"and skills from the assigned resume."

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

        personal_details = st.text_area("Personal Details", st.session_state['display_personal_details'], height=250)
        personal_summary = st.text_area("Personal Summary", st.session_state['display_personal_summary'], height=250)
        candidate_experience = st.text_area("Experience", st.session_state['display_experience'], height=250)
        candidate_education = st.text_area("Education", st.session_state['display_education'], height=250)
        candidate_skills = st.text_area("Skills", st.session_state['display_skills'], height=250)

        # name_section = st.text_area("Name", personal_details['Name'], height=5)
        # contact_section = st.text_area("Contact Number", personal_details['Job Title'], height=5)
        # skills_section = st.text_area("Skills", "\n".join(skills), height=150)

        ## Assuming skills_section contains the user-submitted text
        user_input_text = candidate_skills
        skills_list = user_input_text.split("\n")
        cleaned_skills = [skill.strip() for skill in skills_list]
        # print(cleaned_skills)

        # Save button and functionality
        # if st.form_submit_button("Submit form"):
        # Add Header
        # Create PDF content using formatted text (consider libraries like FPDF for advanced formatting)
        pdf_content = canvas.Canvas("new_pdf.pdf", pagesize=letter)
        pdf_content.drawString(100, 750, "Welcome to CV Labs!")

        # Add Personal Details
        pdf_content.drawString(100, 720, "Personal Details:")
        pdf_content.drawString(150, 700, personal_details)

        # Add Contact section
        pdf_content.drawString(100, 670, "Personal Summary")
        pdf_content.drawString(150, 650, personal_summary)

        # Add Experience
        pdf_content.drawString(100, 620, "Experience:")
        pdf_content.drawString(150, 600, candidate_experience)

        # Add Education
        pdf_content.drawString(100, 570, "Education")
        pdf_content.drawString(150, 550, candidate_education)

        ## Add Skills section
        pdf_content.drawString(100, 520, "Skills:")
        # pdf_content.drawString(150, 600, candidate_skills)
        y_position = 500
        for skill in cleaned_skills:
            pdf_content.drawString(120, y_position, f". {skill}")
            y_position -= 20  # Adjust the vertical spacing

        pdf_content.save()
        with open("new_pdf.pdf", "rb") as file:
            st.download_button(
                label="Download PDF",
                data=file,
                file_name="test_pdf.pdf",
                mime="application/octest-stream"
            )

if __name__ == "__main__":
    main()
