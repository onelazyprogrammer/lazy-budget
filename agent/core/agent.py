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

    def initialize(self, checkpointer) -> None:
        builder = StateGraph(GraphState)
        builder.add_node("inference_node", self._inference_node)
        builder.add_edge(START, "inference_node")
        builder.add_edge("inference_node", END)
        self._graph = builder.compile(checkpointer=checkpointer)

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

    async def get_response(self, thread_id: str, user_message: Message) -> list[Message]:
        config = {"configurable": {"thread_id": thread_id}}
        response = await self._graph.ainvoke(
            {"messages": dump_messages(messages=[user_message])},
            config=config,
        )
        return self.__process_messages(response["messages"])

    async def get_history(self, thread_id: str) -> list[Message]:
        config = {"configurable": {"thread_id": thread_id}}
        state = await self._graph.aget_state(config)
        if state is None or not state.values:
            return []
        return self.__process_messages(state.values.get("messages", []))

    async def analyze_images(self, messages: list[Message]):
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
