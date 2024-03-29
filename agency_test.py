## Import Libraries
# import openai
import streamlit as st
from pdfminer.high_level import extract_text
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import cohere

co = cohere.Client('6YsSo6S1O4zl3cl4016LqdFQUoWm1pSNFX6Wv65z')


# from reportlab.platypus import SimpleDocTemplate, ListFlowable, ListItem

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

#
# setting_the_scene = ""
# iron_grip = ""
# resume_data = ""
# job_description_data = ""


### Prompts & Dependencies


def main():
    # global resume_data, job_description_data
    st.title("CV Labs")
    st.subheader("PDF Extractor")

    ## User Inputs
    st.sidebar.subheader("Please enter relevant Information")
    ### - Upload
    uploaded_file_resume = st.sidebar.file_uploader("Upload a PDF Resume", type=["pdf"], key=123)
    st.sidebar.divider()
    uploaded_file_job_desc = st.sidebar.file_uploader("Upload a PDF Job Description", type=["pdf"], key=234)

    ## Enter OpenAI key
    st.sidebar.divider()
    col1, col2 = st.columns(2)

    if uploaded_file_resume:
        # Read PDF text
        resume_data = extract_text_from_pdf(uploaded_file_resume)
        col1.write("Extracted text from the PDF:")
        col1.text_area("Resume", resume_data, height=500)

        ### - LLM Extract Categorization:
    if uploaded_file_job_desc:
        # Read PDF text
        job_description_data = extract_text_from_pdf(uploaded_file_job_desc)
        col2.write("Extracted text from the PDF:")
        col2.text_area("Job Description", job_description_data, height=500)

    # elif uploaded_file_job_desc is None:
    #     st.sidebar.subheader("Try Pasting the job description below:")
    #     st.sidebar.text_input('Job Description', '<sample job description>')

    if uploaded_file_resume and uploaded_file_job_desc:
        st.divider()
        setting_the_scene = f"""
                I need assistance refining the candidate's resume {resume_data}.
                The specific role to focus as described in {job_description_data}. 
                Please tailor the content to this position, ensuring clarity and coherence throughout. 
                Emphasise any tech-related experiences significantly, 
                adopting a professional tone with a hint of personality to keep it engaging. 
                Stick closely to the original content without introducing new information.
                """

        iron_grip = """
                Enforce strict output format. 

                - Remove all greetings, closing messages, and informative messages 
                  like "Informative Message," "Feedback Message," 
                  "Post-processing Note," or "User Prompt".
                - Return only the core extracted information from the resume.
                """

        #### => Class Object
        class Resume:
            def __init__(self, resume, job_description):
                self.extracted_resume_text = resume
                self.extracted_job_description_text = job_description
                self.setting_the_scene = setting_the_scene
                self.iron_grip = iron_grip

            def extract_pd(self):
                section = f"**Personal details (if found)**\n" \
                          f"{self.setting_the_scene} Look through {self.extracted_resume_text} " \
                          f"and identify the following sections:\n" \
                          f"**First Name**\n" \
                          f"- Look for keywords or phrases suggesting personal details for candidate's first name.\n" \
                          f"**Last Name**\n" \
                          f"- Look for keywords or phrases suggesting personal details for candidate's last name.\n" \
                          f"- Contact\n" \
                          f"**Contact (if found)**\n" \
                          f"- Look for any combination of keywords like City, Country, Phone Number, Email Address.\n" \
                          f"- Extract and format the information accordingly " \
                          f"(e.g., City, Country, Phone: +XX XXXXXXXXXX, Email: example@email.com).\n\n" \
                          f"{self.iron_grip}"

                response = co.chat(
                    message=section,
                    model="command",
                    temperature=0.9
                )

                personal_details = remove_helper_text(response.text)

                return personal_details

            def extract_ps(self):
                section = f"**Personal summary (if found)**\n" \
                          f"Look through {self.extracted_resume_text} " \
                          f"and identify the following (organised experience, education, and skills sections):\n" \
                          f"Based on the organised experience, education, and skills sections, " \
                          f"draft a personalised profile " \
                          f"summary for a candidate seeking the titled position in the {self.extracted_job_description_text} " \
                          f"as well as for its industry. {self.iron_grip}"

                response = co.chat(
                    message=section,
                    model="command",
                    temperature=0.9
                )

                personal_summary = remove_helper_text(response.text)

                return personal_summary

            def extract_exp(self):
                section = f"**Experience (if found)**\n" \
                          f"{self.setting_the_scene} Look through {self.extracted_resume_text} " \
                          f"and review the organized experience section. Identify and prioritize " \
                          f"experience or experiences (or any similar section mentioning " \
                          f"job titles and responsibilities)\n" \
                          f"that are most relevant to advertised role in the {self.extracted_job_description_text} " \
                          f"with cognizance to the tech industry, placing them at the top of the list {self.iron_grip}"

                response = co.chat(
                    message=section,
                    model="command",
                    temperature=0.9
                )

                experience = remove_helper_text(response.text)

                return experience

            def extract_ed(self):
                section = f"**Education (if found)**\n" \
                          f"{self.setting_the_scene} Look through {self.extracted_resume_text} " \
                          f"and identify the following:\n" \
                          f"- Education\n" \
                          f"- Look for keywords suggesting education (e.g., Education, University, Degree).\n" \
                          f"- Extract details like University Name, Degree, Major (if applicable), " \
                          f"Location (City, Country), and Dates of Attendance.\n\n" \
                          f"- list the educational qualifications including degree, institution and graduation year. " \
                          f" Place the most recent qualification at the top." \
                          f"{self.iron_grip}"

                response = co.chat(
                    message=section,
                    model="command",
                    temperature=0.9
                )

                education = remove_helper_text(response.text)

                return education

            def extract_skills(self):
                section = f"**Skills (if found)**\n" \
                          f"{self.setting_the_scene} Consider the job experiences " \
                          f"and education previously in {self.extracted_resume_text}. " \
                          f"- Look for keywords or phrases suggesting skills " \
                          f"(e.g., Skills, Expertise, Proficient in).\n" \
                          f"Compile a list of skills that are " \
                          f"evident from these experiences and qualifications, " \
                          f"focusing on those most relevant to a Job Role in {self.extracted_job_description_text} " \
                          f"in its industry {self.iron_grip}"

                response = co.chat(
                    message=section,
                    model="command",
                    temperature=0.9
                )

                skill = remove_helper_text(response.text)

                return skill

        ### - Enhancement & Combination
        st.divider()
        st.write("Best Fitting")
        ## Call Class
        r1 = Resume(resume_data, job_description_data)

        ### - Export
        st.divider()
        # Display extracted text with editable areas
        st.header("Creating Form:")
        extracted_text_sections = st.form(key="extracted_text_form")

        display_personal_details = r1.extract_pd()
        personal_details = extracted_text_sections.text_area("Personal Details",
                                                             display_personal_details,
                                                             height=250)
        st.divider()

        display_personal_summary = r1.extract_ps()
        personal_summary = extracted_text_sections.text_area("Personal Summary",
                                                             display_personal_summary,
                                                             height=250)
        st.divider()

        display_experience = r1.extract_exp()
        candidate_experience = extracted_text_sections.text_area("Experience",
                                                                 display_experience,
                                                                 height=250)
        st.divider()

        display_education = r1.extract_ed()
        candidate_education = extracted_text_sections.text_area("Education",
                                                                display_education,
                                                                height=250)
        st.divider()

        display_skills = r1.extract_skills()
        candidate_skills = extracted_text_sections.text_area("Skills",
                                                             display_skills,
                                                             height=250)

        # name_section = extracted_text_sections.text_area("Name", personal_details['Name'], height=5)
        # contact_section = extracted_text_sections.text_area("Contact Number", personal_details['Job Title'], height=5)
        # skills_section = extracted_text_sections.text_area("Skills", "\n".join(skills), height=150)

        ## Assuming skills_section contains the user-submitted text
        user_input_text = candidate_skills
        skills_list = user_input_text.split("\n")
        cleaned_skills = [skill.strip() for skill in skills_list]
        # print(cleaned_skills)

        # Save button and functionality
        if extracted_text_sections.form_submit_button("Submit form"):
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


## Wire Framing
### SideBar - Uploader(2) /Summary /

### Categorization & Display Enhancement (as in form)

### Combination for best fit

if __name__ == "__main__":
    main()
