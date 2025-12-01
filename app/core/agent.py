from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph.state import CompiledStateGraph
from langgraph.graph import StateGraph, START, END

from typing import Optional

import os

from schemas import GraphState
from utils import dump_messages, prepare_messages


class Agent:

    def __init__(self):
        self._model = ChatGoogleGenerativeAI(
            model_name="gemini-2.0-flash", api_key=os.getenv("GEMINI_API_KEY")
        )
        self._graph: Optional[CompiledStateGraph] = None

    async def _inference_node(self, state: GraphState) -> GraphState:
        
        messages = prepare_messages(messages=state.messages, llm=self._model, system_prompt="NO PROMPT YET")

        response = await self._model.ainvoke(
            dump_messages(messages=messages),
        )

        return {"messages": [response]}

    def _build_graph(self) -> Optional[CompiledStateGraph]:

        if self._graph is not None:
            return self._graph

        builder = StateGraph(GraphState)
        builder.add_node("inference_node", self._inference_node)
        builder.add_edge(START, "inference_node")
        builder.add_edge("inference_node", END)
        
        self._graph = builder.compile()
        return self._graph
    
    def _get_response(message: str):
        pass
        
