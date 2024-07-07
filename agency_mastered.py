## Import Libraries
# import openai
import os
import cohere
import tempfile
import logging
import numpy as np
from PIL import Image as pIMG
import streamlit as st
# from dotenv import load_dotenv
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from pdfminer.high_level import extract_text
from residue import *

# streamlit secrets
cohere_key = st.secrets["COHERE_KEY"]

#  Set Logging to WARNING
st_logger = logging.getLogger('streamlit')
st_logger.setLevel(logging.WARNING)


## SetUp Dependencies
### Extract Text
@st.cache_data
def extract_text_from_pdf(pdf_path):
    return extract_text(pdf_path)


## PROMPT  FORMAT
### Temperature Settings
temp_settings = {
    "Super Formal": np.random.uniform(0.0, 0.2),
    "Formal": np.random.uniform(0.2, 0.5),
    "Business Casual": np.random.uniform(0.5, 0.9)
}

### Prompt Formatting
setting_the_scene = """
Refine the resume provided for the job_description role. 
Prioritize tech skills, maintain clarity & tone, and stay true to original content.

Importantly, remove any unnecessary output and go straight to the point.
"""

format_personal_details = '''
Name: First Last
Contact Information:
 - City: <City>
 - Country: <Country>
 - Phone: <Phone Number>
 - Email: <Email>
'''

format_skills_list = '''
1. <skill_1>
n. <skill_n>
'''

format_candidate_experience = '''
1. <Job Title> | <Organization> | <Period>
- <Achievement 1>
- <Achievement n>

n. <Job Title> | <Organization> | <Period>
- <Achievement 1>
- <Achievement n>
'''

format_education = '''
<Course Title>(<School>,<Year>)
'''

## PDF Format
# Define margins and spacing values (in inches)
margin_left = 0.5
margin_top = -9.5
line_spacing = 0.2

# Create PDF content
pdf_content = canvas.Canvas("JUNK/cv_labs_pdf.pdf", pagesize=letter)
page_height = 11.7  # Inches (standard letter size)

# Define maximum characters per line
max_chars_per_line = 90  # Adjust this value as needed

# Set font for bold subjects
bold_font_size = 12
regular_font_size = 10

# Bottom margin
bottom_margin = 0.5 * inch

################
## Build Page ##
################

job_desc = ""

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
# uploaded_file_job_desc = st.sidebar.file_uploader("Upload a PDF Job Description", type=["pdf"], key=234)

# Add a radio button to choose between upload and link paste
input_option = st.sidebar.radio("Choose input option", ("Upload PDF", "Paste Link"))

if input_option == "Upload PDF":
    uploaded_file = st.sidebar.file_uploader("Upload a PDF Job Description", type=["pdf"])
    if uploaded_file:
        job_desc = extract_text_from_pdf(uploaded_file)
        # Process the job description content here
        # st.sidebar.write("Uploaded file content:", job_desc)
else:
    link = st.sidebar.text_input("Enter the job description URL")
    if link:
        job_desc = read_webpage(link)
        # Process the job description content here
        # st.sidebar.write("Job description from link:", job_desc)

if uploaded_file_resume and job_desc:
    st.sidebar.divider()
    # col1, col2 = st.columns(2)

    resume_data = extract_text_from_pdf(uploaded_file_resume)
    print("Extracted Resume", "\n\n")
    print(resume_data)
    # job_description_data = extract_text_from_pdf(uploaded_file_job_desc)
    job_description_data = job_desc

    print("Extracted Job Description", "\n\n")
    print(job_description_data, "\n\n")

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

                @st.cache_resource
                def extract_pd(_self):
                    section = f"**Personal details (if found)**\n" \
                              f"Search for First Name, Last Name, and Contact " \
                              f"info (City, Country, " \
                              f"Phone, Email) from the assigned resume " \
                              f"without adding any noise and return in this exact format: {format_personal_details}"

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
                              f"{_self.setting_the_scene} and generate a single concise paragraph of" \
                              f"about 70 - 100 words personal summary " \
                              f"in first person POV."

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
                              f"experiences (titles & duties) for the assigned job description." \
                              f"Prioritize & list them according to recency" \
                              f"and return in this exact format: {format_candidate_experience}"

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
                              f"{_self.setting_the_scene} Analyze the assigned resume to identify " \
                              f"education details (University, Degree, Major, Location, Dates)" \
                              f"Remove and wrappers like '```'," \
                              f"Prioritize & list them according to recency in this exact format: {format_education}"

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
                              f"{_self.setting_the_scene} search and identify the relevant skills (tech focus) " \
                              f"to the job description, " \
                              f"from the assigned resume " \
                              f"Prioritize & list them and return in this exact format: {format_skills_list}"

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
            # st.header("Best fitted data:")
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.stop()


