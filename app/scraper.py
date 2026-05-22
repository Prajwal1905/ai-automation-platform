import requests
from bs4 import BeautifulSoup

def scrape_company_website(company_name: str) -> str:
    try:
        #  Google the company to find their website
        search_url = f"https://www.google.com/search?q={company_name}+official+website"
        headers = {"User-Agent": "Mozilla/5.0"}
        search_response = requests.get(search_url, headers=headers, timeout=5)
        soup = BeautifulSoup(search_response.text, "html.parser")

        # Extract first result URL
        results = soup.select("a")
        website_url = None
        for a in results:
            href = a.get("href", "")
            if "url?q=" in href and "google" not in href:
                website_url = href.split("url?q=")[1].split("&")[0]
                break

        if not website_url:
            return f"Could not find website for {company_name}"

        # Scrape the website
        page_response = requests.get(website_url, headers=headers, timeout=5)
        page_soup = BeautifulSoup(page_response.text, "html.parser")

        #  Extract meaningful text
        paragraphs = page_soup.find_all("p")
        text = " ".join([p.get_text() for p in paragraphs[:10]])
        
        if not text.strip():
            return f"Website found at {website_url} but could not extract content"

        return f"Website: {website_url}\nContent: {text[:1000]}"

    except Exception as e:
        return f"Scraping failed: {str(e)}"


def summarize_company(company_name: str, scraped_content: str, llm_client) -> str:
    try:
        response = llm_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Summarize company information in 2-3 sentences for a CRM record."},
                {"role": "user", "content": f"Company: {company_name}\n\nScraped content:\n{scraped_content}"}
            ],
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Summary failed: {str(e)}"