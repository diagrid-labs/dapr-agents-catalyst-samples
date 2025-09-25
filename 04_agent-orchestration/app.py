import dapr.ext.workflow as wf
from dotenv import load_dotenv
from time import sleep
import asyncio
from dapr_agents import tool, Agent
import os
from dapr_agents.memory import ConversationDaprStateMemory
from dapr.clients import DaprClient
from dapr.clients.grpc.conversation import ConversationInputAlpha2, ConversationMessage, ConversationMessageContent, ConversationMessageOfUser
from dapr_agents.llm.dapr import DaprChatClient

import logging

# Load environment variables
load_dotenv()

os.environ.setdefault("DAPR_LLM_COMPONENT_DEFAULT", "openai")

# Initialize Workflow Instance
wfr = wf.WorkflowRuntime()

@tool
def validate_character(character: str) -> bool:
    """Validates if an agent is valid or blacklisted"""
    return True

# Create agent instance once at module level
agent = Agent(
    name="Character Agent",
    role="Famous Character Assistant",
    goal="Provide famous character lines after validation",
    instructions=["For every character, first make sure is valid and not blacklisted. If not then return a famous line "],
    tools=[validate_character],
    llm=DaprChatClient(),

    # Long-term memory (preferences, past trips, context continuity)
    memory=ConversationDaprStateMemory(
        store_name="memory-state", session_id="session-agent-orchestration"
    ),
)

# Define Workflow logic
@wfr.workflow(name="task_chain_workflow")
def task_chain_workflow(ctx: wf.DaprWorkflowContext):
    result1 = yield ctx.call_activity(get_character)
    result2 = yield ctx.call_activity(get_line, input=result1)
    return result2

# Activity 1
@wfr.activity(name="get_character_conversation_api")
def get_character(ctx):
    with DaprClient() as d:
        text_input = "Pick a random character from The Lord of the Rings, until you find a valid character, and respond with the character name only"

        inputs = [
            ConversationInputAlpha2(
                messages=[
                    ConversationMessage(
                        of_user=ConversationMessageOfUser(
                            content=[ConversationMessageContent(text=text_input)]
                        )
                    )
                ],
                scrub_pii=True
            ),
        ]

        response = d.converse_alpha2(name='openai-mini', inputs=inputs)
        character = response.outputs[0].choices[0].message.content

    print(f"Character: {character}")
    return character

# Activity 2
@wfr.activity(name="get_line_agent")
def get_line(ctx, character: str):
    response = asyncio.run(agent.run(f"What is a famous line by {character}"))

    # Extract the content from the response message
    line = response.content if hasattr(response, 'content') else str(response)

    print(f"Line: {line}")
    return line

if __name__ == "__main__":
    wfr.start()
    sleep(5)  # wait for workflow runtime to start

    wf_client = wf.DaprWorkflowClient()
    instance_id = wf_client.schedule_new_workflow(workflow=task_chain_workflow)
    print(f"Workflow started. Instance ID: {instance_id}")
    state = wf_client.wait_for_workflow_completion(instance_id)
    print(f"Workflow completed! Status: {state.runtime_status}")

    wfr.shutdown()
