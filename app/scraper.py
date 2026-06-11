import requests
from bs4 import BeautifulSoup
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

#Searches DuckDuckGo for the company website
#BeautifulSoup grabs meta description or first paragraphs
def scrape_company_website(company_name: str) -> str:
    try:
        search_url = f"https://html.duckduckgo.com/html/?q={company_name}+official+website"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

        search_response = requests.get(search_url, headers=headers, timeout=5)
        soup = BeautifulSoup(search_response.text, "html.parser")

        results = soup.select(".result__url")
        if not results:
            return None

        website_url = "https://" + results[0].get_text().strip()
        page_response = requests.get(website_url, headers=headers, timeout=5)
        page_soup = BeautifulSoup(page_response.text, "html.parser")

        meta = page_soup.find("meta", attrs={"name": "description"})
        if meta and meta.get("content"):
            return f"Website: {website_url}\nContent: {meta['content']}"

        paragraphs = page_soup.find_all("p")
        text = " ".join([p.get_text() for p in paragraphs[:5]])
        return f"Website: {website_url}\nContent: {text[:800]}"

    except Exception:
        return None


# Summarizes company info using LangChain; falls back to LLM knowledge if scraping failed
def summarize_company(company_name: str, scraped_content: str) -> str:
    try:
        if scraped_content:
            user_input = f"Company: {company_name}\n\nScraped content:\n{scraped_content}"
        else:
            user_input = f"Give me a 2-3 sentence CRM summary of the company: {company_name}. Include what they do, their industry, and size if known."

        prompt = ChatPromptTemplate.from_messages([
            ("system", "Summarize company information in 2-3 sentences for a CRM record."),
            ("user", "{input}")
        ])
        chain = prompt | llm | StrOutputParser()
        return chain.invoke({"input": user_input})
    except Exception as e:
        return f"Summary failed: {str(e)}"