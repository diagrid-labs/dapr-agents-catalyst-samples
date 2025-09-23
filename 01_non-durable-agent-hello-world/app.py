#!/usr/bin/env python3

import asyncio
import logging
import time
import uuid
from typing import List
from pydantic import BaseModel, Field
from dapr_agents import tool, Agent
from dapr_agents.llm.dapr import DaprChatClient
import os

from dapr_agents.memory import ConversationDaprStateMemory
from dotenv import load_dotenv

os.environ.setdefault("DAPR_LLM_COMPONENT_DEFAULT", "openai")

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
    travel_planner = Agent(
        name="TravelBuddy-HelloWorld",
        role="Travel Assistant",
        goal="Help users find flights and remember preferences",
        instructions=["Find flights","Remember preferences","Provide clear info"],
        tools=[search_flights],

        # Dapr conversation api for LLM interactions
        llm = DaprChatClient(),

        # Long-term memory (preferences, past trips, context continuity)
        memory=ConversationDaprStateMemory(
            store_name="memory-state", session_id=f"session-hello-world-{uuid.uuid4().hex[:8]}"
        ),
    )
    try:
        response1 = await travel_planner.run("I love London")
        print(response1)
        response2 = await travel_planner.run("Find me one random flight there")
        print(response2)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

