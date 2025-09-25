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

load_dotenv()
os.environ.setdefault("DAPR_LLM_COMPONENT_DEFAULT", "openai")

# Initialize Workflow Instance
wfr = wf.WorkflowRuntime()

@tool
def validate_character(character: str) -> bool:
    """Validates if a character is valid or blacklisted"""
    print(f"Validating character: {character}")
    return False

# Create agent instance once at module level
agent = Agent(
    name="Character Agent",
    role="Famous Character Assistant",
    goal="Provide famous character lines after validation",
    instructions=["For every character, first verify it is valid and not blacklisted, "
                  "If valid, then return a famous line, otherwise return NONE"
                  "avoiding repetition from previous lines"],
    tools=[validate_character],

    # Use Dapr conversation api
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
@wfr.activity(name="get_character_conv_api")
def get_character(ctx):
    with DaprClient() as d:
        text_input = "Pick a random character from The Lord of the Rings, and respond with the character name only"

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

        response = d.converse_alpha2(name='openai-mini', temperature=1.0, inputs=inputs)
        character = response.outputs[0].choices[0].message.content

    print(f"Character: {character}")
    return character

# Activity 2
@wfr.activity(name="get_line_agent")
def get_line(ctx, character: str):
    response = asyncio.run(agent.run(f"What is a famous line by {character}"))

    print(f"Line: {response.content}")
    return response.content

if __name__ == "__main__":
    wfr.start()
    sleep(5)  # wait for workflow runtime to start

    wf_client = wf.DaprWorkflowClient()
    instance_id = wf_client.schedule_new_workflow(workflow=task_chain_workflow)
    print(f"Workflow started. Instance ID: {instance_id}")
    state = wf_client.wait_for_workflow_completion(instance_id)
    print(f"Workflow completed with result: {state.serialized_output}")

    wfr.shutdown()
