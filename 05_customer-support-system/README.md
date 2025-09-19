# Customer Support System

A complete AI-powered customer support system built with Dapr, demonstrating advanced workflow orchestration with three specialized agents for automated ticket processing. This example showcases the integration of multiple Dapr APIs including Workflow, State Store, PubSub, and Conversation APIs.

## Overview

This system demonstrates a complete customer support workflow that:

1. **Receives support tickets** with customer ID and issue description
2. **Orchestrates three specialized agents** through a Dapr workflow:
   - **Triage Agent**: Validates customer entitlement and gathers system information
   - **Expert Agent**: Analyzes issues using knowledge base and proposes solutions  
   - **Notification Agent**: Creates professional customer communications
3. **Handles external approvals** from support staff before notifying customers
4. **Uses multiple Dapr APIs**: Workflow, State Store, PubSub, and Conversation APIs

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Support       │    │    Dapr          │    │   External      │
│   Ticket        │───▶│    Workflow      │◀──▶│   Support       │
│   (REST API)    │    │    Runtime       │    │   Team          │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                    ┌──────────────────────────────────┐
                    │            Activities            │
                    │                                  │
                    │  ┌─────────────────────────────┐ │
                    │  │      Triage Activity        │ │
                    │  │  ┌─────────────────────────┐│ │
                    │  │  │    Triage Agent         ││ │
                    │  │  │  - Lookup customer      ││ │ ◀── State Store (Customer Data)
                    │  │  │  - Check entitlement    ││ │ ◀── State Store (System Info)
                    │  │  └─────────────────────────┘│ │
                    │  └─────────────────────────────┘ │
                    │                                  │
                    │  ┌─────────────────────────────┐ │
                    │  │    Expert Analysis Activity │ │
                    │  │  ┌─────────────────────────┐│ │
                    │  │  │    Expert Agent         ││ │ ◀── Knowledge Base (MCP)
                    │  │  │  - Deep analysis        ││ │     (Multiple Queries)
                    │  │  │  - Multiple KB queries  ││ │
                    │  │  └─────────────────────────┘│ │
                    │  │  Activity Level Operations:  │ │
                    │  │  - Store analysis result     │ │ ──▶ State Store (Analysis)
                    │  │  - Publish notification      │ │ ──▶ PubSub (Notifications)
                    │  └─────────────────────────────┘ │
                    │                                  │
                    │  ┌─────────────────────────────┐ │
                    │  │   Notification Activity     │ │
                    │  │  ┌─────────────────────────┐│ │
                    │  │  │  Notification Function  ││ │ ◀── Conversation API
                    │  │  │  - Create message       ││ │
                    │  │  └─────────────────────────┘│ │
                    │  └─────────────────────────────┘ │
                    └──────────────────────────────────┘
```

## Features

- **🔄 Complete Workflow Orchestration**: Uses Dapr Workflow to coordinate three specialized agents
- **👤 Customer Validation**: Automatic entitlement checking with customer lookup and system information gathering
- **🧠 Expert Analysis**: AI-powered deep technical analysis with multiple knowledge base queries
- **⏳ External Event Handling**: Waits for support team approval before proceeding with customer notification
- **🔗 Multi-API Integration**: Demonstrates State Store, PubSub, Workflow, and Conversation APIs
- **💬 AI-Generated Communications**: Professional customer notifications using Dapr Conversation API
- **📊 Comprehensive Logging**: Full audit trail of all operations and agent interactions
- **🌐 REST API**: Easy integration with external systems and support tools
- **🏥 Health Checks**: Built-in endpoints to verify system and data health
- **🔧 Production Ready**: Complete error handling, fallback mechanisms, and monitoring

## Prerequisites

- Python 3.8+
- Dapr CLI 1.12+
- OpenAI API key
- Redis (for state store)

## Installation

1. **Clone the repository and navigate to the project**:
   ```bash
   cd 05_customer-support-system
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp env.template .env
   # Edit .env and add your OpenAI API key
   ```

4. **Set up sample data** (one-time setup):
   
   Before running the customer support system, you need to populate the state stores with sample customer and system data.
   
   **Run the setup script once** - it will start Dapr, populate the data, and shut down:
   
   ```bash
   # Run the one-time setup script through Dapr
   dapr run --app-id data-setup --resources-path ../resources -- python setup_sample_data.py
   ```
   
   This will:
   1. Start Dapr with the required state store components
   2. Populate the customer and system data
   3. Complete and shut down automatically
   
   This script will create:
   - **Sample customers** with different support entitlement levels (CUST001, CUST002, CUST003)
   - **System information** for each customer (Dapr versions, cloud providers, applications)
   - **State store data** required for the triage and expert agents to function properly
   
   **Note**: The script uses Dapr's state store APIs to populate the `customer-state` and `system-state` stores with test data.

## Usage

### Running the System

**After completing the one-time setup above**, start the customer support system:

1. **Start the customer support system**:
   ```bash
   dapr run -f .
   ```

2. **The system will start on port 8000** with the following endpoints:
   - `POST /support/ticket` - Create a new support ticket
   - `POST /support/approve/{ticket_id}` - Approve a solution  
   - `GET /support/status/{ticket_id}` - Get ticket status
   - `GET /health` - Basic health check
   - `GET /health/data` - Verify sample data is loaded

### Creating a Support Ticket

```bash
curl -X POST "http://localhost:8000/support/ticket" \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_id": "TICK0012",
    "customer_id": "CUST001", 
    "description": "Dapr sidecar is not connecting to my application"
  }'
