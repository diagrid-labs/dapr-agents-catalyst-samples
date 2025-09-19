#!/usr/bin/env python3
"""
Sample data setup script for the Customer Support System
This script populates the state stores with sample customer and system data
"""

import json
import logging
from dapr.clients import DaprClient
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

def setup_sample_customers():
    """Set up sample customer data"""
    customers = [
        {
            "customer_id": "CUST001",
            "name": "Acme Corporation",
            "email": "support@acme.com",
            "support_entitlement": True,
            "plan": "Enterprise",
            "created_date": "2023-01-15"
        },
        {
            "customer_id": "CUST002", 
            "name": "TechStart Inc",
            "email": "help@techstart.com",
            "support_entitlement": True,
            "plan": "Professional",
            "created_date": "2023-06-20"
        },
        {
            "customer_id": "CUST003",
            "name": "Basic User LLC",
            "email": "user@basicuser.com", 
            "support_entitlement": False,
            "plan": "Basic",
            "created_date": "2024-01-10"
        }
    ]
    
    with DaprClient() as client:
        for customer in customers:
            client.save_state(
                "customer-state",
                customer["customer_id"],
                json.dumps(customer)
            )
            logging.info(f"Created customer: {customer['customer_id']} - {customer['name']}")

def setup_sample_systems():
    """Set up sample system information"""
    systems = [
        {
            "customer_id": "CUST001",
            "environment": "Production",
            "dapr_version": "1.12.0",
            "kubernetes_version": "1.28.2",
            "cloud_provider": "Azure",
            "region": "East US",
            "applications": [
                {"name": "order-service", "version": "2.1.0"},
                {"name": "payment-service", "version": "1.8.3"},
                {"name": "inventory-service", "version": "3.0.1"}
            ],
            "components": [
                {"type": "state", "name": "redis-state", "version": "v1"},
                {"type": "pubsub", "name": "azure-servicebus", "version": "v1"},
                {"type": "bindings", "name": "azure-storage", "version": "v1"}
            ]
        },
        {
            "customer_id": "CUST002",
            "environment": "Staging", 
            "dapr_version": "1.11.5",
            "kubernetes_version": "1.27.1",
            "cloud_provider": "AWS",
            "region": "us-west-2",
            "applications": [
                {"name": "api-gateway", "version": "1.5.2"},
                {"name": "user-service", "version": "2.0.0"}
            ],
            "components": [
                {"type": "state", "name": "dynamodb-state", "version": "v1"},
                {"type": "pubsub", "name": "aws-sns-sqs", "version": "v1"}
            ]
        },
        {
            "customer_id": "CUST003",
            "environment": "Development",
            "dapr_version": "1.10.0", 
            "kubernetes_version": "1.26.0",
            "cloud_provider": "Local",
            "region": "localhost",
            "applications": [
                {"name": "test-app", "version": "0.1.0"}
            ],
            "components": [
                {"type": "state", "name": "redis-local", "version": "v1"}
            ]
        }
    ]
    
    with DaprClient() as client:
        for system in systems:
            client.save_state(
                "system-state",
                system["customer_id"],
                json.dumps(system)
            )
            logging.info(f"Created system info for: {system['customer_id']} - {system['environment']}")

if __name__ == "__main__":
    logging.info("Setting up sample data for Customer Support System...")
    
    try:
        # Test Dapr connection first
        with DaprClient() as test_client:
            logging.info("Dapr connection successful")
        
        logging.info("Creating sample customers...")
        setup_sample_customers()
        
        logging.info("Creating sample system information...")
        setup_sample_systems()
        
        # Verify data was created
        logging.info("Verifying sample data...")
        with DaprClient() as client:
            # Test customer lookup
            result = client.get_state("customer-state", "CUST001")
            if result.data:
                logging.info("✅ Customer data verification successful")
            else:
                logging.warning("⚠️  Customer data verification failed")
            
            # Test system info lookup
            result = client.get_state("system-state", "CUST001")
            if result.data:
                logging.info("✅ System data verification successful")
            else:
                logging.warning("⚠️  System data verification failed")
        
        logging.info("✅ Sample data setup completed successfully!")
        logging.info("You can now run the customer support system with: dapr run -f .")
        
    except Exception as e:
        if "Connection refused" in str(e) or "Health check" in str(e):
            logging.error("❌ Dapr is not running!")
            logging.error("Please start Dapr first:")
            logging.error("  dapr run --app-id data-setup --resources-path ../resources -- python setup_sample_data.py")
        else:
            logging.error(f"❌ Error setting up sample data: {e}")
            import traceback
            traceback.print_exc()
