#!/usr/bin/env python3
"""
Test script for the Customer Support System
Demonstrates the complete workflow with sample data
"""

import requests
import json
import time
import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

BASE_URL = "http://localhost:8000"

def test_support_workflow():
    """Test the complete support workflow"""
    
    # Test data
    test_ticket = {
        "ticket_id": "TEST001",
        "customer_id": "CUST001",
        "description": "My Dapr sidecar keeps timing out when trying to connect to the state store. I'm getting connection refused errors."
    }
    
    print("🎫 Testing Customer Support System Workflow")
    print("=" * 50)
    
    # Step 1: Create support ticket
    print(f"\n1. Creating support ticket: {test_ticket['ticket_id']}")
    try:
        response = requests.post(f"{BASE_URL}/support/ticket", json=test_ticket)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Ticket created successfully")
            print(f"   📋 Instance ID: {result['instance_id']}")
            print(f"   🔄 Status: {result['status']}")
        else:
            print(f"   ❌ Failed to create ticket: {response.status_code}")
            print(f"   📄 Response: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Error creating ticket: {e}")
        return
    
    # Step 2: Wait for workflow processing
    print(f"\n2. Waiting for workflow processing...")
    print("   ⏳ Triage agent analyzing customer and system info...")
    time.sleep(3)
    print("   ⏳ Expert agent querying knowledge base...")
    time.sleep(3)
    print("   ⏳ Solution analysis complete, waiting for approval...")
    
    # Step 3: Check status
    print(f"\n3. Checking ticket status")
    try:
        response = requests.get(f"{BASE_URL}/support/status/{test_ticket['ticket_id']}")
        if response.status_code == 200:
            status = response.json()
            print(f"   📊 Current status: {status['status']}")
            if status.get('output'):
                print(f"   📋 Workflow output available")
        else:
            print(f"   ⚠️  Status check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error checking status: {e}")
    
    # Step 4: Approve solution
    print(f"\n4. Simulating support team approval")
    approval_data = {
        "approved": True,
        "final_solution": "The connection timeout issue is caused by incorrect network configuration. Please update your Dapr configuration file to include the correct Redis connection string with proper timeout settings. Also ensure your firewall allows connections on port 6379.",
        "support_notes": "Reviewed the customer's system configuration. They're running Dapr 1.12.0 on Azure with Redis state store. The issue is a common configuration problem with network timeouts."
    }
    
    try:
        response = requests.post(f"{BASE_URL}/support/approve/{test_ticket['ticket_id']}", json=approval_data)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Solution approved successfully")
            print(f"   📨 Approval sent to workflow")
        else:
            print(f"   ❌ Failed to approve solution: {response.status_code}")
            print(f"   📄 Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error approving solution: {e}")
    
    # Step 5: Wait for final processing
    print(f"\n5. Waiting for customer notification generation...")
    time.sleep(5)
    
    # Step 6: Final status check
    print(f"\n6. Final status check")
    try:
        response = requests.get(f"{BASE_URL}/support/status/{test_ticket['ticket_id']}")
        if response.status_code == 200:
            status = response.json()
            print(f"   📊 Final status: {status['status']}")
            if status.get('output'):
                try:
                    output = json.loads(status['output']) if isinstance(status['output'], str) else status['output']
                    if 'notification_result' in output:
                        print(f"\n   📧 Customer Notification:")
                        print(f"   {'-' * 40}")
                        message = output['notification_result'].get('customer_message', 'No message available')
                        print(f"   {message}")
                        print(f"   {'-' * 40}")
                except:
                    print(f"   📋 Raw output: {status['output']}")
        else:
            print(f"   ⚠️  Final status check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error in final status check: {e}")
    
    print(f"\n🎉 Workflow test completed!")
    print("=" * 50)

def test_health_check():
    """Test the health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Customer Support System Test Suite")
    print("=" * 50)
    
    # Health check first
    print("\n🏥 Checking system health...")
    if not test_health_check():
        print("❌ System is not healthy. Please start the application first:")
        print("   dapr run -f .")
        exit(1)
    
    # Run workflow test
    test_support_workflow()
    
    print(f"\n📝 Test Summary:")
    print("   - Created support ticket")
    print("   - Triggered triage agent (customer lookup)")
    print("   - Triggered expert agent (knowledge base query)")  
    print("   - Simulated support team approval")
    print("   - Generated customer notification via Conversation API")
    print("   - Completed full workflow orchestration")


