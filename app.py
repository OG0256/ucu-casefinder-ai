def search_ulii(query):
    headers = {'User-Agent': 'Mozilla/5.0'}
    search_url = f"https://ulii.org/search?search_api_fulltext={query.replace(' ', '+')}"
    response = requests.get(search_url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        # ULII now lists results inside <h3 class="search-result-title"><a href="...">Title</a></h3>
        for h3 in soup.find_all('h3', class_='search-result-title'):
            a = h3.find('a', href=True)
            if a:
                title = a.get_text(strip=True)
                link = 'https://ulii.org' + a['href']
                results.append((title, link))
        return results[:5]  # top 5 matches
    else:
        return []
