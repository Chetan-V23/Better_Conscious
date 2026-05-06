"""
this file is supposed to-
takes company name as input
"""

from typing import TypedDict, Sequence, Annotated
from langgraph.graph import StateGraph, START, END, add_messages
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, SystemMessage
from .tools import search_using_tavily
import dotenv
dotenv.load_dotenv()
from logger import logger

class Agent:
    """
    take a company
    return atrocities
    by-
    using openai
    and
    using tavily search for web results and web scraping
    this will hold the graph and the compiled graph. it should be singleton
    """
    class AgentState(TypedDict):
        company: str
        messages: Annotated[Sequence[BaseMessage], add_messages]
        result: bool


    #Nodes of the graph
    def __invoke_model(self, state: "Agent.AgentState") -> "Agent.AgentState":
        """
        calls the method
        :param state:
        :return:
        """
        system_message = SystemMessage(
            "You are an AI agent responsible for finding atrocities committed by companies against climate and human rights. "
            "Use the provided tools for web search. "
            "Return ONLY a raw JSON object with no markdown, no code fences, no explanation, and no text before or after it. "
            "The JSON must follow this exact structure: "
            '{"company_name": "<name>", "atrocities": [{"title": "<title>", "severity": "<severity>", "summary": "<summary>", "link": "<full url>"}]}. '
            "Return a maximum of 5 atrocities ordered from most severe to least severe."
        )

        existing_messages = list(state.get("messages", []))
        messages = [system_message, *existing_messages, ("human", state["company"])]
        model_response = self.__model.invoke(messages)

        updated_state = dict(state)
        updated_state["messages"] = [*existing_messages, model_response]
        return updated_state


    def invoke_llm(self, company_name: str) -> dict:

        logger.info(f"Invoking LLM for company: {company_name}")
        final_state = self.__app.invoke(
            {
                "company": company_name,
                "messages": [],
                "result": False,
            }
        )

        messages = final_state.get("messages", [])
        if not messages:
            return {"company_name": company_name, "atrocities": []}

        last_message = messages[-1]
        content = getattr(last_message, "content", "")

        if isinstance(content, list):
            text_parts = [
                part.get("text", "")
                for part in content
                if isinstance(part, dict) and part.get("type") == "text"
            ]
            content = "\n".join(part for part in text_parts if part).strip()

        if isinstance(content, str):
            import json, re

            stripped = re.sub(r"^```(?:json)?\s*|\s*```$", "", content.strip())
            try:
                parsed = json.loads(stripped)
                if isinstance(parsed, dict):
                    logger.info(f"LLM response content: {content}")
                    return parsed
            except json.JSONDecodeError:
                pass
        logger.warning(f"LLM response could not be parsed as JSON: {content}")
        return {
            "company_name": company_name,
            "atrocities": [],
            "raw_output": content,
        }


    def __init__(self):
        self.__model = ChatOpenAI(model= 'gpt-4o')
        tools = [search_using_tavily]
        graph = StateGraph(Agent.AgentState)
        self.__model = self.__model.bind_tools(tools)
        tool_node_name = search_using_tavily.name

        tool_node = ToolNode([search_using_tavily])

        graph.add_node(self.__invoke_model.__name__, self.__invoke_model)

        graph.add_edge(START, self.__invoke_model.__name__)

        graph.add_node(tool_node_name, tool_node)

        graph.add_conditional_edges(self.__invoke_model.__name__, self.should_continue, {
            "end":END,
            "continue": tool_node_name,
        })
        graph.add_edge(tool_node_name, self.__invoke_model.__name__)
        self.__app = graph.compile()


    @staticmethod
    def should_continue(state: "Agent.AgentState") -> str:
        messages = state["messages"]
        last_message = messages[-1]
        if not last_message.tool_calls:
            return "end"
        else:
            return "continue"


if __name__ == "__main__":
    res=Agent().invoke_llm("Nike")
    print(res)