```

### Approving a Solution

After the expert analysis is complete, approve the solution:

```bash
curl -X POST "http://localhost:8000/support/approve/TICK001" \
  -H "Content-Type: application/json" \
  -d '{
    "approved": true,
    "final_solution": "Update your Dapr configuration to include the correct app-port setting",
    "support_notes": "Verified the configuration issue and provided the correct settings"
  }'
```

### Checking Ticket Status

```bash
curl "http://localhost:8000/support/status/TICK001"
```

### Verifying System Health

Check if the system is running:
```bash
curl "http://localhost:8000/health"
```

Verify sample data is loaded:
```bash
curl "http://localhost:8000/health/data"
```

### Success Indicators

When everything is working correctly, you should see:

1. **Startup Logs**: All agents initialized with tools registered
2. **Triage Agent**: Successfully finds customer CUST001 with entitlement
3. **Expert Agent**: Makes multiple parallel knowledge base queries (3+ queries)
4. **Storage Operations**: Analysis results stored successfully
5. **PubSub Operations**: Solution notifications published successfully  
6. **External Events**: Approval workflow responds correctly
7. **Conversation API**: Customer notifications generated (after API fix)
8. **Workflow Completion**: Full end-to-end execution with "COMPLETED" status

## Workflow Details

### 1. Triage Activity
- **Agent**: Support Triage Agent
- **Tools**: `lookup_customer`, `lookup_system_info`
- **Purpose**: Validates customer entitlement and gathers system context
- **Output**: Comprehensive triage analysis with customer and system details

### 2. Expert Analysis Activity  
- **Agent**: Dapr Expert Agent
  - **Tools**: `query_knowledge_base` (only)
  - **Purpose**: Performs deep technical analysis with **multiple parallel knowledge base queries**
  - **Focus**: Exhaustive research across different aspects (connectivity, configuration, compatibility)
  - **Behavior**: Makes 3+ simultaneous knowledge base queries for comprehensive analysis
- **Activity Operations** (after agent completes):
  - **Storage**: Stores analysis results in Dapr state store (`analysis-state`)
  - **Publishing**: Publishes solution notification via Dapr PubSub (`support-pubsub`)
- **Output**: Detailed technical analysis with step-by-step resolution instructions

### 3. External Event Wait
- **Event**: `solution_approved`
- **Timeout**: 24 hours
- **Purpose**: Allows support team to review and modify the proposed solution

### 4. Customer Notification Activity
- **Function**: `create_customer_notification()` 
- **API**: Dapr Conversation API (`customer-notification-llm` component)
- **Purpose**: Creates professional customer update messages using AI
- **Features**: Context-aware, personalized notifications with ticket details
- **Output**: AI-generated customer notification with resolution summary

## Sample Data

The system includes sample customers with different entitlement levels:

- **CUST001** (Acme Corporation): Enterprise plan with full support
- **CUST002** (TechStart Inc): Professional plan with support  
- **CUST003** (Basic User LLC): Basic plan without support entitlement

Each customer has associated system information including Dapr version, cloud provider, and deployed applications.

## Configuration

### Dapr Components Required

The system uses these Dapr components (defined in `../resources/`):

- **State Stores**: 
  - `customer-state`: Customer information and entitlement data
  - `system-state`: System configuration data (Dapr versions, cloud info, applications)
  - `analysis-state`: Expert analysis results and technical solutions
  - `execution-state`: Workflow execution state and progress
  - `memory-state`: Agent conversation memory and context
  - `registry-state`: Agent registry and metadata
  
- **PubSub**: 
  - `support-pubsub`: Solution ready notifications for support team
  - `message-pubsub`: Agent communication and workflow events
  
- **Conversation**: 
  - `customer-notification-llm`: AI-powered customer message generation

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `DAPR_HTTP_PORT`: Dapr HTTP port (default: 3500)  
- `DAPR_GRPC_PORT`: Dapr gRPC port (default: 50001)
- `LOG_LEVEL`: Logging level (default: INFO)

## API Reference

### POST /support/ticket

Create a new support ticket and start the workflow.

**Request Body**:
```json
{
  "ticket_id": "string",
  "customer_id": "string", 
  "description": "string"
}
```

**Response**:
```json
{
  "instance_id": "string",
  "ticket_id": "string",
  "status": "workflow_started"
}
```

### POST /support/approve/{ticket_id}

Approve or modify the proposed solution.

**Request Body**:
```json
{
  "approved": true,
  "final_solution": "string",
  "support_notes": "string"  
}
```

**Response**:
```json
{
  "status": "approval_sent",
  "ticket_id": "string",
  "instance_id": "string"
}
```

### GET /support/status/{ticket_id}

Get the current status of a support ticket.

**Response**:
```json
{
  "ticket_id": "string",
  "instance_id": "string", 
  "status": "string",
  "output": "object"
}
```

## Monitoring and Debugging

### Logs

The system provides comprehensive logging at each stage:
- Workflow start/completion
- Agent execution details
- API call results
- Error conditions

### Dapr Dashboard

Use the Dapr dashboard to monitor workflow instances:
```bash
dapr dashboard
```

Navigate to the Workflows section to see active and completed workflows.

### State Store Inspection

You can inspect the state stores directly:
```bash
# Check customer data
dapr invoke --app-id customer-support-system --method /dapr/state/customer-state/CUST001

