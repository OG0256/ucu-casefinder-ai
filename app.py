import streamlit as st
import requests
import os
from bs4 import BeautifulSoup
import openai

# Set up OpenAI key
openai.api_key = os.getenv("OPENAI_API_KEY")

# App UI
st.set_page_config(page_title="UCU CaseFinder AI", page_icon="⚖️", layout="centered")
st.title("⚖️ UCU CaseFinder AI Agent")
st.write("Search for Ugandan legal cases and get full detailed judgments with simple explanations.")

# Input from user
query = st.text_input("🔍 What case are you looking for? (e.g. 'Land dispute Kyambadde 2023')")

# Function to search ULII
def search_ulii(query):
    headers = {'User-Agent': 'Mozilla/5.0'}
    search_url = f"https://ulii.org/search?search_api_fulltext={query.replace(' ', '+')}"
    response = requests.get(search_url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        results = soup.find_all('a', class_='search-result-title')
        links = []
        for result in results[:3]:
            title = result.get_text(strip=True)
            link = 'https://ulii.org' + result['href']
            links.append((title, link))
        return links
    else:
        return []

# Function to extract full case text
def get_case_text(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    content_div = soup.find('div', {'class': 'field--name-body'})
    if content_div:
        return content_div.get_text(strip=True)
    return "Case text could not be retrieved."

# Function to simplify case using AI
def simplify_case(case_text):
    prompt = (
        "You are a Ugandan law tutor helping a university student. "
        "Explain this case simply and fully, in an easy-to-understand way:\n\n"
        f"{case_text[:6000]}"  # Limit for OpenAI input tokens
    )

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1024
    )
    return response['choices'][0]['message']['content']

# When user enters a query
if query:
    with st.spinner("🔎 Searching ULII..."):
        case_links = search_ulii(query)

    if case_links:
        for title, link in case_links:
            st.markdown(f"### 📄 {title}")
            st.markdown(f"[Read Full Case on ULII]({link})")

            with st.spinner("🧠 Fetching and simplifying case..."):
                full_text = get_case_text(link)
                simplified = simplify_case(full_text)
                with st.expander("📘 Simplified Explanation"):
                    st.write(simplified)
    else:
        st.warning("No results found on ULII. Try a different query.")

# Footer
st.markdown("---")
st.caption("© 2025 UCU CaseFinder AI. Built with ❤️ for UCU law students.")
