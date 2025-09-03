
# LLM and Agent Orchestration with Workflows

This sample demonstrates how to use Dapr workflows and Dapr Agent workflows to orchestrate LLM calls and agents with tools. You'll learn two different approaches: using raw Dapr workflows with activities, and using Dapr Agents' higher-level workflow abstractions with tasks.

## Prerequisites

Make sure you have completed the setup from the [main README](../README.md):

## What This Example Demonstrates

- **Sequential Task Orchestration**: Chain LLM calls and agent interactions
- **Two Orchestration Patterns**: Raw Dapr workflows vs Dapr Agent workflows
- **Agent Tool Integration**: Agents with validation tools working within workflows
- **Durable Execution**: Workflow state persisted across restarts


### Architecture
```
Workflow Start → get_character (LLM call) → get_line (Agent + Tool call) → Result
```

## Orchestration Pattern 1: Raw Dapr Workflows

### Overview
This approach uses Dapr's native workflow engine with activities. It provides fine-grained control over workflow execution and is ideal when you need direct access to Dapr's workflow primitives.

### Deploy and Run
```bash
diagrid dev run -f dapr-activity.yaml --approve
```

### How It Works
The workflow (`app_activity.py`) demonstrates a sequential pattern:

1. **Activity 1** (`get_character`): Direct OpenAI API call to select a random character
2. **Activity 2** (`get_line`): Uses a Dapr Agent with validation tool to generate a quote

**Key Features:**
- Direct OpenAI client usage in activities
- Agent integration within workflow activities
- Character validation using agent tools
- Manual workflow runtime management

## Orchestration Pattern 2: Dapr Agent Workflows

### Overview
This approach uses Dapr Agents' workflow abstraction with tasks. It provides a higher-level, more declarative way to define workflows.

### Deploy and Run
```bash
diagrid dev run -f dapr-task.yaml --approve
```

### How It Works
The workflow (`app_task.py`) uses the same sequential pattern but with a cleaner abstraction:

1. **Task 1** (`get_character`): LLM task with natural language description
2. **Task 2** (`get_line`): Agent task that incorporates validation logic

**Key Features:**
- Declarative task definitions with descriptions
- Built-in agent integration via `@task(agent=agent)`
- Automatic workflow runtime management
- Simplified error handling and state management

## Key Differences Between Approaches

| Feature | Raw Dapr Workflows | Dapr Agent Workflows |
|---------|-------------------|---------------------|
| **Abstraction Level** | Low-level activities | High-level tasks |
| **LLM Integration** | Manual OpenAI client | Declarative descriptions |
| **Agent Integration** | Manual async calls | Built-in agent parameter |
| **State Management** | Manual state tracking | Automatic persistence |
| **Code Complexity** | More verbose | More concise |

## Monitoring in Catalyst

### Workflow Execution
- Navigate to Catalyst dashboard → Workflows
- View detailed step-by-step execution logs
- Monitor timing and performance differences
