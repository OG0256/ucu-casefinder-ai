import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="UCU CaseFinder AI", layout="wide")
st.title("📘 UCU CaseFinder AI")
st.subheader("Search full-text Ugandan cases from ULII.org")

def search_ulii(keyword):
    url = f"https://ulii.org/search?search_api_fulltext={keyword.replace(' ', '+')}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        return []

    soup = BeautifulSoup(res.text, 'html.parser')
    links = soup.find_all("h3", class_="search-result-title")

    results = []
    for h3 in links[:5]:
        a = h3.find("a")
        if a:
            title = a.text.strip()
            href = a['href']
            full_link = "https://ulii.org" + href
            results.append((title, full_link))

    return results


def get_case_text(case_url):
    res = requests.get(case_url)
    soup = BeautifulSoup(res.content, "html.parser")

    content = soup.find("div", class_="field-item even")
    if not content:
        return "⚠️ Case text not found."

    return content.get_text(separator="\n", strip=True)


# User input
search_term = st.text_input("🔍 Enter a case name, topic, or keyword:")

if search_term:
    with st.spinner("Searching..."):
        cases = search_ulii(search_term)

    if cases:
        st.success(f"Found {len(cases)} result(s):")
        for idx, (title, url) in enumerate(cases):
            if st.button(f"📄 {title}", key=idx):
                st.subheader(title)
                st.markdown(f"[Open on ULII]({url})", unsafe_allow_html=True)
                with st.spinner("Fetching full case text..."):
                    full_text = get_case_text(url)
                st.code(full_text, language='text')
    else:
        st.warning("No cases found. Try a different keyword.")

else:
    st.info("Type something in the search box above to begin.")
