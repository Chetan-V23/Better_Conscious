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
        calls the model and processes the response
        :param state:
        :return:
        """
        logger.debug(f"__invoke_model called for company: {state['company']}")
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
        logger.debug(f"Invoking model with {len(messages)} messages")
        
        try:
            model_response = self.__model.invoke(messages)
            logger.debug(f"Model response received: {model_response}")
        except Exception as e:
            logger.error(f"Error invoking model: {e}", exc_info=True)
            raise

        updated_state = dict(state)
        updated_state["messages"] = [*existing_messages, model_response]
        return updated_state


    def invoke_llm(self, company_name: str) -> dict:
        logger.info(f"Invoking LLM for company: {company_name}")
        try:
            final_state = self.__app.invoke(
                {
                    "company": company_name,
                    "messages": [],
                    "result": False,
                }
            )
            logger.debug(f"LLM graph execution completed for {company_name}")
        except Exception as e:
            logger.error(f"Error during LLM graph invocation for {company_name}: {e}", exc_info=True)
            return {"company_name": company_name, "atrocities": [], "error": str(e)}

        messages = final_state.get("messages", [])
        if not messages:
            logger.warning(f"No messages returned for {company_name}")
            return {"company_name": company_name, "atrocities": []}

        last_message = messages[-1]
        logger.debug(f"Processing last message for {company_name}")
        content = getattr(last_message, "content", "")

        if isinstance(content, list):
            logger.debug("Content is a list, extracting text parts")
            text_parts = [
                part.get("text", "")
                for part in content
                if isinstance(part, dict) and part.get("type") == "text"
            ]
            content = "\n".join(part for part in text_parts if part).strip()

        if isinstance(content, str):
            import json, re
            logger.debug(f"Attempting to parse JSON response: {content[:100]}...")

            stripped = re.sub(r"^```(?:json)?\s*|\s*```$", "", content.strip())
            try:
                parsed = json.loads(stripped)
                if isinstance(parsed, dict):
                    logger.info(f"Successfully parsed LLM response for {company_name}")
                    return parsed
            except json.JSONDecodeError as e:
                logger.warning(f"JSON decode error for {company_name}: {e}")
                pass
        logger.warning(f"LLM response could not be parsed as JSON for {company_name}: {content[:100]}...")
        return {
            "company_name": company_name,
            "atrocities": [],
            "raw_output": content,
        }


    def __init__(self):
        logger.info("Initializing Agent")
        try:
            self.__model = ChatOpenAI(model='gpt-4o')
            logger.info("ChatOpenAI model initialized")
        except Exception as e:
            logger.error(f"Failed to initialize ChatOpenAI model: {e}", exc_info=True)
            raise
        
        tools = [search_using_tavily]
        graph = StateGraph(Agent.AgentState)
        logger.debug("StateGraph created")
        
        self.__model = self.__model.bind_tools(tools)
        logger.debug("Tools bound to model")
        
        tool_node_name = search_using_tavily.name
        tool_node = ToolNode([search_using_tavily])
        logger.debug(f"Tool node created for: {tool_node_name}")

        graph.add_node(self.__invoke_model.__name__, self.__invoke_model)
        graph.add_edge(START, self.__invoke_model.__name__)
        graph.add_node(tool_node_name, tool_node)
        graph.add_conditional_edges(self.__invoke_model.__name__, self.should_continue, {
            "end": END,
            "continue": tool_node_name,
        })
        graph.add_edge(tool_node_name, self.__invoke_model.__name__)
        logger.debug("Graph edges and nodes configured")
        
        self.__app = graph.compile()
        logger.info("Agent graph compiled successfully")


    @staticmethod
    def should_continue(state: "Agent.AgentState") -> str:
        messages = state["messages"]
        last_message = messages[-1]
        has_tool_calls = bool(last_message.tool_calls)
        logger.debug(f"Checking if should continue: has_tool_calls={has_tool_calls}")
        if not has_tool_calls:
            logger.debug("No tool calls found, ending graph execution")
            return "end"
        else:
            logger.debug(f"Found {len(last_message.tool_calls)} tool calls, continuing")
            return "continue"


if __name__ == "__main__":
    res=Agent().invoke_llm("Nike")
    print(res)