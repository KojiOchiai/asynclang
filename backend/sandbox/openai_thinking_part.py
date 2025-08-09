import asyncio

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModel, OpenAIResponsesModelSettings

model = OpenAIResponsesModel("o3")
settings = OpenAIResponsesModelSettings(
    openai_reasoning_effort="low",
    openai_reasoning_summary="detailed",
)
agent = Agent(model, model_settings=settings)


async def main():
    async with agent:
        result = await agent.run("I am Alice. What time is it?")
    for message in result.all_messages():
        print(message)


if __name__ == "__main__":
    asyncio.run(main())
