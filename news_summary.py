# from openai import OpenAI
# import json
# import os
# import base64
# import requests
# import numpy as np
# from PIL import Image
# from io import BytesIO
# from dotenv import load_dotenv
# from docx import Document
# from docx.shared import Inches
# import sys
# import ssl
# import httpx
# import urllib3

# # Suppress InsecureRequestWarning
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# # Disable SSL verification for the entire script
# os.environ['PYTHONHTTPSVERIFY'] = '0'
# ssl._create_default_https_context = ssl._create_unverified_context

# # Load API key
# try:
#     load_dotenv()
#     api_key = os.getenv("OPENAI_API_KEY")
#     if not api_key:
#         raise Exception("API key not found in environment variables!")
# except Exception as e:
#     print(f"Environment setup error: {e}")
#     sys.exit(1)

# # Initialize OpenAI client
# client = OpenAI(
#     api_key=api_key,
#     http_client=httpx.Client(verify=False)
# )

# def image_to_base64(image_url):
#     """Download image and convert to Base64."""
#     try:
#         response = requests.get(image_url, verify=False)
#         response.raise_for_status()
#         return base64.b64encode(response.content).decode('utf-8'), response.content
#     except requests.exceptions.RequestException as e:
#         raise Exception(f"Failed to download image: {e}")

# # Load image URLs from text file
# with open("image_urls.txt", "r") as file:
#     image_urls = [line.strip() for line in file if line.strip()]

# # Create a Word document to store all results
# doc = Document()
# doc.add_heading("News Reports", level=1)

# for idx, image_url in enumerate(image_urls, start=1):
#     try:
#         print(f"Processing image {idx}/{len(image_urls)}: {image_url}")
#         image_base64, image_data = image_to_base64(image_url)
#         image_path = f"output_image_{idx}.jpg"
#         with open(image_path, "wb") as img_file:
#             img_file.write(image_data)

#         # Extract text and identify headline
#         response = client.chat.completions.create(
#             model="gpt-4o",
#             response_format={"type": "json_object"},
#             messages=[
#                 {
#                     "role": "user",
#                     "content": [
#                         {"type": "text", "text": "Extract the text from this image and identify the headline (largest font size line). Return JSON with 'headline' and 'text'."},
#                         {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
#                     ],
#                 }
#             ],
#             max_tokens=1000,
#         )
        
#         response_content = response.choices[0].message.content
#         json_data = json.loads(response_content)
#         headline = json_data.get("headline", "No headline identified")
#         extracted_text = json_data.get("text", "")

#         # Summarization
#         paragraphs = [p.strip() for p in extracted_text.split("\n") if p.strip()]
#         article_text = "\n\n".join(paragraphs)
#         original_word_count = len(article_text.split())
#         target_word_count = int(original_word_count * 0.5)

#         if original_word_count > 0:
#             summary_response = client.chat.completions.create(
#                 model="gpt-4o",
#                 messages=[
#                     {
#                         "role": "user",
#                         "content": f"""
#                         You are an AI summarization assistant. Process the following article:
#                         Headline: {headline}
                        
#                         {article_text}
                    
#                     Important **The language of the summarized text must be same the language of extracted text.**
#                     Please read and understand the entire article below and then produce a contextual summary that preserves all the key points and the core meaning.
#                     The summary should have less than {target_word_count} words (i.e. less than 50% of the original article's word count).
                    
#                     the AI shall write 5 key points from the news in complete meaningful sentence format.When summarizing news, it's crucial to capture the essence of the story without missing any important details. 
#                     The key points has to be written in full sentenses and there has to be 5 complete meaningful sentences.
#                     Here are the key factors to consider:
#                     Focus on the event or action that is the main subject of the news.
#                     Summarize the core facts and developments. For example, if it’s an election, mention key results, controversies, or decisions made.
                    
#                     Identify the main people or organizations involved in the story. This could include political figures, companies, celebrities, or any key individuals related to the event.
#                     Make sure to highlight their roles and significance to the story.
#                     Pinpoint the location of the event or issue. This could be a specific country, city, or region, especially if the location is central to understanding the significance of the story.
  
#                     Understand and summarize the reasons behind the event or decision. Why is it happening? What triggered it? This is essential to grasp the full story.
#                     Impact or consequence of the news should be mentioned here. Consider how the event or situation affects people, regions, industries, or the world in general.
#                     Briefly mention the short-term or long-term impact to give readers a sense of the significance of the event.
                    
#                     **The summary should be written in two paragraphs.** the word count of a paragraph should be between 150 words to 200 words. 
#                     Article:

#                         """
#                     }
#                 ],
#                 max_tokens=1000
#             )
#             summarized_text = summary_response.choices[0].message.content.strip()
#         else:
#             summarized_text = "No text to summarize."

#         # Append results to document
#         doc.add_heading(f"Article {idx}", level=1)
#         doc.add_paragraph(f"Image Source: {image_url}")
#         if os.path.exists(image_path):
#             doc.add_picture(image_path, width=Inches(4))
#         doc.add_heading("Headline", level=2)
#         doc.add_paragraph(headline)
#         doc.add_heading("Summarized Text", level=2)
#         doc.add_paragraph(summarized_text)
#         doc.add_page_break()

#     except Exception as e:
#         print(f"Error processing {image_url}: {e}")

