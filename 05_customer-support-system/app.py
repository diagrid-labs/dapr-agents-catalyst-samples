#!/usr/bin/env python3

from fastapi import FastAPI
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager
from dapr.ext.workflow.workflow_runtime import WorkflowRuntime
from dapr.ext.workflow import DaprWorkflowClient
from datetime import timedelta
import dapr.ext.workflow as wf
from dapr.clients import DaprClient
from dapr.clients.grpc.conversation import ConversationInputAlpha2, ConversationMessage, ConversationMessageContent, ConversationMessageOfUser
from dapr_agents import tool, Agent, OpenAIChatClient

import os, json, time, asyncio
from dataclasses import dataclass
from typing import Dict, Any, Optional
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
logging.basicConfig(level=logging.INFO)

# Initialize Workflow Runtime
wfr = WorkflowRuntime()

# === Data Models ===
@dataclass
class SupportTicket:
    ticket_id: str
    customer_id: str
    description: str
    
    @staticmethod
    def from_dict(data):
        return SupportTicket(**data)

@dataclass
class CustomerInfo:
    customer_id: str
    name: str
    support_entitlement: bool
    system_info: Dict[str, Any]
    
    def to_dict(self):
        return {
            "customer_id": self.customer_id,
            "name": self.name,
            "support_entitlement": self.support_entitlement,
            "system_info": self.system_info
        }

@dataclass
class TriageResult:
    customer_info: CustomerInfo
    user_reported_issue: str
    has_entitlement: bool
    additional_info: str
    
    def to_dict(self):
        return {
            "customer_info": self.customer_info.to_dict(),
            "user_reported_issue": self.user_reported_issue,
            "has_entitlement": self.has_entitlement,
            "additional_info": self.additional_info
        }

@dataclass
class ExpertAnalysis:
    issue_analysis: str
    proposed_solution: str
    confidence_score: float
    
    def to_dict(self):
        return {
            "issue_analysis": self.issue_analysis,
            "proposed_solution": self.proposed_solution,
            "confidence_score": self.confidence_score
        }

@dataclass
class SolutionUpdate:
    approved: bool
    final_solution: str
    support_notes: str
    
    @staticmethod
    def from_dict(data):
        return SolutionUpdate(**data)

# === Agent Tools ===
@tool
def lookup_customer(customer_id: str) -> Dict[str, Any]:
    """Look up customer information by customer ID using Dapr state store"""
    try:
        with DaprClient() as client:
            result = client.get_state("customer-state", customer_id)
            if result.data:
                customer_data = json.loads(result.data)
                logging.info(f"Found customer: {customer_id}")
                return customer_data
            else:
                logging.warning(f"Customer not found: {customer_id}")
                return {"error": f"Customer {customer_id} not found"}
    except Exception as e:
        logging.error(f"Error looking up customer {customer_id}: {e}")
        return {"error": f"Failed to lookup customer: {str(e)}"}

@tool
def lookup_system_info(customer_id: str) -> Dict[str, Any]:
    """Look up customer's system information using Dapr state store"""
    try:
        with DaprClient() as client:
            result = client.get_state("system-state", customer_id)
            if result.data:
                system_data = json.loads(result.data)
                logging.info(f"Found system info for customer: {customer_id}")
                return system_data
            else:
                logging.warning(f"System info not found for customer: {customer_id}")
                return {"error": f"System info not found for customer {customer_id}"}
    except Exception as e:
        logging.error(f"Error looking up system info for {customer_id}: {e}")
        return {"error": f"Failed to lookup system info: {str(e)}"}

