## Import Libraries
import openai
import streamlit as st
from pdfminer.high_level import extract_text
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


# from reportlab.platypus import SimpleDocTemplate, ListFlowable, ListItem

## SetUp Dependencies
### Extract Text
def extract_text_from_pdf(pdf_path):
    return extract_text(pdf_path)


def ChatGPT(user_query):
    """
    This function uses the OpenAI API to generate a response to the given
    user_query using the ChatGPT model
    """
    # Use the OpenAI API to generate a response
    completion = openai.Completion.create(
        engine=model_engine,
        prompt=user_query,
        max_tokens=1024,
        n=1,
        temperature=0.5,
    )
    gpt_response = completion.choices[0].text
    return gpt_response


response = ""


@st.cache_data
def api_call_on(query):
    """
    This function gets the user input, pass it to ChatGPT function and
    displays the response
    """

    response = ChatGPT(query)
    return response


# Set the model engine and your OpenAI API key
model_engine = "text-davinci-003"


# def create_enhanced_categorization_data(text):
#     return resume_data

def format_resume(resume_data):
    formatted_text = ""

    # Personal Details
    formatted_text += "Personal Details\n"
    for key, value in resume_data["personal_details"].items():
        formatted_text += f"- {key}: {value}\n"

    # Profile Summary
    formatted_text += "\nProfile Summary\n"
    formatted_text += f"- {resume_data['profile_summary']}\n"

    # Experience
    formatted_text += "\nExperience\n"
    for idx, experience in enumerate(resume_data["experience"], start=1):
        formatted_text += f"{idx}. Company: {experience['Company']}\n"
        formatted_text += f"   - Location: {experience['Location']}\n"
        formatted_text += f"   - Industry: {experience['Industry']}\n"
        formatted_text += f"   - Position: {experience['Position']}\n"
        formatted_text += f"   - Duration: {experience['Duration']}\n"
        formatted_text += "   - Responsibilities:\n"
        for responsibility in experience["Responsibilities"]:
            formatted_text += f"     - {responsibility}\n"
        formatted_text += "\n"

    return formatted_text


resume_data = {
    "personal_details": {
        "Name": "First Last",
        "Job Title": "Project Manager"
    },
    "profile_summary": "As an experienced Project Manager, I specialize in coordinating people and processes to "
                       "ensure successful project delivery. My focus is on organization, timelines, and achieving "
                       "desired results. I excel at managing multiple tasks, problem-solving, and effective "
                       "communication.",
    "experience": [
        {
            "Company": "Resume Worded",
            "Location": "London, United Kingdom",
            "Industry": "Education Technology",
            "Position": "Project Manager",
            "Duration": "08/2021 – Present",
            "Responsibilities": [
                "Initiated new customer service guidelines, resulting in improved ratings.",
                "Renegotiated pricing with 120+ suppliers, securing an 11.5% discount.",
                "Coordinated contract review and submission for various project-related documents.",
                "Implemented time management and productivity systems, optimizing inter-departmental performance."
            ]
        },
        {
            "Company": "Polyhire",
            "Location": "London, United Kingdom",
            "Industry": "Recruitment and Employer Branding",
            "Position": "Business Analyst",
            "Duration": "10/2019 – 07/2021",
            "Responsibilities": [
                "Implemented a change control process, reducing human errors by 85%.",
                "Created and maintained an enterprise-wide financial data warehouse.",
                "Developed value-added business strategies and comprehensive rebranding, resulting in a 77% revenue "
                "increase.",
                "Initiated Total Quality Control (TQC) improvements in supply chain departments, boosting productivity."
            ]
        },
        {
            "Company": "Growthsi",
            "Location": "London, United Kingdom & Barcelona, Spain",
            "Industry": "Career Training and Membership SaaS",
            "Position": "Key Account Executive",
            "Duration": "11/2018 – 09/2019",
            "Responsibilities": [
                "Championed business pitches, securing $220K in Q1 2019.",
                "Increased online sales within 60 days of employment while decreasing costs."
            ]
        }
    ],
    "education": [
        {
            "School": "University of New York",
            "Major": "Bachelor of Science-Applied Statistics",
            "Location": "New York City, New York",
            "Date": "10/2011 - 06/2014"
        }
    ],
    "skills": [
        "Excellent communicator",
        "Effective problem solver",
        "Skilled in project management",
        "Comfortable managing multiple tasks",
        "Team player"
    ]
}


