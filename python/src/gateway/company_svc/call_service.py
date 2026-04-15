import requests, os

def forward_company_info_request(company_name, access):

    company_info_svc = os.getenv("COMPANY_INFO_SVC_URL", "http://localhost:8081")
    response = requests.get(f"{company_info_svc}/get_company_info", json={"company_name": company_name}, headers={"Authorization": f"{access['token']}"})
    if response.status_code != 200:
        return None, (response.text, response.status_code)
    
    return response.json(), None