# # Save the document
# output_docx = "news_summary.docx"
# doc.save(output_docx)
# print(f"All summaries saved in {output_docx}")
#ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ
import streamlit as st
import os
import base64
import requests
import json
from openai import OpenAI
from docx import Document
from docx.shared import Inches
from dotenv import load_dotenv
from io import BytesIO
import httpx

# Set Streamlit page configuration at the very beginning
st.set_page_config(page_title="Chakshu News Summarizer", layout="wide")

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = OpenAI(
    api_key=api_key,
    http_client=httpx.Client(verify=False)
)

def image_to_base64(image_url):
    """Download image and convert to Base64."""
    try:
        response = requests.get(image_url, verify=False)
        response.raise_for_status()
        return base64.b64encode(response.content).decode('utf-8'), response.content
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to download image: {e}")

def process_images(image_urls):
    """Process images and return a Word document."""
    doc = Document()
    doc.add_heading("News Reports", level=1)
    
    for idx, image_url in enumerate(image_urls, start=1):
        try:
            st.write(f"Processing image {idx}/{len(image_urls)}: {image_url}")
            image_base64, image_data = image_to_base64(image_url)
            
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
                    messages=[
                    {
                        "role": "user",
                        "content": f"""
                        You are an AI summarization assistant. Process the following article:
                        Headline: {headline}
                        
                        {article_text}
                    
                    Important **The language of the summarized text must be same the language of extracted text.**
                    Please read and understand the entire article below and then produce a contextual summary that preserves all the key points and the core meaning.
                    The summary should have less than {target_word_count} words (i.e. less than 50% of the original article's word count).
                    
                    the AI shall write 5 key points from the news in complete meaningful sentence format.When summarizing news, it's crucial to capture the essence of the story without missing any important details. 
                    The key points has to be written in full sentenses and there has to be 5 complete meaningful sentences.
                    Here are the key factors to consider:
                    Focus on the event or action that is the main subject of the news.
                    Summarize the core facts and developments. For example, if it’s an election, mention key results, controversies, or decisions made.
                    
                    Identify the main people or organizations involved in the story. This could include political figures, companies, celebrities, or any key individuals related to the event.
                    Make sure to highlight their roles and significance to the story.
                    Pinpoint the location of the event or issue. This could be a specific country, city, or region, especially if the location is central to understanding the significance of the story.
  
                    Understand and summarize the reasons behind the event or decision. Why is it happening? What triggered it? This is essential to grasp the full story.
                    Impact or consequence of the news should be mentioned here. Consider how the event or situation affects people, regions, industries, or the world in general.
                    Briefly mention the short-term or long-term impact to give readers a sense of the significance of the event.
                    
                    **The summary should be written in two paragraphs.** the word count of a paragraph should be between 150 words to 200 words. 
                    Article:

                        """
                    }
                    
                    ],
                    max_tokens=1000
                )
                summarized_text = summary_response.choices[0].message.content.strip()
            else:
                summarized_text = "No text to summarize."
            
            # Append results to document
            doc.add_heading(f"Article {idx}", level=1)
            doc.add_paragraph(f"Image Source: {image_url}")
            
            image_stream = BytesIO(image_data)
            doc.add_picture(image_stream, width=Inches(4))
            
            doc.add_heading("Headline", level=2)
            doc.add_paragraph(headline)
            doc.add_heading("Summarized Text", level=2)
            doc.add_paragraph(summarized_text)
            doc.add_page_break()
        
        except Exception as e:
            st.error(f"Error processing {image_url}: {e}")
    
    output_stream = BytesIO()
    doc.save(output_stream)
    output_stream.seek(0)
    return output_stream


# # Streamlit UI
# st.title("Chakshu News Summaraizer")

# def get_base64_image(image_path):
#     """Convert an image to Base64 encoding."""
#     with open(image_path, "rb") as img_file:
#         return base64.b64encode(img_file.read()).decode()

# background_image = get_base64_image("Slide1.JPG")

# st.markdown(f"""
#     <style>
#     .stApp {{
#         background-image: url("data:image/jpeg;base64,{background_image}");
#         background-size: cover;
#         background-position: center;
#         background-attachment: fixed;
#     }}
#     </style>
#     """, unsafe_allow_html=True)

# Streamlit UI
st.title("Chakshu News Summarizer")

def get_base64_image(image_path):
    """Convert an image to Base64 encoding."""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

background_image = get_base64_image("Slide1.JPG")

# File uploader
uploaded_file = st.file_uploader("Upload a .txt file with image URLs", type=["txt"])

st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpeg;base64,{background_image}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    
    h1 {{
        background-color: rgba(255, 255, 255, 0.5); /* Semi-transparent white background */
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        color: black;
        text-shadow: 2px 2px 5px rgba(255, 255, 255, 0.5);
        display: inline-block;
    }}

    /* Styling file uploader label */
    label[data-testid="stFileUploaderLabel"] {{
        background-color: rgba(255, 255, 255, 0.5); /* Semi-transparent white background */
        padding: 10px;
        border-radius: 10px;
        color: #FF5733; /* Change this color as needed */
        text-align: center;
        font-weight: bold;
        font-size: 18px;
        display: inline-block;
    }}
    </style>
    """, unsafe_allow_html=True)

if uploaded_file is not None:
    image_urls = [line.decode("utf-8").strip() for line in uploaded_file.readlines() if line.strip()]
    if st.button("Process Images"):
        doc_file = process_images(image_urls)
        st.download_button("Download Summary", doc_file, file_name="news_summary.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