# def extract_personal_details_from_pdf(text):
#        return
# def extract_profile_summary_from_pdf(pdf_text):
#     ##    return
# def extract_experience_from_pdf(pdf_text):
#     ##    return
# def extract_education_from_pdf(pdf_text):
#     ##    return
# def extract_skills_from_pdf(pdf_text):
#     ##    return


# def enhance_categories(pdf_text):
#     ## return

# def combine_for_best_fit():
#     ## return

def main():
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
    st.sidebar.subheader("Enter OpenAI API Key")
    st.sidebar.info(
        '''
           Enter your **open ai key** and follow-through with the **query** in the **text box** 
           and **press enter** to receive a **response** from the ChatGPT
        '''
    )
    openai.api_key = st.sidebar.text_input('OpenAI API Key', type='password')

    col1, col2 = st.columns(2)

    if uploaded_file_job_desc:
        # Read PDF text
        job_desc_text = extract_text_from_pdf(uploaded_file_job_desc)
        col2.write("Extracted text from the PDF:")
        col2.text_area("Job Description", job_desc_text, height=500)

    elif uploaded_file_job_desc is None:
        st.sidebar.subheader("Try Pasting the job description below:")
        st.sidebar.text_input('Job Description', '<sample job description>')

    if uploaded_file_resume:
        # Read PDF text
        pdf_text = extract_text_from_pdf(uploaded_file_resume)
        col1.write("Extracted text from the PDF:")
        col1.text_area("Resume", pdf_text, height=500)

        ### - LLM Extract Categorization:
        st.divider()
        # personal_details = extract_personal_details_from_pdf(pdf_text)
        personal_details = resume_data.get("personal_details", {})
        experience = resume_data.get("experience", {})
        education = resume_data.get("education", {})
        skills = resume_data.get("skills", {})
        if st.checkbox("Show Enhanced Categorization"):
            st.subheader("Enhanced Categorization")
            # 1. Personal Details,
            st.write("Personal details")
            # col2.info(personal_details)
            # resume_data = create_enhanced_categorization_data(pdf_text)
            st.json(personal_details)
            # 2. Profile summary,
            # profile_summary = resume_data.get("profile_summary", {})
            # st.json(profile_summary)
            # 3. Experience,
            st.write("Experience")
            st.json(experience)
            # 4. Education,
            st.write("Education")
            st.json(education)
            # 5. Skills

        ### - Enhancement
        ### - Combination
        st.divider()
        st.write("Best Fitting")
        formatted_resume = format_resume(resume_data)
        st.text_area("Best Fit Data", formatted_resume, height=250)

        ### - Export
        st.divider()
        # Display extracted text with editable areas
        st.header("Creating Form:")
        extracted_text_sections = st.form(key="extracted_text_form")

        name_section = extracted_text_sections.text_area("Name", personal_details['Name'], height=5)
        contact_section = extracted_text_sections.text_area("Contact Number", personal_details['Job Title'], height=5)
        skills_section = extracted_text_sections.text_area("Skills", "\n".join(skills), height=150)

        # Assuming skills_section contains the user-submitted text
        user_input_text = skills_section
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
            pdf_content.drawString(150, 700, name_section)

            # Add Contact section
            pdf_content.drawString(100, 670, "Contact:")
            pdf_content.drawString(150, 650, contact_section)

            # Add Skills section
            pdf_content.drawString(100, 620, "Skills:")
            # pdf_content.drawString(150, 600, skills_section)
            y_position = 600
            for skill in cleaned_skills:
                pdf_content.drawString(120, y_position, f". {skill}")
                y_position -= 20  # Adjust the vertical spacing

            pdf_content.save()
            with open("new_pdf.pdf", "rb") as file:
                btn = st.download_button(
                    label="Download PDF",
                    data=file,
                    file_name="test_pdf.pdf",
                    mime="application/octest-stream"
                )


## Wire Framing
### SideBar - Uploader(2) /Summary /

### Categorization & Display Enhancement (as in form)

### Combination for best fit

### Introduce Scoring Mechanism (Optional)

if __name__ == "__main__":
    main()
