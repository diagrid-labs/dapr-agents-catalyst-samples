# Customer Support System

A complete AI-powered customer support system built with Dapr, demonstrating advanced workflow orchestration with three specialized agents for automated ticket processing.

## Overview

This system demonstrates a complete customer support workflow that:

1. **Receives support tickets** with customer ID and issue description
2. **Orchestrates three specialized agents** through a Dapr workflow:
   - **Triage Agent**: Validates customer entitlement and gathers system information
   - **Expert Agent**: Analyzes issues using knowledge base and proposes solutions  
   - **Notification Agent**: Creates professional customer communications
3. **Handles external approvals** from support staff before notifying customers
4. **Uses multiple Dapr APIs**: Workflow, State Store, PubSub, and Conversation APIs

## Quick Start

### 1. Setup Sample Data
```bash
# Load sample customers and system data
dapr run --app-id data-setup --resources-path ./resources -- python setup_sample_data.py
```

### 2. Start the System
```bash
# Start the customer support system
dapr run -f .
```

### 3. Verify System Health
```bash
# Check if system is running
curl "http://localhost:8000/health"

# Verify sample data is loaded
curl "http://localhost:8000/health/data"
```

## Usage

### Create Support Ticket
```bash
curl -X POST "http://localhost:8000/support/ticket" \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_id": "TICK001",
    "customer_id": "CUST001", 
    "description": "Dapr sidecar is not connecting to my application"
  }'
```

### Check Ticket Status
```bash
curl "http://localhost:8000/support/status/TICK001"
```

### Approve Solution
```bash
curl -X POST "http://localhost:8000/support/approve/TICK001" \
  -H "Content-Type: application/json" \
  -d '{
    "approved": true,
    "final_solution": "Update your Dapr configuration to include the correct app-port setting",
    "support_notes": "Verified the configuration issue and provided the correct settings"
  }'
```

### Monitor Ticket Progress
```bash
# Use the monitoring script
./monitor_ticket.sh TICK001

# Or check status manually
curl "http://localhost:8000/support/status/TICK001"
```

## Data Inspection

### Check Customer Data
```bash
curl "http://localhost:3500/v1.0/state/customer-state/CUST001"
```

### Check System Data
```bash
curl "http://localhost:3500/v1.0/state/system-state/CUST001"
```

### Check Analysis Results
```bash
curl "http://localhost:3500/v1.0/state/analysis-state/analysis-TICK001"
```

## Automated Testing

### Run Complete Workflow Test
```bash
python test_workflow.py
```

**What the test does:**
1. Creates a test support ticket (TEST001)
2. Runs the complete workflow (triage → expert analysis → approval → notification)
3. Shows progress and final results
4. Displays the generated customer notification

## Sample Data

The system includes sample customers with different entitlement levels:

- **CUST001** (Acme Corporation): Enterprise plan with full support
- **CUST002** (TechStart Inc): Professional plan with support  
- **CUST003** (Basic User LLC): Basic plan without support entitlement

## Configuration

### Dapr Components Required

The system uses these Dapr components (defined in `./resources/`):

- **State Stores**: 
  - `customer-state`: Customer information and entitlement data
  - `system-state`: System configuration data (Dapr versions, cloud info, applications)
  - `analysis-state`: Expert analysis results and technical solutions
  - `execution-state`: Workflow execution state (internal)
- **PubSub**: 
  - `support-pubsub`: Solution notifications
  - `message-pubsub`: General messaging
- **Conversation API**: 
  - `customer-notification-llm`: AI-generated customer notifications
  - `openai`: OpenAI integration for agents

## API Endpoints

### POST /support/ticket
Create a new support ticket.

**Request**:
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
Approve a solution for a ticket.

**Request**:
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

## Workflow States

The ticket progresses through these states:
- `workflow_started` - Initial ticket creation
- `RUNNING` - Workflow is executing activities
- `WAITING` - Waiting for external approval (24h timeout)
- `COMPLETED` - Workflow finished successfully
- `FAILED` - Workflow encountered an error
