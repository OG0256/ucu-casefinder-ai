import streamlit as st
import requests
from bs4 import BeautifulSoup
import logging
import bleach
from requests.exceptions import RequestException

# Set up logging for debugging
logging.basicConfig(level=logging.INFO)

def sanitize_html(text):
    # Only allow basic tags, no scripts or styles
    return bleach.clean(text, tags=['b', 'i', 'u', 'em', 'strong', 'p', 'br'], strip=True)

@st.cache_data(show_spinner=False)
def search_ulii(query, num_results=5):
    """
    Search for legal cases on ULII based on a query.

    Args:
        query (str): The search term or keywords.
        num_results (int): Number of search results to return.

    Returns:
        list or str: A list of tuples containing (title, link), or an error message.
    """
    headers = {'User-Agent': 'Mozilla/5.0'}
    search_url = f"https://ulii.org/search?search_api_fulltext={query.replace(' ', '+')}"
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
    except RequestException as e:
        logging.error(f"Network/search error: {e}")
        return f"An error occurred while searching ULII: {e}"

    soup = BeautifulSoup(response.text, 'html.parser')
    results = []
    for h3 in soup.find_all('h3', class_='search-result-title'):
        a = h3.find('a', href=True)
        if a:
            title = a.get_text(strip=True)
            link = 'https://ulii.org' + a['href']
            results.append((title, link))
            if len(results) >= num_results:
                break
    return results

@st.cache_data(show_spinner=False)
def get_case_text(url):
    """
    Fetch the full text of a legal case from a given ULII URL.

    Args:
        url (str): The URL to the case.

    Returns:
        str: The sanitized text of the case.
    """
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except RequestException as e:
        logging.error(f"Network/case fetch error: {e}")
        return f"An error occurred while fetching the case: {e}"

    soup = BeautifulSoup(response.text, 'html.parser')
    paragraphs = soup.find_all('p')
    case_text = "\n\n".join(p.get_text() for p in paragraphs)
    return sanitize_html(case_text) if case_text else "No case text found."

st.title("🎓 UCU Law CaseFinder AI")
st.markdown("Find full case law decisions from ULII and other free legal sources in Uganda.")

# Sidebar for options
num_results = st.sidebar.slider("Number of results", min_value=1, max_value=10, value=5)

query = st.text_input("Enter case name, keywords, or legal issue:")

if st.button("Search"):
    if not query or not query.strip():
        st.warning("Please enter a valid query.")
    else:
        with st.spinner("Searching ULII..."):
            results =

