#!/usr/bin/env python3

import chainlit as cl
import logging
import json
from typing import List
from pydantic import BaseModel, Field
from dapr_agents import tool, DurableAgent, OpenAIChatClient
from dapr_agents.memory import ConversationDaprStateMemory
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)


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
        FlightOption(airline="CloudNine Airways", price=520.25),
        FlightOption(airline="Budget Flyers", price=299.99),
    ]


# Create the DurableAgent instance
travel_planner = DurableAgent(
    name="TravelAssistant",
    role="Travel Assistant",
    goal="Help users find flights and remember preferences",
    instructions=[
        "You are a friendly travel assistant that helps users search for flights.",
        "Use the search_flights tool to find flights to destinations the user asks about.",
        "Remember user preferences and conversation history.",
        "Provide clear flight information including airline names and prices.",
        "Be helpful and engaging in your responses.",
        "If users ask about flights without specifying a destination, ask them where they want to go.",
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


@cl.on_chat_start
async def start():
    """Initialize the chat session."""
    await cl.Message(
        content="✈️ **Welcome to Flight Search Assistant!** ✈️\n\n"
                "I'm your travel assistant and I can help you search for flights to any destination. "
                "Just tell me where you'd like to go and I'll find available flights for you!\n\n"
                "Try asking me something like:\n"
                "- 'Find me flights to Tokyo'\n"
                "- 'I want to go to Paris'\n"
                "- 'Search for flights to New York'"
    ).send()


@cl.on_message
async def main(message: cl.Message):
    """Handle user messages and interact with the DurableAgent."""
    try:
        # Send the user message to the DurableAgent
        response: str = await travel_planner.run(message.content)

        # Parse the response to extract just the content
        try:
            # Try to parse as JSON first
            response_data = json.loads(response)
            if isinstance(response_data, dict) and 'content' in response_data:
                content = response_data['content']
            else:
                content = response
        except (json.JSONDecodeError, TypeError):
            # If it's not JSON, use the response as-is
            content = response

        # Send the agent's response back to ChainLit
        await cl.Message(content=content).send()

    except Exception as e:
        logging.error(f"Error processing message: {e}")
        await cl.Message(
            content=f"❌ I apologize, but I encountered an error while processing your request. "
                    f"Please try again or check if all Dapr components are running properly."
        ).send()
