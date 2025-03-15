import streamlit as st 
import os
import base64
import zipfile
import json
from openai import OpenAI
from docx import Document
from docx.shared import Inches
from dotenv import load_dotenv
from io import BytesIO
import httpx
import time

# Set Streamlit page configuration
st.set_page_config(page_title="Chakshu News Summarizer", layout="wide")

# Load environment variables
load_dotenv()
#api_key = os.getenv("OPENAI_API_KEY")
api_key = os.getenv("OPENAI_API_KEY", st.secrets.get("OPENAI_API_KEY"))

# Initialize OpenAI client
client = OpenAI(
    api_key=api_key,
    http_client=httpx.Client(verify=False)
)

def image_to_base64(image_bytes):
    """Convert image bytes to Base64 encoding."""
    return base64.b64encode(image_bytes).decode('utf-8')

def process_images(image_files):
    """Process images and return a Word document."""
    doc = Document()
    doc.add_heading("News Reports", level=1)
    total_images = len(image_files)
    progress_bar = st.progress(0)
    
    for idx, image_file in enumerate(image_files, start=1):
        try:
            st.write(f"Processing image {idx}/{total_images}")
            image_bytes = image_file.read()
            image_base64 = image_to_base64(image_bytes)
            
            response = client.chat.completions.create(
                model="gpt-4o",
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Extract the text from this image and identify the headline (largest font size line). Return JSON with 'headline' and 'text'."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                        ],
                    }
                ],
                max_tokens=1000,
            )
            
            response_content = response.choices[0].message.content
            json_data = json.loads(response_content)
            headline = json_data.get("headline", "No headline identified")
            extracted_text = json_data.get("text", "")
            
            paragraphs = [p.strip() for p in extracted_text.split("\n") if p.strip()]
            article_text = "\n\n".join(paragraphs)
            original_word_count = len(article_text.split())
            target_word_count = int(original_word_count * 0.5)
            
            if original_word_count > 0:
                summary_response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{
                        "role": "user",
                        "content": f"""
                        You are an AI summarization assistant. Process the following article:
                        Headline: {headline}
                        
                        {article_text}
                        
                        **The language of the summarized text must be the same as the language of extracted text.**
                        
                        Please read and understand the entire article below and then produce a contextual summary that preserves all the key points and the core meaning.
                        The summary should have less than {target_word_count} words (i.e. less than 50% of the original article's word count).
                        
                        The AI shall write 5 key points from the news in complete meaningful sentence format.
                        The key points have to be written in full sentences, and there have to be 5 complete meaningful sentences.
                        
                        **The summary should be written in two paragraphs.** Each paragraph should be between 150 and 200 words.
                        """
                    }],
                    max_tokens=1000
                )
                summarized_text = summary_response.choices[0].message.content.strip()
            else:
                summarized_text = "No text to summarize."
            
            # Append results to document
            doc.add_heading(f"Article {idx}", level=1)
            doc.add_paragraph("Image Source: Uploaded File")
            
            image_stream = BytesIO(image_bytes)
            doc.add_picture(image_stream, width=Inches(4))
            
            doc.add_heading("Headline", level=2)
            doc.add_paragraph(headline)
            doc.add_heading("Summarized Text", level=2)
            doc.add_paragraph(summarized_text)
            doc.add_page_break()
            
            progress_bar.progress(int((idx / total_images) * 100))
            time.sleep(0.5)
        
        except Exception as e:
            st.error(f"Error processing image: {e}")
    
    output_stream = BytesIO()
    doc.save(output_stream)
    output_stream.seek(0)
    return output_stream

# Predefined background image
def get_base64_image(image_path):
    """Convert an image to Base64 encoding."""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

background_image_path = "Slide1.JPG"  # Change this to your local background image path
background_base64 = get_base64_image(background_image_path)

# Styling for improved readability
st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpeg;base64,{background_base64}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    /* White transparent box for the title */
    .title-box {{
        background-color: rgba(255, 255, 255, 0.7);
        padding: 10px;
        border-radius: 4px;
        text-align: left;
        color: black;
        text-shadow: none;
        width: 50%;
        margin-left: 0%
        margin-top: 10px;
        margin-bottom: 10px;
        max-height: 100px; /* Ensures it doesn't expand too much */
    }}

    /* Adjusting all UI elements for better readability */
    .stRadio div[role="radiogroup"], .stFileUploader, .stButton {{
        background-color: rgba(255, 255, 255, 0.7);
        padding: 5px;
        border-radius: 5px;
        width: 50%;
    }}

    .stRadio div[role="radiogroup"] label {{
        background-color: rgba(255, 255, 255, 0.5);
        padding: 5px;
        border-radius: 5px;
    }}
    </style>
    """, unsafe_allow_html=True)

# Navigation - Select Processing Mode
st.markdown('<div class="title-box"><h1>Chakshu News Summarizer</h1></div>', unsafe_allow_html=True)

processing_mode = st.radio("Choose an option:", ["Single Image Processing", "Bulk Image Processing (ZIP)"])

if processing_mode == "Single Image Processing":
    uploaded_image = st.file_uploader("Upload a JPG or PNG image", type=["jpg", "png"])

    if uploaded_image:
        if st.button("Process Image"):
            doc_file = process_images([uploaded_image])
            st.download_button("Download Summary", doc_file, file_name="news_summary.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

elif processing_mode == "Bulk Image Processing (ZIP)":
    uploaded_zip = st.file_uploader("Upload a ZIP file containing images (JPG, PNG only)", type=["zip"])

    if uploaded_zip:
        with zipfile.ZipFile(uploaded_zip, "r") as zip_ref:
            image_files = [
                zip_ref.open(file) for file in zip_ref.namelist()
                if file.lower().endswith((".png", ".jpg",".jpeg"))
            ]
            
            if image_files:
                if st.button("Process Images"):
                    doc_file = process_images(image_files)
                    st.download_button("Download Summary", doc_file, file_name="news_summary.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            else:
                st.error("No valid image files found in the ZIP. Only JPG and PNG are allowed.")

