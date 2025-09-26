#!/bin/bash
# monitor_ticket.sh - Monitor ticket progress in real-time

# Default ticket ID
TICKET_ID=${1:-"TEST001"}

echo "🔍 Monitoring ticket: $TICKET_ID"
echo "Press Ctrl+C to stop monitoring"
echo "=================================="

while true; do
  echo ""
  echo "=== $(date '+%H:%M:%S') ==="
  
  # Get ticket status
  STATUS_RESPONSE=$(curl -s "http://localhost:8000/support/status/$TICKET_ID" 2>/dev/null)
  
  if [ $? -eq 0 ] && [ -n "$STATUS_RESPONSE" ]; then
    # Extract status using jq if available, otherwise use grep
    if command -v jq &> /dev/null; then
      STATUS=$(echo "$STATUS_RESPONSE" | jq -r '.status // "unknown"')
      INSTANCE_ID=$(echo "$STATUS_RESPONSE" | jq -r '.instance_id // "unknown"')
      OUTPUT=$(echo "$STATUS_RESPONSE" | jq -r '.output // "none"')
      
      echo "📊 Status: $STATUS"
      echo "🆔 Instance: $INSTANCE_ID"
      
      # Show output if it's not "none" and not too long
      if [ "$OUTPUT" != "none" ] && [ "$OUTPUT" != "null" ]; then
        OUTPUT_LENGTH=$(echo "$OUTPUT" | wc -c)
        if [ $OUTPUT_LENGTH -lt 200 ]; then
          echo "📋 Output: $OUTPUT"
        else
          echo "📋 Output: [Long output - check manually]"
        fi
      fi
    else
      # Fallback without jq
      echo "📊 Response: $STATUS_RESPONSE"
    fi
  else
    echo "❌ Failed to get status (system may not be running)"
  fi
  
  sleep 3
done
