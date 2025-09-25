#!/usr/bin/env python3

import chainlit as cl
import logging
import json
import uuid
from typing import List
from pydantic import BaseModel, Field
from dapr_agents import tool, DurableAgent, OpenAIChatClient
from dapr_agents.memory import ConversationDaprStateMemory
from dotenv import load_dotenv

from dapr_agents.llm.dapr import DaprChatClient
import os

load_dotenv()
logging.basicConfig(level=logging.INFO)

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

@cl.on_chat_start
async def start():
    """Initialize the chat session with a unique session ID."""
    
    # Generate a unique session ID for this chat session
    session_id = f"session-{uuid.uuid4().hex[:8]}"
    
    # Create the DurableAgent instance with the session-specific memory
    travel_planner = DurableAgent(
        name="TravelAssistant-Chat",
        role="Travel Assistant",
        goal="Help users find flights and remember preferences",
        instructions=[
            "You are a travel assistant that helps users search for flights.",
            "Use the search_flights tool to find flights to destinations.",
            "Provide clear flight information with airline names and prices.",
        ],
        tools=[search_flights],
        llm = DaprChatClient(),
        message_bus_name="message-pubsub",
        state_store_name="statestore",
        state_key="execution-chat",

        agents_registry_store_name="registry-state",
        memory=ConversationDaprStateMemory(
            store_name="memory-state", session_id=session_id
        ),
    )
    
    # Store the agent in the user session
    cl.user_session.set("travel_planner", travel_planner)
    
    await cl.Message(
        content="✈️ **Flight Search Assistant**\n\n"
                "Tell me where you'd like to go and I'll find flights for you!\n\n"
                "Example: 'Find flights to Tokyo'\n\n"
                f"💡 *Session ID: {session_id}*"
    ).send()

@cl.on_message
async def main(message: cl.Message):
    """Handle user messages and interact with the DurableAgent."""
    try:
        # Get the session-specific travel_planner
        travel_planner = cl.user_session.get("travel_planner")
        
        if not travel_planner:
            await cl.Message(
                content="❌ Session error. Please refresh the page to start a new session."
            ).send()
            return
            
        response: str = await travel_planner.run(message.content)

        # Parse the response to extract just the content
        try:
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
        
        logging.info("Message processed successfully")

    except Exception as e:
        logging.error(f"Error processing message: {e}")
        await cl.Message(
            content=f"❌ I apologize, but I encountered an error while processing your request. "
                    f"Please try again or refresh the page to start a new session.\n\n"
                    f"Error: {str(e)}"
        ).send()