@tool
def query_knowledge_base(query_focus: str, context_info: str = "") -> Dict[str, Any]:
    """Query the knowledge base for specific aspects of issues and solutions (MCP call simulation)"""
    # This simulates an MCP call to a knowledge base
    # In a real implementation, this would make an actual MCP call
    try:
        # Simulate different types of knowledge base responses based on query focus
        knowledge_responses = {
            "connection": {
                "similar_issues": [
                    {
                        "issue": "Dapr sidecar connection timeout to state store",
                        "solution": "Increase connection timeout in component configuration, verify network connectivity",
                        "confidence": 0.90
                    },
                    {
                        "issue": "Redis connection refused errors",
                        "solution": "Check Redis server status, verify port and host configuration",
                        "confidence": 0.85
                    }
                ],
                "technical_details": "Connection issues often stem from network configuration, firewall rules, or service discovery problems",
                "confidence_score": 0.88
            },
            "configuration": {
                "similar_issues": [
                    {
                        "issue": "State store component misconfiguration",
                        "solution": "Verify component YAML syntax, check metadata fields and connection strings",
                        "confidence": 0.92
                    },
                    {
                        "issue": "Invalid component metadata",
                        "solution": "Review component specification, ensure required fields are present",
                        "confidence": 0.80
                    }
                ],
                "technical_details": "Configuration errors are common with component metadata, connection strings, and YAML formatting",
                "confidence_score": 0.86
            },
            "version": {
                "similar_issues": [
                    {
                        "issue": "Dapr version compatibility issues",
                        "solution": "Check component version compatibility matrix, upgrade to compatible versions",
                        "confidence": 0.75
                    },
                    {
                        "issue": "Breaking changes between versions",
                        "solution": "Review migration guide and update configurations accordingly",
                        "confidence": 0.70
                    }
                ],
                "technical_details": "Version mismatches can cause unexpected behavior and connection failures",
                "confidence_score": 0.73
            }
        }
        
        # Determine response based on query focus
        query_lower = query_focus.lower()
        if "connection" in query_lower or "timeout" in query_lower or "connect" in query_lower:
            response_type = "connection"
        elif "config" in query_lower or "component" in query_lower or "yaml" in query_lower:
            response_type = "configuration"
        elif "version" in query_lower or "compatibility" in query_lower:
            response_type = "version"
        else:
            # Default comprehensive response
            response_type = "connection"
        
        knowledge_results = knowledge_responses[response_type].copy()
        knowledge_results["query_focus"] = query_focus
        knowledge_results["context_considered"] = bool(context_info)
        
        logging.info(f"Knowledge base query completed - Focus: {query_focus[:50]}...")
        return knowledge_results
        
    except Exception as e:
        logging.error(f"Error querying knowledge base: {e}")
        return {"error": f"Knowledge base query failed: {str(e)}"}

