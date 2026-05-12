from langchain_core.tools import tool
from langchain_tavily.tavily_search import TavilySearch
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from logger import logger

@tool
def search_using_tavily(company_name: str) -> str:
    """
    Method that searches the web for the impact of the company on climate change and human rights violations
    :param company_name: name of the company to search for
    :return: top search results in string format
    """
    try:
        logger.info(f"Starting Tavily search for company: {company_name}")
        query = f"List the main atrocities committed by {company_name} against climate and human rights"
        logger.debug(f"Search query: {query}")

        search_tool = TavilySearch(topic="news", max_results=10)
        logger.info("Tavily search tool initialized")
        
        response = search_tool.invoke({"query": query})
        articles = response.get("results", []) if isinstance(response, dict) else []
        logger.info(f"Retrieved {len(articles)} articles from Tavily search")
        
        context = "\n\n".join([article["title"] + "\n" + article.get("url", "") + "\n" + article["content"] for article in articles])
        logger.info(f"Successfully compiled search context for {company_name}")
        return context
    except Exception as e:
        logger.error(f"Error during Tavily search for {company_name}: {e}", exc_info=True)
        raise