#!/usr/bin/env python3
"""
Stateful Augmented LLM Pattern demonstrates:
1. Memory - remembering user preferences
2. Tool use - accessing external data
3. LLM abstraction
4. Durable execution of tools as workflow actions
"""
import asyncio
import logging
import time
import uuid
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
    try:

travel_planner = DurableAgent(
    name="TravelBuddy",
    role="Travel Planner",
    goal="Help users plan trips by finding flights and suggesting hotels",
    instructions=[
        "Understand user travel intent even if input is incomplete",
        "Search for flights and hotels based on context",
        "Adapt recommendations when preferences change",
        "Remember user preferences for future queries",
        "Provide clear and concise information"
    ],
    tools=[search_flights, search_hotels],

    llm=OpenAIChatClient(model="gpt-4o"),

    # PubSub input for real-time interaction
    message_bus_name="message-pubsub",

    # Execution state (workflow progress, retries, failure recovery)
    state_store_name="execution-state",

    # Long-term memory (preferences, past trips, context continuity)
    memory=ConversationDaprStateMemory(
        store_name="memory-state", session_id="my-session"
    )
)







        # start REST
        travel_planner.as_service(port=8001)
        await travel_planner.start()
        print("Travel Planner Agent is running")

    except Exception as e:
        print(f"Error starting service: {e}")

if __name__ == "__main__":
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
