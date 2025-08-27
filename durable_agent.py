#!/usr/bin/env python3

import asyncio
import logging
from typing import List
from pydantic import BaseModel, Field
from dapr_agents import tool, DurableAgent, OpenAIChatClient
from dapr_agents.memory import ConversationDaprStateMemory
from dotenv import load_dotenv


# Define tool output model
class FlightOption(BaseModel):
    airline: str = Field(description="Airline name")
    price: float = Field(description="Price in USD")


# Define tool input model
class DestinationSchema(BaseModel):
    destination: str = Field(description="Destination city name")


# Define flight search tool
@tool(args_model=DestinationSchema)
def search_flights(destination: str) -> List[FlightOption]:
    """Search for flights to the specified destination."""
    # Mock flight data (would be an external API call in a real app)
    return [
        FlightOption(airline="SkyHighAir", price=450.00),
        FlightOption(airline="GlobalWings", price=375.50),
    ]


async def main():

    load_dotenv()
    logging.basicConfig(level=logging.INFO)

    travel_planner = DurableAgent(
        name="TravelAssistant",
        role="Travel Assistant",
        goal="Help users find flights and remember preferences",
        instructions=[
            "Find flights to destinations",
            "Remember user preferences",
            "Provide clear flight info",
        ],
        tools=[search_flights],
        message_bus_name="message-pubsub",
        state_store_name="execution-state",
        agents_registry_store_name="registry-state",
        memory=ConversationDaprStateMemory(
            store_name="memory-state", session_id="my-unique-session-id"
        ),
        llm=OpenAIChatClient(model="gpt-3.5-turbo"),
    )

    response = await travel_planner.run("Find me flights to paris?")
    print("Travel Planner Agent response1: " + response)
    response = await travel_planner.run("Now to London")
    print("Travel Planner Agent response2: " + response)

if __name__ == "__main__":
    asyncio.run(main())