def main():
    # Display form data
    st.write("Output Form Data:")

    # Retrieve and Format Ouput
    personal_details = st.text_area("Personal_Details",
                                    st.session_state['display_personal_details'],
                                    height=150)
    formatted_personal_details = format_candidate_details(personal_details)

    personal_summary = st.text_area("Personal_Summary",
                                    st.session_state['display_personal_summary'],
                                    height=250)

    candidate_experience = st.text_area("Experience",
                                        st.session_state['display_experience'],
                                        height=250)
    # Format the experience text using the new function
    candidate_experience = format_experience(candidate_experience)

    candidate_education = st.text_area("Education",
                                       st.session_state['display_education'],
                                       height=250)

    candidate_skills = st.text_area("Skills",
                                    st.session_state['display_skills'],
                                    height=250)

    # # Create a dictionary to store form data
    form_data = {"Personal_Details": formatted_personal_details,
                 "Personal_Summary": personal_summary,
                 "Experience": candidate_experience,
                 "Education": candidate_education,
                 "Skills": candidate_skills
                 }

    if st.button("Submit"):
        # Starting y position (calculate based on top margin and first element height)
        first_line_height = pdf_content.stringWidth("Welcome to CV Lab!") * 0.1  # Assuming 0.1 is font size
        y_position = page_height - margin_top * inch - first_line_height

        # Text elements with wrapping
        sections = [
            ("Personal Details", form_data["Personal_Details"]),
            ("Personal Summary", form_data["Personal_Summary"]),
            ("Experience", form_data["Experience"]),
            ("Education", form_data["Education"])
            # ("Skills:", candidate_skills),  # Assuming no wrapping needed for skills header
        ]

        ## Append Logo
        if uploaded_cv_logo:
            # Open Image File
            uploaded_logo = pIMG.open(uploaded_cv_logo)

            ## Temporary Directory
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                temp_path = temp_file.name
                uploaded_logo.save(temp_path)

            # Close the image explicitly
            uploaded_logo.close()

            ## Fix Logo
            pdf_add_logo(pdf_content, logo_path=temp_path)

            # Remove the temporary file
            os.unlink(temp_path)
        else:
            pdf_add_logo(pdf_content, logo_path='assets/logo.png')

        for title, text in sections:
            # Set bold font for the title
            pdf_content.setFont("Helvetica-Bold", bold_font_size)
            pdf_content.drawString(margin_left * inch, y_position, title)
            y_position -= line_spacing * inch  # Update y position

            # Set regular font for the body text
            pdf_content.setFont("Helvetica", regular_font_size)
            # Check if it's the personal details section
            if title == "Personal Details":
                for line in formatted_personal_details:
                    pdf_content.drawString(margin_left * inch, y_position, line)
                    y_position -= line_spacing * inch
            elif title == "Experience":
                # Add each formatted line to the PDF content with proper indentation
                for line in candidate_experience:
                    # Check if the line starts with 'Title:' (Job Title)
                    if line.startswith('Title:'):
                        pdf_content.drawString(margin_left * inch, y_position, line)  # Add Job Title
                    # Handle achievements (assuming they don't start with any special prefix)
                    else:
                        #  Check if the line is an achievement
                        achievement_text = line[3:]
                        wrapped_achievement_lines = justify_text(achievement_text)
                        # Add each wrapped line to the PDF content with proper indentation
                        for wrapped_line in wrapped_achievement_lines:
                            y_position -= line_spacing * inch
                            pdf_content.drawString(margin_left * inch + 3, y_position,
                                                   wrapped_line)  # Adjust indentation for bullet point
                # Add an empty line after each section
                y_position -= line_spacing * inch

            else:
                # Wrap and add text content (if any)
                if text:
                    wrapped_lines = justify_text(text)
                    for line in wrapped_lines:
                        pdf_content.drawString(margin_left * inch, y_position, line)
                        y_position -= line_spacing * inch

            # Add an empty line after each section
            y_position -= line_spacing * inch

        ## Skills
        # Define the starting y position and left margin for the second column
        column_spacing = 3 * inch  # Adjust the spacing between columns as needed
        right_column_start = margin_left + column_spacing

        # Handle the "Skills" section separately
        pdf_content.setFont("Helvetica-Bold", bold_font_size)
        pdf_content.drawString(margin_left * inch, y_position, "Skills:")
        y_position -= line_spacing * inch  # Update y position

        # Set regular font for the skills list
        pdf_content.setFont("Helvetica", regular_font_size)

        # Split the skills into individual lines and filter out any empty lines
        skills_list = [skill.strip() for skill in form_data["Skills"].split("\n") if skill.strip()]

        # Calculate the number of skills per column
        skills_per_column = len(skills_list) // 2

        # Loop through skills and add them side by side in two columns
        for i in range(skills_per_column):
            # Draw the left column skill
            pdf_content.drawString(margin_left * inch, y_position, skills_list[i])
            # Draw the right column skill if it exists
            if i + skills_per_column < len(skills_list):
                pdf_content.drawString(right_column_start, y_position, skills_list[i + skills_per_column])
            # Move to the next line
            y_position -= line_spacing * inch

            # Check if we need to create a new page
            if y_position < bottom_margin:
                pdf_content.showPage()  # Create a new page
                pdf_content.setFont("Helvetica", regular_font_size)  # Reset font
                y_position = page_height - margin_top * inch  # Reset y_position to top of new page

        ## Save PDF Output
        pdf_content.save()

        # Read and display the PDF file
        modified_file = open("JUNK/cv_labs_pdf.pdf", "rb")
        # Close the file
        modified_file.close()
        display_pdf("cv_labs_pdf.pdf")

        with open("JUNK/cv_labs_pdf.pdf", "rb") as file:
            st.download_button(
                label="Download PDF",
                data=file,
                file_name="test_pdf.pdf",
                mime="application/octest-stream"
            )


if __name__ == "__main__":
    main()
