from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph.state import CompiledStateGraph
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage, convert_to_openai_messages

from typing import Optional


from agent.core.config import settings
from agent.core.prompts import prompts
from agent.core.schemas import GraphState, Message
from agent.utils.graph import dump_messages, prepare_messages
from agent.files.schemas import Transactions


class Agent:

    def __init__(self):
        self._model = ChatGoogleGenerativeAI(
            model=settings.model_name,
            api_key=settings.gemini_api_key,
        )
        self._graph: Optional[CompiledStateGraph] = None

    async def _inference_node(self, state: GraphState) -> GraphState:

        messages = prepare_messages(
            messages=state.messages,
            llm=self._model,
            system_prompt=prompts.lara_system_prompt,
        )

        response = await self._model.ainvoke(
            dump_messages(messages=messages),
        )

        return {"messages": [response]}

    def __process_messages(self, messages: list[BaseMessage]) -> list[Message]:
        openai_style_messages = convert_to_openai_messages(messages)
        return [
            Message(**message)
            for message in openai_style_messages
            if message["role"] in ["assistant", "user"] and message["content"]
        ]

    def _build_graph(self) -> Optional[CompiledStateGraph]:

        if self._graph is not None:
            return self._graph

        builder = StateGraph(GraphState)
        builder.add_node("inference_node", self._inference_node)
        builder.add_edge(START, "inference_node")
        builder.add_edge("inference_node", END)

        self._graph = builder.compile()
        return self._graph

    async def get_response(self, messages: list[Message]):
        if self._graph is None:
            self._graph = self._build_graph()

        response = await self._graph.ainvoke(
            {"messages": dump_messages(messages=messages)}
        )
        response = self.__process_messages(response["messages"])
        return response

    async def analyze_images(self, messages: list[Message]):
        if self._graph is None:
            self._graph = self._build_graph()

        messages = prepare_messages(
            messages=messages,
            llm=self._model,
            system_prompt=prompts.lara_system_prompt,
        )

        response = await self._model.with_structured_output(Transactions).ainvoke(
            dump_messages(messages=messages),
        )

        return response


agent = Agent()
