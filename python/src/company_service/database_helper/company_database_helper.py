from database import db_dependency
from models.company_model import CompanyInfo, CompanyActs
from logger import logger

def get_company_if_exists_in_database(company_name: str, db: db_dependency):
    """
    check if company exists in the database
    """
    logger.info(f"Checking if company: {company_name} exists in the database")
    return db.query(CompanyInfo).filter(CompanyInfo.company_name == company_name).first()


def get_company_acts_from_database(company_info: CompanyInfo, db: db_dependency):
    """
    get company acts from the database
    """
    logger.info(f"Getting company acts for company: {company_info.company_name} from the database")
    return db.query(CompanyActs).filter(CompanyActs.company_id==company_info.id).all()