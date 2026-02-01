"""
this file is supposed to-
takes company name as input
"""

from typing import TypedDict, Sequence, Annotated
from langgraph.graph import StateGraph, START, END, add_messages
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, SystemMessage
from langchain.agents import AgentState
from tools import search_using_tavily

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
        message: Annotated[Sequence[BaseMessage], add_messages]
        result: bool


    #Nodes of the graph
    def __invoke_model(self, state: AgentState) -> AgentState:
        """
        calls the method
        :param state:
        :return:
        """
        system_message = SystemMessage(["You are an AI agent thats responsible to find out what kind of atrocities companies have done against the climate and human rights."
                                        "Use the tools provided for web search. Compile the results in a dictionary format as follows - {"
                                        "\"company name\": ,"
                                        "\"atrocities\": [{"
                                        "   \"title\": , "
                                        "   \"severity\": ,"
                                        "   \"summary\": , "
                                        "   \"link\": }],}"
                                        "Maximum of 5 main atrocities, arranged from worst to best"])
        self.__model.invoke(state["company"])
        return state


    def __init__(self):
        self.__model = ChatOpenAI(model= 'gpt-4o')
        tools = [search_using_tavily]
        graph = StateGraph(AgentState)
        self.__model.bind_tools(tools)

        graph.add_node(self.__invoke_model.__name__, self.__invoke_model)

        graph.add_edge(START, self.__invoke_model.__name__)

        graph.add_node(search_using_tavily.__name__, search_using_tavily)

        graph.add_conditional_edges(self.__invoke_model.__name__, self.should_continue, {
            "end":END,
            "continue": search_using_tavily.__name__,
        })
        graph.add_edge(search_using_tavily.__name__, self.__invoke_model.__name__)
        self.__app = graph.compile()


    @staticmethod
    def should_continue(state: AgentState) -> str:
        messages = state["messages"]
        last_message = messages[-1]
        if not last_message.tool_calls:
            return "end"
        else:
            return "continue"