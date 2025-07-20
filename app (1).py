
import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai
import os

st.set_page_config(page_title="UCU CaseFinder AI", layout="wide")
st.title("📚 UCU CaseFinder AI")
st.markdown("Search ULII and get **full legal cases** explained simply.")

openai.api_key = os.getenv("OPENAI_API_KEY")

def search_ulii(keyword):
    url = f"https://ulii.org/search?search_api_fulltext={keyword.replace(' ', '+')}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        return []

    soup = BeautifulSoup(res.text, 'html.parser')
    result_divs = soup.find_all("div", class_="search-result")

    results = []
    for div in result_divs[:5]:
        h3 = div.find("h3", class_="title") or div.find("h3")
        if h3:
            a = h3.find("a")
            if a:
                title = a.text.strip()
                link = a['href']
                full_url = f"https://ulii.org{link}"
                results.append((title, full_url))
    return results

def extract_case_text(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        return "Failed to fetch the case content."

    soup = BeautifulSoup(res.text, 'html.parser')
    content = soup.find("div", class_="content") or soup.find("div", class_="doc-content")
    return content.get_text(separator="\n").strip() if content else "No content found."

def simplify_case(case_text):
    prompt = (
        "You are a legal AI assistant helping Ugandan law students. "
        "Summarize the following legal case in simple, detailed terms. "
        "Include facts, issues, decision, and judge's reasoning:

"
        f"{case_text}"
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
            temperature=0.4
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"OpenAI API error: {str(e)}"

query = st.text_input("Enter a legal topic or case name (e.g. breach of contract, locus standi):")

if st.button("Search Cases") and query:
    with st.spinner("Searching ULII for relevant cases..."):
        results = search_ulii(query)

    if not results:
        st.warning("No cases found. Try another keyword.")
    else:
        for title, link in results:
            st.markdown(f"### [{title}]({link})")
            with st.expander("🔍 View and Simplify Case"):
                raw_text = extract_case_text(link)
                st.text_area("Raw Case Text", raw_text[:3000], height=300)
                if st.button(f"Simplify: {title}", key=link):
                    with st.spinner("Simplifying case using AI..."):
                        explanation = simplify_case(raw_text)
                    st.markdown("#### 🧠 Simplified Explanation")
                    st.write(explanation)
