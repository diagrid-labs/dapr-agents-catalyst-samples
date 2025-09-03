import time

from dapr_agents.workflow import WorkflowApp, workflow, task
from dapr.ext.workflow import DaprWorkflowContext
from dotenv import load_dotenv
import logging
from dapr_agents import tool, Agent, OpenAIChatClient
from dapr_agents.memory import ConversationDaprStateMemory

@tool
def validate_character(character: str) -> bool:
    """Validates if an agent is valid or blacklisted"""
    return True

agent = Agent(
    name="Character Agent",
    role="Famous Character Assistant",
    goal="Provide famous character lines after validation",
    instructions=["For every character, first make sure is valid and not blacklisted. If not then return a famous line "],
    tools=[validate_character]
)

# Define Workflow logic
@workflow(name="task_chain_workflow")
def task_chain_workflow(ctx: DaprWorkflowContext):
    result1 = yield ctx.call_activity(get_character)
    result2 = yield ctx.call_activity(get_line, input={"character": result1})
    return result2

@task(description="""Pick a random character from The Lord of the Rings and respond with the character's name only""")
def get_character() -> str:
    pass

@task(agent=agent, description="What is a famous line by {character}. Return only the quote text as a string.")
def get_line(character: str) -> str:
    pass

if __name__ == "__main__":
    load_dotenv()
    logging.basicConfig(level=logging.INFO)

    wfapp = WorkflowApp()

    results = wfapp.run_and_monitor_workflow_sync(task_chain_workflow)
    print(f"Famous Line: {results}")
    
    # Keep the app running
    print("Workflow completed. Keeping app alive...")
    try:
        while True:
            time.sleep(60)  # Sleep for 60 seconds at a time
    except KeyboardInterrupt:
        print("Shutting down...")