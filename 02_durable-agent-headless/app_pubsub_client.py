#!/usr/bin/env python3
import json
import time
from dapr.clients import DaprClient

def trigger_agent(agent_topic: str, task: str, pubsub_name: str = "message-pubsub"):
    """Trigger a DurableAgent with a specific task"""

    try:
        with DaprClient() as client:
            client.publish_event(
                pubsub_name=pubsub_name,
                topic_name=agent_topic,
                data=json.dumps({"task": task}),
                data_content_type="application/json",
                publish_metadata={
                    "cloudevent.type": "TriggerAction",
                }
            )
        print(f"✅ Successfully triggered agent '{agent_topic}' with task: {task}")
        return True

    except Exception as e:
        print(f"❌ Failed to trigger agent: {e}")
        return False

# Usage
if __name__ == "__main__":
    for dest in ["Paris", "London", "Tokyo", "New York"]:
        trigger_agent("TravelBuddy-Headless", f"Find flights to {dest}")