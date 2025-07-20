import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="UCU Legal Case Finder", layout="wide")

st.title("📚 UCU Legal Case Finder")
st.subheader("Find full case texts from ULII and more.")

def search_ulii(query):
    """Search ULII and return a list of case titles and links."""
    headers = {'User-Agent': 'Mozilla/5.0'}
    search_url = f"https://ulii.org/search?search_api_fulltext={query.replace(' ', '+')}"
    response = requests.get(search_url, headers=headers)

    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    results = []

    for h3 in soup.find_all('h3', class_='search-result-title'):
        a = h3.find('a', href=True)
        if a:
            title = a.get_text(strip=True)
            link = "https://ulii.org" + a['href']
            results.append((title, link))

    return results[:5]  # Return top 5 results


def get_case_text(url):
    """Extract the full text of the case from the case page."""
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return "⚠️ Failed to fetch the case content."

    soup = BeautifulSoup(response.text, 'html.parser')

    content_div = soup.find('div', class_='field-item even')
    if not content_div:
        return "⚠️ Could not find case text on this page."

    return content_div.get_text(separator="\n", strip=True)


# Sidebar
st.sidebar.header("🔍 Case Search")
query = st.sidebar.text_input("Enter case topic, citation or keyword:")

if query:
    with st.spinner("Searching ULII..."):
        results = search_ulii(query)

    if results:
        st.success(f"Found {len(results)} results. Select one below to view:")
        for title, link in results:
            if st.button(title):
                with st.spinner("Loading full case text..."):
                    case_text = get_case_text(link)
                st.subheader(title)
                st.markdown(
