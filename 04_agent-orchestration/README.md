
# LLM and Agent Orchestration with Workflows

This sample demonstrates how to use Dapr workflows to orchestrate LLM calls and agents with tools. It shows how to integrate the Dapr Conversation API with Dapr Agents in a workflow pattern.

## Prerequisites

Make sure you have completed the setup from the [main README](../README.md):

## What This Example Demonstrates

- **Sequential Activity Orchestration**: Chain Dapr Conversation API calls and agent interactions
- **Dapr Conversation API Integration**: Using conversation components for LLM calls
- **Agent Tool Integration**: Agents with validation tools working within workflows
- **Durable Execution**: Workflow state persisted across restarts


### Architecture
```
Workflow Start → get_character (Dapr Conversation API) → get_line (Agent + Tool call) → Result
```

## Implementation Overview

### Deploy and Run
```bash
cd 04_agent-orchestration
dapr run -f dapr.yaml
```

### How It Works
The workflow (`app.py`) demonstrates a sequential pattern:

1. **Activity 1** (`get_character`): Uses Dapr Conversation API to select a random LOTR character
2. **Activity 2** (`get_line`): Uses a Dapr Agent with validation tool to generate a famous quote

**Key Features:**
- **Dapr Conversation API**: Direct integration with OpenAI models via Dapr components
- **Agent Integration**: DaprChatClient for agent LLM interactions
- **Tool Validation**: Character validation using agent tools
- **Memory Persistence**: Agent memory stored in Dapr state store
- **Workflow Orchestration**: Durable execution with state persistence

### Code Structure
```python
# Activity 1: Character generation using Conversation API
@wfr.activity(name="step1")
def get_character(ctx):
    with DaprClient() as d:
        response = d.converse_alpha2(name='openai-mini', inputs=inputs)
        return response.outputs[0].choices[0].message.content

# Activity 2: Quote generation using Dapr Agent
@wfr.activity(name="step2")
def get_line(ctx, character: str):
    response = asyncio.run(agent.run(f"What is a famous line by {character}"))
    return response.content
```

## Components Used

- **openai-mini**: Conversation component for character generation
- **memory-state**: State store for agent conversation memory
- **execution-state**: State store for workflow execution state

## Monitoring in Catalyst

### Workflow Execution
- Navigate to Catalyst dashboard → Workflows
- View detailed step-by-step execution logs
- Monitor conversation API calls and agent interactions
