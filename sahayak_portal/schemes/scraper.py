import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import json
import os
import re
import django
import sys

# Setup Django env
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sahayak_portal.settings')
django.setup()

from schemes.models import Scheme
from schemes.translator import translate_to_lang  # Optional

# Gemini config
genai.configure(api_key="AIzaSyAZo0bscN0f8Uz9Cp_V_OziIsXI8C0bn7w")
model = genai.GenerativeModel("gemini-1.5-flash")

def extract_text_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.get_text(separator="\n")

def extract_scheme_info_from_text(cleaned_text):
    prompt = f"""
You are an intelligent extraction engine. From the given text about a government scheme, extract the following information in **valid JSON** format with all fields accurately and completely filled (if information is available).

Here are the fields to extract:

- **title**: Full name of the scheme.
- **description**: A summary of what the scheme is, its goals, and who it's for (about 3-5 lines).
- **ministry**: Name of the central or state department or ministry responsible for the scheme (e.g., Social Justice Department, Government of Kerala).
- **state**: Name of the state (if state-specific) or "All India" if applicable.
- **scheme_category**: A broad category like 'Education', 'Healthcare', 'Financial Assistance', etc.
- **gender**: Eligible genders (e.g., Male, Female, All).
- **age_group**: Age range if mentioned, otherwise leave as empty string.
- **caste**: Mention if the scheme is limited to any caste(s), or leave as empty string.
- **residence**: Any residence-specific eligibility (e.g., rural/urban/locality).
- **minority**: Whether minorities are eligible or targeted.
- **differently_abled**: only Boolean  for disabled persons.
- **benefit_type**: A list of benefits offered. Each benefit should be descriptive (e.g., "₹1950/- Course Fee Assistance for 11th Class", not just "Course Fee").
- **eligibility_criteria**: A **detailed bullet-point list** of all eligibility conditions. Try to keep the original wording.
- **documents_required**: A **list of documents** required to apply (try to extract even if they are inline or in paragraph form).
- **tags**: A list of tags/keywords related to the scheme (e.g., ["Disabled", "Student", "Financial Assistance", "Kerala", "APL", "BPL"]).
- **actual_text**: The entire original text extracted from the webpage, formatted with **<p>**, **<ul>**, **<li>**, and **<strong>** tags wherever applicable.

Below is the text content of the scheme page. Extract the required fields from this text.

TEXT:
{cleaned_text}

Please respond with **only the JSON object**, no explanation or markdown. Ensure the JSON is properly closed and parsable."""  # Keep your same Gemini prompt
    response = model.generate_content(prompt)
    try:
        match = re.search(r"\{[\s\S]*\}", response.text)
        if match:
            return json.loads(match.group(0))
        else:
            print("No JSON found.")
            return None
    except json.JSONDecodeError as e:
        print("JSON error:", e)
        return None

def save_to_database(data, source_url):
    title = data.get('title')
    description = data.get('description')
    ministry = data.get('ministry', '')
    state = data.get('state', '')
    category = data.get('scheme_category', '')
    gender = data.get('gender', '')
    age_group = data.get('age_group', '')
    caste = data.get('caste', '')
    residence = data.get('residence', '')
    minority = data.get('minority', False)
    differently_abled = data.get('differently_abled', False)

    eligibility = data.get('eligibility_criteria', [])
    benefits = data.get('benefit_type', [])
    documents = data.get('documents_required', [])
    tags = data.get('tags', [])

    # Make sure list-like fields are stored as strings
    def ensure_string_list(value):
        if isinstance(value, list):
            return "\n".join(value)
        elif isinstance(value, str):
            return value
        else:
            return ""

    Scheme.objects.create(
        title=title,
        description=description,
        ministry=ministry,
        state=state,
        category=category,
        gender=gender,
        age_group=age_group,
        caste=caste,
        residence=residence,
        minority=minority,
        differently_abled=differently_abled,
        eligibility_criteria=ensure_string_list(eligibility),
        benefit_type=ensure_string_list(benefits),
        documents_required=ensure_string_list(documents),
        tags=ensure_string_list(tags),
        language='en',
        url=source_url
    )

    print(f"✅ Saved scheme: {title}")

def extract_from_url(url):
    cleaned_text = extract_text_from_url(url)
    data = extract_scheme_info_from_text(cleaned_text)
    if data:
        save_to_database(data, url)
    else:
        print("❌ Extraction failed.")


def process_links(link_array):
    for link in link_array:
        extract_from_url(link)

# Test with a sample URL
link_array=['https://www.myscheme.gov.in/schemes/fadsp1012e', 'https://www.myscheme.gov.in/schemes/icmr-pdf', 'https://www.myscheme.gov.in/schemes/tkgthe', 'https://www.myscheme.gov.in/schemes/skerala', 'https://www.myscheme.gov.in/schemes/sgassobcaniphsaislecxixii', 'https://www.myscheme.gov.in/schemes/nfbsup', 'https://www.myscheme.gov.in/schemes/dacsspostmsebcs', 'https://www.myscheme.gov.in/schemes/owjws', 'https://www.myscheme.gov.in/schemes/sjpfsgc', 'https://www.myscheme.gov.in/schemes/evtala']
process_links(link_array)