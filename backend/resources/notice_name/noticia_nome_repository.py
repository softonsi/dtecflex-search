from typing import Any, Dict, List
from sqlalchemy import func
from typing_extensions import Optional
from backend.resources.notice_name.noticia_nome import NoticiaRaspadaNomeCreateSchema
from sqlalchemy.orm import Session, joinedload
from backend.models.database import NoticiaRaspadaModel, NoticiaRaspadaNomeModel
from datetime import date

class NoticiaNomeRepository:
    def __init__(self, session: Session):
        self.session = session

    def listar_nomes_por_status_e_data_hoje(self, status: str) -> List[Dict[str, Any]]:
        hoje = date.today()

        q = (
            self.session
                .query(NoticiaRaspadaNomeModel)
                .join(
                    NoticiaRaspadaModel,
                    NoticiaRaspadaNomeModel.NOTICIA_ID == NoticiaRaspadaModel.ID
                )
                .filter(NoticiaRaspadaModel.STATUS == status)
        )

        if status == "203-PUBLISHED":
            q = q.filter(func.date(NoticiaRaspadaModel.DT_TRANSFERENCIA) == hoje)
        elif status in ("201-APPROVED", "205-TRANSFERED"):
            q = q.filter(func.date(NoticiaRaspadaModel.DT_APROVACAO) == hoje)

        resultados = q.all()

        def to_dict(obj: NoticiaRaspadaNomeModel) -> Dict[str, Any]:
            d = {
                col.name: getattr(obj, col.name)
                for col in obj.__table__.columns
            }
            d["REG_NOTICIA"] = obj.noticia.REG_NOTICIA
            return d

        return [to_dict(n) for n in resultados]
    
    def obter_contagem_por_status(self) -> List[NoticiaRaspadaNomeModel]:
        hoje = date.today()
        status_list = [
            "203-PUBLISHED",
            "200-TO-APPROVE",
            "201-APPROVED",
            "205-TRANSFERED",
        ]
        resultados: Dict[str, int] = {}

        for status in status_list:
            q = (
                self.session
                    .query(func.count(NoticiaRaspadaNomeModel.ID))
                    .join(
                        NoticiaRaspadaModel,
                        NoticiaRaspadaNomeModel.NOTICIA_ID == NoticiaRaspadaModel.ID
                    )
                    .filter(NoticiaRaspadaModel.STATUS == status)
            )

            if status == "203-PUBLISHED":
                q = q.filter(func.date(NoticiaRaspadaModel.DT_TRANSFERENCIA) == hoje)
            elif status in ("201-APPROVED", "205-TRANSFERED"):
                q = q.filter(func.date(NoticiaRaspadaModel.DT_APROVACAO) == hoje)

            count = q.scalar() or 0
            resultados[status] = count

        return resultados
    
    def create(self, noticia_data: NoticiaRaspadaNomeCreateSchema) -> NoticiaRaspadaNomeModel:
        noticia = NoticiaRaspadaNomeModel(**noticia_data.model_dump())
        self.session.add(noticia)
        self.session.commit()
        self.session.refresh(noticia)
        return noticia

    def find_by_noticia_id(self, noticia_id):
        return self.session.query(NoticiaRaspadaNomeModel).options(
            joinedload(NoticiaRaspadaNomeModel.noticia)
        ).filter(NoticiaRaspadaNomeModel.NOTICIA_ID == noticia_id).all()

    def update(self, nome_id: int, data: NoticiaRaspadaNomeCreateSchema) -> Optional[NoticiaRaspadaNomeModel]:
        nome = self.get_by_id(nome_id)
        if nome:
            for key, value in data.model_dump(exclude_unset=True).items():
                setattr(nome, key, value)
            try:
                self.session.commit()
                self.session.refresh(nome)
                return nome
            except Exception as e:
                self.session.rollback()
                print(f"Erro ao atualizar o nome: {e}")
                return None
        return None

    def get_by_id(self, nome_id: int) -> Optional[NoticiaRaspadaNomeModel]:
            return self.session.query(NoticiaRaspadaNomeModel).filter_by(ID=nome_id).first()

    def delete(self, nome_id: int) -> bool:
            nome = self.get_by_id(nome_id)
            if nome:
                try:
                    self.session.delete(nome)
                    self.session.commit()
                    return True
                except Exception as e:
                    self.session.rollback()
                    print(f"Erro ao deletar o nome: {e}")
                    return False
            return False
