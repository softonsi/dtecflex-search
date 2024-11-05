import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

class PageContentFetcher:
    def __init__(self, user_agent=None):
        self.user_agent = user_agent or 'Mozilla/5.0 (Linux; Android 13; SM-S901B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36'
    
    def fetch(self, url: str) -> str:
        page_content = self._fetch_with_requests(url)
        if page_content is None:
            page_content = self.fetch_and_extract_text(url)
        return page_content or ""
    
    def extract_text_from_html(self, html_content: str) -> str:
        soup = BeautifulSoup(html_content, 'html.parser')
        return '\n'.join([p.get_text() for p in soup.find_all('p')])
    
    def fetch_and_extract_text(self, url: str) -> str:
        html_content = self.fetch(url)
        return self.extract_text_from_html(html_content)

    def _fetch_with_requests(self, url: str) -> str:
        headers = {'User-Agent': self.user_agent}
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.content
        except requests.RequestException as e:
            print(f"Erro ao acessar a URL com requests: {e}")
        return None

    # def _fetch_with_playwright(self, url: str) -> str:
    #     try:
    #         with sync_playwright() as p:
    #             browser = p.chromium.launch(headless=True)
    #             page = browser.new_page()
    #             page.goto(url)
    #             page.wait_for_load_state(state='networkidle')
    #             page_content = page.content()
    #             print(f"URL processada com playwright: {page.url}")
    #             browser.close()
    #             return page_content
    #     except Exception as e:
    #         print(f"Erro ao acessar a URL com Playwright: {e}")
    #     return None  # Retorna None se falhar
