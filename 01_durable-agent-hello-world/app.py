#!/usr/bin/env python3

import asyncio
import logging
import uuid
import time
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
    time.sleep(10)

    return [
        FlightOption(airline="SkyHighAir", price=450.00),
        FlightOption(airline="GlobalWings", price=375.50),
    ]

async def main():

    travel_planner = DurableAgent(
        name="TravelBuddy-HelloWorld",
        role="Travel Assistant",
        goal="Help users find flights and remember preferences",
        instructions=["Find flights","Remember preferences","Provide clear info"],
        tools=[search_flights],
        llm=OpenAIChatClient(model="gpt-4o"),

        message_bus_name="message-pubsub",
        state_store_name="execution-state",
        state_key="execution-hello-world",
        memory=ConversationDaprStateMemory(
            store_name="memory-state", session_id=f"session-headless-{uuid.uuid4().hex[:8]}"
        ),
        agents_registry_store_name="registry-state",
    )

    response = await travel_planner.run("Find me flights to London and Paris?")
    print("Travel Planner Agent response1: " + response)

if __name__ == "__main__":
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

