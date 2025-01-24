from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timedelta

from backend.models.database import NoticiaRaspadaModel
from backend.resources.notice.noticia import NoticiaRaspadaCreateSchema, NoticiaRaspadaUpdateSchema


class NoticiaRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all_fontes(self) -> List[str]:
        query = self.session.query(NoticiaRaspadaModel.FONTE).distinct()
        fontes = [row.FONTE for row in query.all()]
        return fontes

    def create(self, noticia_data: NoticiaRaspadaCreateSchema) -> NoticiaRaspadaModel:
        #noticia = NoticiaRaspadaModel(**noticia_data.dict(exclude_unset=True))
        noticia = NoticiaRaspadaModel(**noticia_data.model_dump())
        self.session.add(noticia)
        self.session.commit()
        self.session.refresh(noticia)
        return noticia

    def get_by_id(self, noticia_id: int) -> Optional[NoticiaRaspadaModel]:
        return self.session.query(NoticiaRaspadaModel).filter(NoticiaRaspadaModel.ID == noticia_id).first()

    def get_by_id_with_names(self, noticia_id: int) -> Optional[NoticiaRaspadaModel]:
            return self.session.query(NoticiaRaspadaModel)\
                .options(joinedload(NoticiaRaspadaModel.nomes_raspados))\
                .filter(NoticiaRaspadaModel.ID == noticia_id)\
                .first()
    
    def listar_noticias_edit_mode_por_usuario(self, usuario_id: int, offset: int = 0, limit: int = 10) -> List[NoticiaRaspadaModel]:
        query = self.session.query(NoticiaRaspadaModel).options(
            joinedload(NoticiaRaspadaModel.nomes_raspados),
            joinedload(NoticiaRaspadaModel.mensagens)
        )

        query = query.filter(
            and_(
                NoticiaRaspadaModel.STATUS.in_(['07-EDIT-MODE', '06-REPROVED']),
                NoticiaRaspadaModel.ID_USUARIO == usuario_id
            )
        )

        query = query.offset(offset).limit(limit)
        noticias = query.all()

        noticias_por_status = defaultdict(list)

        for noticia in noticias:
            noticias_por_status[noticia.STATUS].append(noticia)

        return dict(noticias_por_status)

    def xlist(self, limit: int = None) -> List[NoticiaRaspadaModel]:
        query = self.session.query(NoticiaRaspadaModel).order_by(NoticiaRaspadaModel.ID.desc())
        if limit:
            query = query.limit(limit)

        return query.all()

    def xxlist(self, offset: int = 0, limit: int = 10) -> List[NoticiaRaspadaModel]:
        query = self.session.query(NoticiaRaspadaModel).order_by(NoticiaRaspadaModel.ID.desc())
        query = query.offset(offset).limit(limit)
        return query.all()

    def list(self, offset: int = 0, limit: int = 10, filters: Optional[Dict[str, Any]] = None) -> Tuple[List[NoticiaRaspadaModel], int]:
        query = self.session.query(NoticiaRaspadaModel).options(joinedload(NoticiaRaspadaModel.nomes_raspados))

        if filters:
            filter_conditions = []
            if 'FONTE' in filters and filters['FONTE']:
                if isinstance(filters['FONTE'], list):
                    filter_conditions.append(NoticiaRaspadaModel.FONTE.in_(filters['FONTE']))
                else:
                    filter_conditions.append(NoticiaRaspadaModel.FONTE.ilike(f"%{filters['FONTE']}%"))
            if 'STATUS' in filters and filters['STATUS']:
                filter_conditions.append(NoticiaRaspadaModel.STATUS.in_(filters['STATUS']))
            if 'DATA_INICIO' in filters and 'DATA_FIM' in filters:
                filter_conditions.append(
                    NoticiaRaspadaModel.DATA_PUBLICACAO.between(filters['DATA_INICIO'], filters['DATA_FIM'])
                )
            if 'CATEGORIA' in filters and filters['CATEGORIA']:
                if isinstance(filters['CATEGORIA'], list):
                    filter_conditions.append(NoticiaRaspadaModel.CATEGORIA.in_(filters['CATEGORIA']))
                else:
                    filter_conditions.append(NoticiaRaspadaModel.CATEGORIA == filters['CATEGORIA'])
            if 'PERIODO' in filters:
                today = datetime.today()

                if filters['PERIODO'] == 'dia':
                    start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
                    end_date = today.replace(hour=23, minute=59, second=59, microsecond=999999)
                    filter_conditions.append(NoticiaRaspadaModel.DATA_PUBLICACAO.between(start_date, end_date))

                elif filters['PERIODO'] == 'semana':
                    start_date = today - timedelta(days=today.weekday())
                    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
                    end_date = today.replace(hour=23, minute=59, second=59, microsecond=999999)
                    filter_conditions.append(NoticiaRaspadaModel.DATA_PUBLICACAO.between(start_date, end_date))

                elif filters['PERIODO'] == 'mes':
                    start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                    end_date = today.replace(hour=23, minute=59, second=59, microsecond=999999)
                    filter_conditions.append(NoticiaRaspadaModel.DATA_PUBLICACAO.between(start_date, end_date))

            if 'USUARIO_ID' in filters and filters['USUARIO_ID']:
                filter_conditions.append(NoticiaRaspadaModel.ID_USUARIO == filters['USUARIO_ID'])

            if filter_conditions:
                query = query.filter(and_(*filter_conditions))

        total_count = query.count()

        query = query.order_by(NoticiaRaspadaModel.ID.desc()).offset(offset).limit(limit)
        return query.all(), total_count
    # def list(self, offset: int = 0, limit: int = 10, filters: Optional[Dict[str, Any]] = None) -> Tuple[List[NoticiaRaspadaModel], int]:
    #     query = self.session.query(NoticiaRaspadaModel)
    #     if filters:
    #         filter_conditions = []
    #         if 'FONTE' in filters and filters['FONTE']:
    #             if isinstance(filters['FONTE'], list):
    #                 filter_conditions.append(NoticiaRaspadaModel.FONTE.in_(filters['FONTE']))
    #             else:
    #                 filter_conditions.append(NoticiaRaspadaModel.FONTE.ilike(f"%{filters['FONTE']}%"))
    #         if 'STATUS' in filters and filters['STATUS']:
    #             filter_conditions.append(NoticiaRaspadaModel.STATUS.in_(filters['STATUS']))
    #         if 'DATA_INICIO' in filters and 'DATA_FIM' in filters:
    #             filter_conditions.append(
    #                 NoticiaRaspadaModel.DATA_PUBLICACAO.between(filters['DATA_INICIO'], filters['DATA_FIM'])
    #             )
    #         if 'CATEGORIA' in filters and filters['CATEGORIA']:
    #             if isinstance(filters['CATEGORIA'], list):
    #                 filter_conditions.append(NoticiaRaspadaModel.CATEGORIA.in_(filters['CATEGORIA']))
    #             else:
    #                 filter_conditions.append(NoticiaRaspadaModel.CATEGORIA == filters['CATEGORIA'])
    #         if 'PERIODO' in filters:
    #             today = datetime.today()

    #             if filters['PERIODO'] == 'dia':
    #                 start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
    #                 end_date = today.replace(hour=23, minute=59, second=59, microsecond=999999)
    #                 filter_conditions.append(NoticiaRaspadaModel.DATA_PUBLICACAO.between(start_date, end_date))

    #             elif filters['PERIODO'] == 'semana':
    #                 start_date = today - timedelta(days=today.weekday())
    #                 start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    #                 end_date = today.replace(hour=23, minute=59, second=59, microsecond=999999)
    #                 filter_conditions.append(NoticiaRaspadaModel.DATA_PUBLICACAO.between(start_date, end_date))

    #             elif filters['PERIODO'] == 'mes':
    #                 start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    #                 end_date = today.replace(hour=23, minute=59, second=59, microsecond=999999)
    #                 filter_conditions.append(NoticiaRaspadaModel.DATA_PUBLICACAO.between(start_date, end_date))
            
    #         if 'USUARIO_ID' in filters and filters['USUARIO_ID']:
    #             filter_conditions.append(NoticiaRaspadaModel.ID_USUARIO == filters['USUARIO_ID'])
            
    #         if filter_conditions:
    #             query = query.filter(and_(*filter_conditions))

    #     total_count = query.count()

    #     query = query.order_by(NoticiaRaspadaModel.ID.desc()).offset(offset).limit(limit)
    #     return query.all(), total_count

    def update(self, noticia_id: int, noticia_data: NoticiaRaspadaUpdateSchema) -> Optional[NoticiaRaspadaModel]:
        noticia = self.get_by_id(noticia_id)
        try:
            if noticia:
                noticia_schema = NoticiaRaspadaUpdateSchema.model_validate(noticia, from_attributes=True)
                for key, value in noticia_data.model_dump(exclude_unset=True).items():
                    setattr(noticia, key, value)
                self.session.commit()
                self.session.refresh(noticia)
        except Exception as err:
            print('erro repository:', err)
        return noticia

    def xupdate(self, noticia_id: int, noticia_data: NoticiaRaspadaUpdateSchema) -> Optional[NoticiaRaspadaModel]:
        noticia = self.get_by_id(noticia_id)
        if noticia:
            for key, value in noticia_data.dict(exclude_unset=True).items():
                setattr(noticia, key, value)
            self.session.commit()
            self.session.refresh(noticia)
        return noticia

    def delete(self, noticia_id: int) -> bool:
        noticia = self.get_by_id(noticia_id)
        if noticia:
            self.session.delete(noticia)
            self.session.commit()
            return True
        return False

    def count(self) -> int:
            return self.session.query(NoticiaRaspadaModel).count()
