from backend.models.database import CategoriaBusca, TermoBusca
from sqlalchemy.orm import Session

class SearchTermRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, category: str, and_words: list, or_words: list):
        category_obj = self.db.query(CategoriaBusca).filter(CategoriaBusca.NM_CATEGORIA == category).first()
        
        if not category_obj:
            category_obj = CategoriaBusca(NM_CATEGORIA=category)
            self.db.add(category_obj)
            self.db.commit()

        keywords = ",".join(and_words)
        or_terms = ",".join(or_words)

        existing_term = self.db.query(TermoBusca).filter(
            TermoBusca.ID_CATEGORIA == category_obj.ID,
            TermoBusca.KEYWORD == keywords,
            TermoBusca.OR_TERMS == or_terms
        ).first()

        if not existing_term:
            term = TermoBusca(KEYWORD=keywords, OR_TERMS=or_terms, ID_CATEGORIA=category_obj.ID)
            self.db.add(term)
            self.db.commit()

    def get_terms_by_category(self, category: str):
        category_obj = self.db.query(CategoriaBusca).filter(CategoriaBusca.NM_CATEGORIA == category).first()
        
        if not category_obj:
            terms = self.db.query(TermoBusca).all()
        else:
            terms = self.db.query(TermoBusca).filter(TermoBusca.ID_CATEGORIA == category_obj.ID).all()
        
        return terms