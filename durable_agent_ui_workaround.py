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


def create_travel_agent(session_id: str) -> DurableAgent:
    """Create a fresh DurableAgent for a specific session."""
    return DurableAgent(
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
            store_name="memory-state", session_id=session_id
        ),
        llm=OpenAIChatClient(model="gpt-3.5-turbo"),
    )


@cl.on_chat_start
async def start():
    """Initialize the chat session with a unique session ID."""
    # Generate a unique session ID for this chat session
    session_id = f"session-{uuid.uuid4().hex[:8]}"
    
    # Store only the session_id - we'll create fresh agents for each message
    cl.user_session.set("session_id", session_id)
    
    await cl.Message(
        content="✈️ **Welcome to Flight Search Assistant!** ✈️\n\n"
        "I'm your travel assistant and I can help you search for flights to any destination. "
        "Just tell me where you'd like to go and I'll find available flights for you!\n\n"
        "Try asking me something like:\n"
        "- 'Find me flights to Tokyo'\n"
        "- 'I want to go to Paris'\n"
        "- 'Search for flights to New York'\n\n"
        f"💡 *Session ID: {session_id}*\n"
    ).send()


@cl.on_message
async def main(message: cl.Message):
    """Handle user messages by creating a fresh DurableAgent for each message."""
    try:
        # Get the persistent session ID
        session_id = cl.user_session.get("session_id")
        
        if not session_id:
            await cl.Message(
                content="❌ Session error. Please refresh the page to start a new session."
            ).send()
            return
        
        # Create a FRESH DurableAgent instance for this message
        # The memory will persist because we use the same session_id
        travel_planner = create_travel_agent(session_id)
        
        logging.info(f"Created fresh DurableAgent for session {session_id}")
        
        # Send the user message to the fresh DurableAgent
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
        
        logging.info(f"Message processed successfully for session {session_id}")
        
    except Exception as e:
        logging.error(f"Error processing message: {e}")
        await cl.Message(
            content=f"❌ I apologize, but I encountered an error while processing your request. "
            f"Please try again or refresh the page to start a new session.\n\n"
            f"Error: {str(e)}"
        ).send()


@cl.on_chat_end
async def end():
    """Clean up when chat session ends."""
    session_id = cl.user_session.get("session_id")
    if session_id:
        logging.info(f"Chat session {session_id} ended")
