import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# class PageContentFetcher:
#     def __init__(self, user_agent=None):
#         self.user_agent = user_agent or 'Mozilla/5.0 (Linux; Android 13; SM-S901B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36'
    
#     def fetch(self, url: str) -> str:
#         page_content = self._fetch_with_requests(url)
#         if page_content is None:
#             page_content = self.fetch_and_extract_text(url)
#         return page_content or ""

#     def extract_text_from_html(self, html_content: str) -> str:
#         soup = BeautifulSoup(html_content, 'html.parser')
#         return '\n'.join([p.get_text() for p in soup.find_all('p')])

#     def fetch_and_extract_text(self, url: str) -> str:
#         html_content = self.fetch(url)
#         return self.extract_text_from_html(html_content)

#     def _fetch_with_requests(self, url: str) -> str:
#         headers = {'User-Agent': self.user_agent}
#         try:
#             response = requests.get(url, headers=headers)
#             if response.status_code == 200:
#                 return response.content
#         except requests.exceptions.Timeout:
#             print(f"Erro: Timeout ao acessar a URL {url} com requests.")
#         except requests.RequestException as e:
#             print(f"Erro ao acessar a URL com requests: {e}")
#         return self._fetch_with_playwright(url)

#     def _fetch_with_playwright(self, url: str) -> str:
#         try:
#             with sync_playwright() as p:
#                 browser = p.chromium.launch(headless=True)
#                 page = browser.new_page()

#                 page.goto(url, timeout=self.max_timeout * 1000)
#                 page.wait_for_load_state(state='networkidle', timeout=self.max_timeout * 1000)
                
#                 page_content = page.content()
#                 print(f"URL processada com playwright: {page.url}")
#                 browser.close()
#                 return page_content
#         except PlaywrightTimeoutError:
#             print(f"Erro: Timeout ao acessar a URL {url} com Playwright.")
#         except Exception as e:
#             print(f"Erro ao acessar a URL com Playwright: {e}")
#         return None  # Retorna None se falhar


import trafilatura

class PageContentFetcher:
    def __init__(self, user_agent=None, timeout=30):
        self.user_agent = user_agent or (
            'Mozilla/5.0 (Linux; Android 13; SM-S901B) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/112.0.0.0 Mobile Safari/537.36'
        )
        self.timeout = timeout  # em segundos

    def fetch(self, url: str) -> str:
        """Tenta baixar o HTML via requests; se falhar, cai no Playwright."""
        html = self._fetch_with_requests(url)
        if html is None:
            html = self._fetch_with_playwright(url)
        return html or ""

    def _fetch_with_requests(self, url: str) -> str | None:
        headers = {'User-Agent': self.user_agent}
        try:
            r = requests.get(url, headers=headers, timeout=self.timeout)
            if r.status_code == 200:
                return r.text
        except requests.exceptions.Timeout:
            print(f"Timeout requests: {url}")
        except requests.RequestException as e:
            print(f"Erro requests: {e}")
        return None

    def _fetch_with_playwright(self, url: str) -> str | None:
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(user_agent=self.user_agent)
                page.goto(url, timeout=self.timeout * 1000)
                page.wait_for_load_state('networkidle', timeout=self.timeout * 1000)
                content = page.content()
                browser.close()
                return content
        # except PlaywrightTimeoutError:
        #     print(f"Timeout Playwright: {url}")
        except Exception as e:
            print(f"Erro Playwright: {e}")
        return None

    def fetch_and_extract_text(self, url: str) -> str:
        """Baixa e extrai texto limpo usando Trafilatura."""
        html = self.fetch(url)
        if not html:
            return ""
        text = trafilatura.extract(html, include_comments=False)
        return text or ""
