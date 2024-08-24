import streamlit as st
from dotenv import load_dotenv
import base64
import os
import io
from PIL import Image
import pdf2image
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure the API key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("API key is missing. Please check your .env file.")
else:
    model = genai.GenerativeModel('gemini-1.0-pro-latest')
    genai.configure(api_key=api_key)

# Simple login function
def login(username, password):
    # Define your credentials here
    return username == "admin" and password == "password"

# Streamlit App
def main_app():
    def get_gemini_response(input_text, prompt):
        """
        Get response from Gemini AI model using provided job description and prompt.
        """
        combined_prompt = f"{prompt}\n\nJob Description:\n{input_text}"
        try:
            response = model.generate_content(combined_prompt)
            return response.text  # Accessing the generated text
        except Exception as e:
            st.error(f"An error occurred while fetching the response: {e}")
            return ""

    def input_pdf_setup(uploaded_file):
        """
        Convert the uploaded PDF file to base64-encoded JPEG image.
        """
        if uploaded_file is not None:
            # Convert the PDF to images
            images = pdf2image.convert_from_bytes(uploaded_file.read())
            first_page = images[0]

            # Convert to bytes
            img_byte_arr = io.BytesIO()
            first_page.save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()

            pdf_parts = [
                {
                    "mime_type": "image/jpeg",
                    "data": base64.b64encode(img_byte_arr).decode()  # encode to base64
                }
            ]
            return pdf_parts
        else:
            st.error("No file uploaded")
            return None

    st.set_page_config(page_title="ATS Resume Expert")
    st.header("ATS Tracking System")

    input_text = st.text_area("Job Description: ", key="input")
    uploaded_file = st.file_uploader("Upload your resume (PDF)...", type=["pdf"])

    submit1 = st.button("Tell Me About the Resume")
    submit3 = st.button("Percentage match")

    input_prompt1 = """
    You are an experienced Technical Human Resource Manager. Your task is to review the provided resume against the job description.
    Please share your professional evaluation on whether the candidate's profile aligns with the role.
    Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
    """

    input_prompt3 = """
    You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality.
    Your task is to evaluate the resume against the provided job description. Give me the percentage of match if the resume matches
    the job description. First, the output should come as a percentage and then keywords missing and last, final thoughts.
    """

    if submit1:
        if uploaded_file is not None:
            pdf_content = input_pdf_setup(uploaded_file)
            response = get_gemini_response(input_text, input_prompt1)
            st.subheader("The Response is")
            st.write(response)
        else:
            st.write("Please upload the resume")

    elif submit3:
        if uploaded_file is not None:
            pdf_content = input_pdf_setup(uploaded_file)
            response = get_gemini_response(input_text, input_prompt3)
            st.subheader("The Response is")
            st.write(response)
        else:
            st.write("Please upload the resume")

    if st.button("Logout"):
        st.session_state['authenticated'] = False
        st.session_state['page'] = 'login'

# Main login page
def login_page():
    st.set_page_config(page_title="Login")
    st.title("Login Page")

    with st.form(key='login_form'):
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')
        submit_button = st.form_submit_button("Login")

        if submit_button:
            if login(username, password):
                st.success("Login successful")
                st.session_state['authenticated'] = True
                st.session_state['page'] = 'main'
            else:
                st.error("Invalid username or password")

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if 'page' not in st.session_state:
    st.session_state['page'] = 'login'

# Display the appropriate page based on authentication
if st.session_state['authenticated'] and st.session_state['page'] == 'main':
    main_app()
else:
    login_page()