# Check analysis results  
dapr invoke --app-id customer-support-system --method /dapr/state/analysis-state/analysis-TICK001
```

## Troubleshooting

### Common Issues

1. **"Customer not found" error**:
   - **First**: Ensure sample data is loaded by running: `python setup_sample_data.py`
   - **Verify**: Check that the script completed successfully (should show "Sample data setup completed successfully!")
   - **Check**: Use valid customer IDs from the sample data: `CUST001`, `CUST002`, or `CUST003`

2. **OpenAI API errors**:
   - Verify your API key is set in `.env`
   - Check your OpenAI account has sufficient credits

3. **Workflow timeout**:
   - The workflow waits 24 hours for approval by default
   - Use the approve endpoint to continue the workflow

4. **Dapr connection errors**:
   - **Setup script fails**: Run the setup through Dapr as shown in the installation steps:
     ```bash
     dapr run --app-id data-setup --resources-path ../resources -- python setup_sample_data.py
     ```
   - **Main application fails**: Ensure the one-time setup was completed successfully first
   - **Component errors**: Check Dapr components are configured in `../resources/`

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
dapr run -f .
```

## Extending the System

### Adding New Agents

1. Create agent tools using the `@tool` decorator
2. Define the agent with appropriate instructions
3. Add a new activity function
4. Update the workflow to call the new activity

### Custom Knowledge Base

Replace the `query_knowledge_base` tool with your MCP implementation:
```python
@tool
def query_knowledge_base(issue_description: str, system_info: str) -> Dict[str, Any]:
    # Your MCP client implementation here
    return mcp_client.query(issue_description, system_info)
```

### Additional Integrations

- **Email notifications**: Add SMTP binding for email alerts
- **Slack integration**: Use Slack binding for team notifications  
- **Database storage**: Replace state store with SQL database binding
- **Monitoring**: Add observability with Application Insights binding

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.
