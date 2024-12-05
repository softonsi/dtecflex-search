from backend.resources.search_term.search_term_repository import SearchTermRepository
from sqlalchemy.orm import Session

class SearchTermService:
    def __init__(self, db: Session):
        self.db = db
        self.termo_busca_repo = SearchTermRepository(db)

    def save(self, categoria: str, palavras_and: list, palavras_or: list):
        self.termo_busca_repo.save(categoria, palavras_and, palavras_or)
    
    def get_processed_terms(self, category: str):
        terms = self.termo_busca_repo.get_terms_by_category(category)
        
        keywords = [term.KEYWORD for term in terms]
        
        return keywords
