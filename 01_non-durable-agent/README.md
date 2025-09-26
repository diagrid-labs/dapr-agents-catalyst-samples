# Non-Durable Agent

This is the simplest example of a non-durable agent and serves as the perfect starting point for understanding Dapr Agents. Running this example demonstrates the core concepts of agents: tool execution, conversation memory, and Dapr chat client integration.

## Prerequisites

Make sure you have completed the setup from the [main README](../README.md):

## What This Example Demonstrates

- **Basic Non-Durable Agent**: Simple agent setup with essential configuration
- **Conversation Memory**: Agent conversation history persisted using Dapr state store
- **Dapr Chat Client**: LLM interactions through Dapr conversation API
- **Tool Execution**: Agent uses flight search tool to find travel options
- **Session Management**: Unique session ID for conversation continuity

### Architecture

This example demonstrates a simple conversation pattern where the agent maintains context across multiple interactions:

```
Agent Start → User: "I love London" → Agent Response → User: "Find me one random flight there" → Agent uses tool → Flight Results
```

**Agent Overview:**
When you run this example, the agent processes two sequential requests:
1. User expresses preference for London
2. User asks for a random flight to London
3. Agent uses the `search_flights` tool to find options
4. Agent returns flight information while maintaining conversation context

## Deploy and Run

Deploy the agent:

```bash
diagrid dev run -f dapr.yaml --approve
```

The agent will automatically:
1. Initialize with the travel assistant role
2. Process the first request: "I love London"
3. Process the second request: "Find me one random flight there"
4. Execute tool call to `search_flights` for London
5. Return flight options for London
6. Persist conversation history in Dapr state store

## Monitor Execution

After running the deployment command, you can monitor the execution:

1. Check the console output for agent responses
2. Monitor the conversation flow between the two requests
3. Observe the tool execution for flight search

### State Management
- **Memory State**: Conversation history stored in Redis state store (`memory-state`)
- **Session Management**: Unique session ID for conversation continuity
- **LLM Integration**: OpenAI model via Dapr conversation API

## Expected Output

The agent will process both requests and return flight options for London:

```
Travel Assistant response to "I love London": [Agent acknowledges preference]

Travel Assistant response to "Find me one random flight there": I found flight options for London:

- SkyHighAir: $450.00
- GlobalWings: $375.50
```

## Next Steps

Once you've successfully run this example:

Ready to explore durable agents with workflows? Check out the [02_durable-agent-headless](../02_durable-agent-headless/README.md) example to learn about durable agents with REST API and PubSub triggering.