@tool
def store_analysis_result(ticket_id: str, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
    """Store the expert analysis result using Dapr state store"""
    try:
        with DaprClient() as client:
            analysis_key = f"analysis-{ticket_id}"
            client.save_state("analysis-state", analysis_key, json.dumps(analysis_result))
            logging.info(f"Stored analysis result for ticket: {ticket_id}")
            return {"success": True, "message": f"Analysis stored for ticket {ticket_id}"}
    except Exception as e:
        logging.error(f"Error storing analysis for ticket {ticket_id}: {e}")
        return {"success": False, "error": f"Failed to store analysis: {str(e)}"}

@tool
def publish_solution_notification(ticket_id: str, message: str) -> Dict[str, Any]:
    """Publish a notification that the solution is ready for review"""
    try:
        with DaprClient() as client:
            notification_data = {
                "ticket_id": ticket_id,
                "message": message,
                "timestamp": time.time(),
                "status": "solution_ready"
            }
            client.publish_event(
                pubsub_name="support-pubsub",
                topic_name="solution-notifications",
                data=json.dumps(notification_data),
                data_content_type="application/json"
            )
            logging.info(f"Published solution notification for ticket: {ticket_id}")
            return {"success": True, "message": f"Notification published for ticket {ticket_id}"}
    except Exception as e:
        logging.error(f"Error publishing notification for ticket {ticket_id}: {e}")
        return {"success": False, "error": f"Failed to publish notification: {str(e)}"}

# === Agents ===
# Triage Agent
triage_agent = Agent(
    name="Support Triage Agent",
    role="Customer Support Triage Specialist",
    goal="Analyze support tickets and validate customer entitlements",
    instructions=[
        "Look up customer information by ID using the lookup_customer tool",
        "Check if customer has support entitlement",
        "Look up customer's system information using lookup_system_info tool",
        "Provide a comprehensive triage analysis including customer details, entitlement status, and system information",
        "Format the response clearly with all relevant details"
    ],
    tools=[lookup_customer, lookup_system_info],
    llm=OpenAIChatClient(model="gpt-4o")
)

# Dapr Expert Agent  
expert_agent = Agent(
    name="Dapr Expert Agent",
    role="Dapr Technical Expert",
    goal="Deeply analyze Dapr-related issues and find comprehensive solutions through extensive knowledge base research",
    instructions=[
        "Analyze the provided issue description and system information thoroughly",
        "Query the knowledge base multiple times with different approaches to gather comprehensive information",
        "Look for similar issues, root causes, and proven solutions",
        "Cross-reference different aspects of the problem (configuration, networking, versions, etc.)",
        "Synthesize findings from multiple queries into a detailed technical analysis",
        "Provide specific, actionable solutions with step-by-step instructions",
        "Include confidence levels and alternative approaches when applicable",
        "Be exhaustive in your research - query as many relevant aspects as needed",
        "Return a comprehensive analysis with clear problem identification and solution recommendations"
    ],
    tools=[query_knowledge_base],
    llm=OpenAIChatClient(model="gpt-4o")
)

# Notification function using Dapr Conversation API
def create_customer_notification(ticket_id: str, final_solution: str, support_notes: str) -> str:
    """Create customer notification using Dapr Conversation API"""
    try:
        with DaprClient() as client:
            # Prepare the conversation input
            prompt = f"""Create a professional customer update message for:
- Ticket ID: {ticket_id}
- Status: Solution has been reviewed and approved by our support team
- Final Solution: {final_solution}
- Support Notes: {support_notes}

Create a message that:
1. References the ticket ID
2. Provides an update on the resolution
3. Is professional and reassuring
4. Thanks the customer for their patience

Format the response as a direct customer message without any additional formatting or metadata."""

            inputs = [
                ConversationInputAlpha2(
                    messages=[
                        ConversationMessage(
                            of_user=ConversationMessageOfUser(
                                content=[ConversationMessageContent(text=prompt)]
                            )
                        )
                    ],
                    scrub_pii=True,
                )
            ]
            
            metadata = {
                'model': 'gpt-4o',
                'temperature': '0.3',
                'cacheTTL': '5m'
            }
            
            # Make the conversation API call
            response = client.converse_alpha2(
                name='openai',
                inputs=inputs,
                temperature=0.3,
                metadata=metadata
            )
            
            # Extract the response
            if response.outputs:
                notification_message = response.outputs[0].choices[0].message.content
                logging.info(f"Customer notification created via Conversation API for ticket: {ticket_id}")
                return notification_message
            else:
                logging.warning(f"No response from Conversation API for ticket: {ticket_id}")
                return f"Dear Customer, your support ticket {ticket_id} has been resolved. Please check your account for details."
                
    except Exception as e:
        logging.error(f"Error creating notification via Conversation API: {e}")
        # Fallback message
        return f"Dear Customer, your support ticket {ticket_id} has been processed by our team. Thank you for your patience."

# === Activities ===
def triage_activity(ctx, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
    """First activity: Triage the support ticket"""
    try:
        ticket = SupportTicket.from_dict(ticket_data)
        logging.info(f"Starting triage for ticket: {ticket.ticket_id}")
        
        # Run triage agent
        triage_prompt = f"""
        Analyze this support ticket:
        - Ticket ID: {ticket.ticket_id}
        - Customer ID: {ticket.customer_id}
        - Issue Description: {ticket.description}
        
        Please:
        1. Look up the customer information
        2. Check their support entitlement
        3. Look up their system information
        4. Provide a comprehensive triage summary
        """
        
        response = asyncio.run(triage_agent.run(triage_prompt))
        
        # Parse the response to extract structured data
        # In a real implementation, you might want to use structured output
        triage_result = {
            "ticket_id": ticket.ticket_id,
            "customer_id": ticket.customer_id,
            "user_reported_issue": ticket.description,
            "triage_analysis": response.content if hasattr(response, 'content') else str(response),
            "timestamp": time.time()
        }
        
        logging.info(f"Triage completed for ticket: {ticket.ticket_id}")
        return triage_result
        
    except Exception as e:
        logging.error(f"Error in triage activity: {e}")
        return {"error": f"Triage failed: {str(e)}"}

def expert_analysis_activity(ctx, triage_data: Dict[str, Any]) -> Dict[str, Any]:
    """Second activity: Expert analysis of the issue, followed by storage and notification"""
    try:
        ticket_id = triage_data.get("ticket_id")
        logging.info(f"Starting expert analysis for ticket: {ticket_id}")
        
        # Run expert agent for deep analysis
        expert_prompt = f"""
        Perform comprehensive expert analysis on this support case:
        - Ticket ID: {ticket_id}
        - Customer ID: {triage_data.get('customer_id')}
        - Issue: {triage_data.get('user_reported_issue')}
        - Triage Analysis: {triage_data.get('triage_analysis')}
        
        Your task is to:
        1. Deeply analyze the issue using multiple knowledge base queries
        2. Research similar problems and their solutions
        3. Consider the customer's specific system configuration
        4. Query different aspects: configuration issues, network problems, version compatibility, etc.
        5. Provide a comprehensive technical analysis with specific solutions
        6. Include step-by-step resolution instructions
        
        Be thorough - use the knowledge base tool multiple times to gather all relevant information.
        """
        
        response = asyncio.run(expert_agent.run(expert_prompt))
        expert_analysis_text = response.content if hasattr(response, 'content') else str(response)
        
        # Prepare the analysis result
        analysis_result = {
            "ticket_id": ticket_id,
            "expert_analysis": expert_analysis_text,
            "timestamp": time.time(),
            "status": "analysis_complete"
        }
        
        logging.info(f"Expert analysis completed for ticket: {ticket_id}")
        
        # Store the analysis result using Dapr state store
        try:
            storage_result = store_analysis_result(ticket_id, analysis_result)
            if not storage_result.get("success", False):
                logging.warning(f"Failed to store analysis for ticket {ticket_id}: {storage_result.get('error')}")
            else:
                logging.info(f"Analysis stored successfully for ticket: {ticket_id}")
        except Exception as e:
            logging.error(f"Error storing analysis for ticket {ticket_id}: {e}")
        
        # Publish notification that solution is ready
        try:
            notification_message = f"Expert analysis completed for ticket {ticket_id}. Solution is ready for review."
            publish_result = publish_solution_notification(ticket_id, notification_message)
            if not publish_result.get("success", False):
                logging.warning(f"Failed to publish notification for ticket {ticket_id}: {publish_result.get('error')}")
            else:
                logging.info(f"Solution notification published for ticket: {ticket_id}")
        except Exception as e:
            logging.error(f"Error publishing notification for ticket {ticket_id}: {e}")
        
        return analysis_result
        
    except Exception as e:
        logging.error(f"Error in expert analysis activity: {e}")
        return {"error": f"Expert analysis failed: {str(e)}"}

def customer_notification_activity(ctx, final_data: Dict[str, Any]) -> Dict[str, Any]:
    """Third activity: Send customer notification using Dapr Conversation API"""
    try:
        ticket_id = final_data.get("ticket_id")
        logging.info(f"Creating customer notification for ticket: {ticket_id}")
        
        # Use Dapr Conversation API to create the notification
        customer_message = create_customer_notification(
            ticket_id=ticket_id,
            final_solution=final_data.get('final_solution', 'A comprehensive solution has been prepared'),
            support_notes=final_data.get('support_notes', 'Our team has thoroughly reviewed your case')
        )
        
        notification_result = {
            "ticket_id": ticket_id,
            "customer_message": customer_message,
            "timestamp": time.time(),
            "status": "customer_notified"
        }
        
        logging.info(f"Customer notification created for ticket: {ticket_id}")
        return notification_result
        
    except Exception as e:
        logging.error(f"Error in customer notification activity: {e}")
        return {"error": f"Customer notification failed: {str(e)}"}

# === Main Workflow ===
def customer_support_workflow(ctx: wf.DaprWorkflowContext, ticket_data: Dict[str, Any]):
    """Main customer support workflow orchestrating the three agents"""
    try:
        ticket_id = ticket_data.get("ticket_id", "unknown")
        logging.info(f"Starting customer support workflow for ticket: {ticket_id}")
        
        # Activity 1: Triage
        triage_result = yield ctx.call_activity(triage_activity, input=ticket_data)
        
        if "error" in triage_result:
            logging.error(f"Triage failed for ticket {ticket_id}: {triage_result['error']}")
            return {"status": "failed", "error": triage_result["error"]}
        
        # Check if customer has entitlement by looking at the triage analysis
        # Look for key indicators that suggest the customer has support entitlement
        triage_analysis = str(triage_result.get("triage_analysis", "")).lower()
        has_entitlement = (
            "support_entitlement: true" in triage_analysis or
            "entitlement: true" in triage_analysis or
            "enterprise" in triage_analysis or
            "professional" in triage_analysis or
            "has support" in triage_analysis or
            "entitled" in triage_analysis or
            "active support entitlement" in triage_analysis or
            "production environment" in triage_analysis
        )
        
        # Additional check: if we can't determine from analysis, check the customer data directly
        if not has_entitlement:
            try:
                customer_lookup = lookup_customer(triage_result.get("customer_id", ""))
                if not customer_lookup.get("error") and customer_lookup.get("support_entitlement"):
                    has_entitlement = True
                    logging.info(f"Direct customer lookup confirmed entitlement for {triage_result.get('customer_id')}")
                elif customer_lookup.get("error") and "not found" in customer_lookup.get("error", "").lower():
                    # Customer data is missing - this is a setup issue
                    logging.error(f"Customer data missing for {triage_result.get('customer_id')}. Please run the sample data setup script first.")
                    return {
                        "status": "setup_error",
                        "error": f"Customer data not found for {triage_result.get('customer_id')}. Please run: dapr run --app-id data-setup --resources-path ./resources -- python setup_sample_data.py",
                        "ticket_id": ticket_id
                    }
            except Exception as e:
                logging.warning(f"Could not perform direct customer lookup: {e}")
        
        if not has_entitlement:
            logging.info(f"Customer does not have support entitlement for ticket: {ticket_id}")
            return {
                "status": "no_entitlement",
                "message": "Customer does not have support entitlement",
                "ticket_id": ticket_id
            }
        
        # Activity 2: Expert Analysis
        expert_result = yield ctx.call_activity(expert_analysis_activity, input=triage_result)
        
        if "error" in expert_result:
            logging.error(f"Expert analysis failed for ticket {ticket_id}: {expert_result['error']}")
            return {"status": "failed", "error": expert_result["error"]}
        
        # Wait for external event (support team review)
        logging.info(f"Waiting for support team review for ticket: {ticket_id}")
        solution_update_event = ctx.wait_for_external_event("solution_approved")
        timeout_timer = ctx.create_timer(timedelta(seconds=30))  # 30 second timeout
        
        completed_task = yield wf.when_any([solution_update_event, timeout_timer])
        
        final_solution_data = {}
        if completed_task == solution_update_event:
            # Solution was reviewed and approved
            event_result = solution_update_event.get_result()
            final_solution_data = {
                "ticket_id": ticket_id,
                "final_solution": event_result.get("final_solution", "Solution approved"),
                "support_notes": event_result.get("support_notes", "Reviewed by support team"),
                "approved": True
            }
            logging.info(f"Solution approved for ticket: {ticket_id}")
        else:
            # Timeout occurred
            final_solution_data = {
                "ticket_id": ticket_id,
                "final_solution": "Your case is still under review by our support team",
                "support_notes": "Case requires additional review time",
                "approved": False
            }
            logging.warning(f"Timeout waiting for solution approval for ticket: {ticket_id}")
        
        # Activity 3: Customer Notification
        notification_result = yield ctx.call_activity(customer_notification_activity, input=final_solution_data)
        
        if "error" in notification_result:
            logging.error(f"Customer notification failed for ticket {ticket_id}: {notification_result['error']}")
            return {"status": "partial_success", "error": notification_result["error"]}
        
        # Final result
        workflow_result = {
            "status": "completed",
            "ticket_id": ticket_id,
            "triage_result": triage_result,
            "expert_result": expert_result,
            "notification_result": notification_result,
            "final_solution": final_solution_data
        }
        
        logging.info(f"Customer support workflow completed for ticket: {ticket_id}")
        return workflow_result
        
    except Exception as e:
        logging.error(f"Error in customer support workflow: {e}")
        return {"status": "failed", "error": str(e)}

# === FastAPI Setup ===
@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan manager for workflow runtime"""
    # Register workflow and activities
    wfr.register_workflow(customer_support_workflow)
    wfr.register_activity(triage_activity)
    wfr.register_activity(expert_analysis_activity)
    wfr.register_activity(customer_notification_activity)
    
    # Start workflow runtime
    wfr.start()
    logging.info("=== Customer Support Workflow Runtime Started ===")
    yield
    
    # Shutdown
    wfr.shutdown()
    logging.info("=== Customer Support Workflow Runtime Stopped ===")

app = FastAPI(
    title="Customer Support System",
    description="AI-powered customer support system with workflow orchestration",
    lifespan=lifespan
)

# === API Models ===
class TicketInput(BaseModel):
    ticket_id: str = Field(description="Unique ticket identifier")
    customer_id: str = Field(description="Customer identifier")
    description: str = Field(description="Description of the issue")

class SolutionApprovalInput(BaseModel):
    approved: bool = Field(description="Whether the solution is approved")
    final_solution: str = Field(description="Final solution text")
    support_notes: str = Field(description="Additional notes from support team")

# === API Endpoints ===
@app.post("/support/ticket")
def create_support_ticket(ticket: TicketInput):
    """Create a new support ticket and start the workflow"""
    try:
        client = DaprWorkflowClient()
        instance_id = f"support-{ticket.ticket_id}"
        
        workflow_input = {
            "ticket_id": ticket.ticket_id,
            "customer_id": ticket.customer_id,
            "description": ticket.description
        }
        
        scheduled_id = client.schedule_new_workflow(
            workflow=customer_support_workflow,
            input=workflow_input,
            instance_id=instance_id
        )
        
        logging.info(f"Support ticket workflow started: {scheduled_id}")
        return {
            "instance_id": scheduled_id,
            "ticket_id": ticket.ticket_id,
            "status": "workflow_started"
        }
        
    except Exception as e:
        logging.error(f"Error creating support ticket: {e}")
        return {"error": f"Failed to create support ticket: {str(e)}"}

@app.post("/support/approve/{ticket_id}")
def approve_solution(ticket_id: str, approval: SolutionApprovalInput):
    """Approve or modify the proposed solution"""
    try:
        client = DaprWorkflowClient()
        instance_id = f"support-{ticket_id}"
        
        client.raise_workflow_event(
            instance_id=instance_id,
            event_name="solution_approved",
            data=approval.model_dump()
        )
        
        logging.info(f"Solution approval sent for ticket: {ticket_id}")
        return {
            "status": "approval_sent",
            "ticket_id": ticket_id,
            "instance_id": instance_id
        }
        
    except Exception as e:
        logging.error(f"Error approving solution for ticket {ticket_id}: {e}")
        return {"error": f"Failed to approve solution: {str(e)}"}

@app.get("/support/status/{ticket_id}")
def get_ticket_status(ticket_id: str):
    """Get the current status of a support ticket"""
    try:
        client = DaprWorkflowClient()
        instance_id = f"support-{ticket_id}"
        
        state = client.get_workflow_state(instance_id)
        
        return {
            "ticket_id": ticket_id,
            "instance_id": instance_id,
            "status": state.runtime_status.name if state else "not_found",
            "output": state.serialized_output if state and state.serialized_output else None
        }
        
    except Exception as e:
        logging.error(f"Error getting status for ticket {ticket_id}: {e}")
        return {"error": f"Failed to get ticket status: {str(e)}"}

@app.get("/data")
def list_all_data():
    """List all data: customers, systems, analysis, and tickets"""
    try:
        with DaprClient() as client:
            result = {
                "customers": [],
                "systems": [],
                "analysis": [],
                "tickets": []
            }
            
            # List customers from customer-state
            try:
                customers_response = client.get_bulk_state("customer-state", [])
                if hasattr(customers_response, 'items'):
                    for item in customers_response.items:
                        if item.data:
                            customer_data = json.loads(item.data)
                            result["customers"].append({
                                "key": item.key,
                                "data": customer_data
                            })
            except Exception as e:
                logging.warning(f"Error listing customers: {e}")
                result["customers"] = {"error": str(e)}
            
            # List systems from system-state
            try:
                systems_response = client.get_bulk_state("system-state", [])
                if hasattr(systems_response, 'items'):
                    for item in systems_response.items:
                        if item.data:
                            system_data = json.loads(item.data)
                            result["systems"].append({
                                "key": item.key,
                                "data": system_data
                            })
            except Exception as e:
                logging.warning(f"Error listing systems: {e}")
                result["systems"] = {"error": str(e)}
            
            # List analysis from analysis-state
            try:
                analysis_response = client.get_bulk_state("analysis-state", [])
                if hasattr(analysis_response, 'items'):
                    for item in analysis_response.items:
                        if item.data:
                            analysis_data = json.loads(item.data)
                            result["analysis"].append({
                                "key": item.key,
                                "data": analysis_data
                            })
            except Exception as e:
                logging.warning(f"Error listing analysis: {e}")
                result["analysis"] = {"error": str(e)}
            
            # List tickets from execution-state (workflow instances)
            try:
                tickets_response = client.get_bulk_state("execution-state", [])
                if hasattr(tickets_response, 'items'):
                    for item in tickets_response.items:
                        if item.data:
                            ticket_data = json.loads(item.data)
                            result["tickets"].append({
                                "key": item.key,
                                "data": ticket_data
                            })
            except Exception as e:
                logging.warning(f"Error listing tickets: {e}")
                result["tickets"] = {"error": str(e)}
            
            return {
                "status": "success",
                "counts": {
                    "customers": len(result["customers"]) if isinstance(result["customers"], list) else 0,
                    "systems": len(result["systems"]) if isinstance(result["systems"], list) else 0,
                    "analysis": len(result["analysis"]) if isinstance(result["analysis"], list) else 0,
                    "tickets": len(result["tickets"]) if isinstance(result["tickets"], list) else 0
                },
                "data": result
            }
            
    except Exception as e:
        logging.error(f"Error listing data: {e}")
        return {
            "status": "error",
            "message": f"Failed to list data: {str(e)}"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
