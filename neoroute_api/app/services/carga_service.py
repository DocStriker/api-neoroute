from app.repositories.carga_repository import CargaRepository   

class CargaService:
    @staticmethod
    def get_top_carga(db):
        result = CargaRepository.top_carga(db)
        if not result:
            return None
        return result
    
    @staticmethod
    def get_cargas(db):
        result = CargaRepository.list_cargas(db)
        return result
    
    @staticmethod
    def get_ocurrency_by_day(db):
        result = CargaRepository.ocurrency_by_day(db)
        return [{"date": str(row[0]), "total": row[1]} for row in result]