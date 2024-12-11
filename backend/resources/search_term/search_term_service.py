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
        
        labels = []
        
        terms_data = []
        
        for term in terms:
            or_terms_list = term.OR_TERMS.split(',') if term.OR_TERMS else []
            label = f"{term.KEYWORD}({', '.join(or_terms_list)})"
            
            labels.append(label)
            
            term_data = {
                'id_categoria': term.ID_CATEGORIA,
                'keyword': term.KEYWORD,
                'or_terms': term.OR_TERMS,
                'label': label
            }
            
            terms_data.append(term_data)
        
        return {
        'labels': labels,
        'terms_data': terms_data
    }
