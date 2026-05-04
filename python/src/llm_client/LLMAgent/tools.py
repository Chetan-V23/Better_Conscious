from langchain_core.tools import tool
from langchain_tavily.tavily_search import TavilySearch

@tool
def search_using_tavily(company_name: str) -> str:
    """
    Method that searches the web for the impact of the company on climate change and human rights violations
    :param company_name: name of the company to search for
    :return: top search results in string format
    """

    query = f"List the main atrocities committed by {company_name} against climate and human rights"

    search_tool = TavilySearch(topic="news", max_results=10)
    response = search_tool.invoke({"query": query})
    articles = response.get("results", []) if isinstance(response, dict) else []
    context = "\n\n".join([article["title"] + "\n" + article.get("url", "") + "\n" + article["content"] for article in articles])
    return context