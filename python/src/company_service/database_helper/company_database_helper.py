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


def write_company_to_database(payload: dict, db: db_dependency):
    """
    write company and its acts to the database from an LLM result payload
    """
    company_name = payload["company_name"]
    logger.info(f"Writing company: {company_name} to the database")

    company = db.query(CompanyInfo).filter(CompanyInfo.company_name == company_name).first()
    if not company:
        company = CompanyInfo(company_name=company_name)
        db.add(company)
        db.flush()

    severity_map = {"low": 1, "medium": 2, "high": 3}
    for atrocity in payload.get("atrocities", []):
        severity_int = severity_map.get(atrocity.get("severity", "").lower(), 2)
        act = CompanyActs(
            company_id=company.id,
            act_severity=severity_int,
            act_title=atrocity.get("title", ""),
            act_description=atrocity.get("summary", ""),
        )
        db.add(act)

    db.commit()