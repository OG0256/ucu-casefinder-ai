
import streamlit as st
import requests
from bs4 import BeautifulSoup

def search_ulii(query):
    headers = {'User-Agent': 'Mozilla/5.0'}
    search_url = f"https://ulii.org/search?search_api_fulltext={query.replace(' ', '+')}"
    response = requests.get(search_url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        for h3 in soup.find_all('h3', class_='search-result-title'):
            a = h3.find('a', href=True)
            if a:
                title = a.get_text(strip=True)
                link = 'https://ulii.org' + a['href']
                results.append((title, link))
        return results[:5]
    else:
        return []

def get_case_text(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        return "\n\n".join(p.get_text() for p in paragraphs)
    else:
        return "Could not fetch case content."

st.title("🎓 UCU Law CaseFinder AI")
st.markdown("Find full case law decisions from ULII and other free legal sources in Uganda.")

query = st.text_input("Enter case name, keywords, or legal issue:")

if st.button("Search") and query:
    with st.spinner("Searching ULII..."):
        results = search_ulii(query)
    if results:
        st.success("Top cases found:")
        for title, link in results:
            if st.button(f"📄 View: {title}", key=link):
                with st.spinner("Fetching full case text..."):
                    case_text = get_case_text(link)
                st.subheader(title)
                st.write(case_text)
    else:
        st.warning("No results found. Try another query.")
