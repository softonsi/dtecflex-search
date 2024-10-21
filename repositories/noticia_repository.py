from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from models.database import NoticiaRaspadaModel
from schemas.noticia import NoticiaRaspadaCreateSchema, NoticiaRaspadaUpdateSchema


class NoticiaRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, noticia_data: NoticiaRaspadaCreateSchema) -> NoticiaRaspadaModel:
        #noticia = NoticiaRaspadaModel(**noticia_data.dict(exclude_unset=True))
        noticia = NoticiaRaspadaModel(**noticia_data.model_dump())
        self.session.add(noticia)
        self.session.commit()
        self.session.refresh(noticia)
        return noticia

    def get_by_id(self, noticia_id: int) -> Optional[NoticiaRaspadaModel]:
        return self.session.query(NoticiaRaspadaModel).filter(NoticiaRaspadaModel.ID == noticia_id).first()

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
        query = self.session.query(NoticiaRaspadaModel)
        if filters:
            filter_conditions = []
            if 'FONTE' in filters and filters['FONTE']:
                filter_conditions.append(NoticiaRaspadaModel.FONTE.ilike(f"%{filters['FONTE']}%"))
            if 'STATUS' in filters and filters['STATUS']:
                filter_conditions.append(NoticiaRaspadaModel.STATUS.in_(filters['STATUS']))
            if 'DATA_INICIO' in filters and 'DATA_FIM' in filters:
                filter_conditions.append(
                    NoticiaRaspadaModel.DATA_PUBLICACAO.between(filters['DATA_INICIO'], filters['DATA_FIM'])
                )
            if 'CATEGORIA' in filters and filters['CATEGORIA']:
                filter_conditions.append(NoticiaRaspadaModel.CATEGORIA == filters['CATEGORIA'])
            if 'PERIODO' in filters:
                today = datetime.today()

                if filters['PERIODO'] == 'dia':
                    start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
                    end_date = today.replace(hour=23, minute=59, second=59, microsecond=999999)
                    filter_conditions.append(NoticiaRaspadaModel.DATA_PUBLICACAO.between(start_date, end_date))

                # Filtro por notícias da semana
                elif filters['PERIODO'] == 'semana':
                    start_date = today - timedelta(days=today.weekday())
                    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
                    end_date = today.replace(hour=23, minute=59, second=59, microsecond=999999)
                    filter_conditions.append(NoticiaRaspadaModel.DATA_PUBLICACAO.between(start_date, end_date))

                # Filtro por notícias do mês
                elif filters['PERIODO'] == 'mes':
                    start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)  # Primeiro dia do mês
                    end_date = today.replace(hour=23, minute=59, second=59, microsecond=999999)
                    filter_conditions.append(NoticiaRaspadaModel.DATA_PUBLICACAO.between(start_date, end_date))
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
    #             filter_conditions.append(NoticiaRaspadaModel.FONTE.ilike(f"%{filters['FONTE']}%"))
    #         if 'STATUS' in filters and filters['STATUS']:
    #             print(filter)
    #             filter_conditions.append(NoticiaRaspadaModel.STATUS == filters['STATUS'])
    #         if 'CATEGORIA' in filters and filters['CATEGORIA']:
    #             print(filter)
    #             filter_conditions.append(NoticiaRaspadaModel.CATEGORIA == filters['CATEGORIA'])
    #         if 'DATA_INICIO' in filters and 'DATA_FIM' in filters:
    #             filter_conditions.append(
    #                 NoticiaRaspadaModel.DATA_PUBLICACAO.between(filters['DATA_INICIO'], filters['DATA_FIM'])
    #             )
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
    #                 start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)  # Primeiro dia do mês
    #                 end_date = today.replace(hour=23, minute=59, second=59, microsecond=999999)
    #                 filter_conditions.append(NoticiaRaspadaModel.DATA_PUBLICACAO.between(start_date, end_date))
    #         # Adicione mais filtros conforme necessário
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
        # print('return2', noticia)
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