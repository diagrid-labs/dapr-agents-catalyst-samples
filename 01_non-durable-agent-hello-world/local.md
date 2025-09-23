# Local Development Alternative

> **Note**: We recommend using [Diagrid Catalyst](../README.md) for the full experience with enterprise-grade observability, managed infrastructure, and workflow visualization. This local setup is provided as an alternative for development scenarios where cloud deployment isn't suitable.

## Prerequisites for Local Setup

- [Dapr CLI installed](https://docs.dapr.io/getting-started/install-dapr-cli/)
- Docker Desktop running
- Local Dapr initialized: `dapr init`

## Limitations of Local Development

This approach lacks several key features provided by Catalyst:
- Advanced application architecture visualization
- Enterprise workflow monitoring and debugging
- Managed infrastructure with automatic scaling
- Advanced observability and metrics

## Run Locally

Initialize local Dapr components and run the agent:

```bash
# Ensure Dapr is initialized with required components
dapr init

# Run the hello world agent locally
dapr run -f dapr.yaml
```

The agent will run with local Redis for state storage and local workflow engine.

## Basic Local Monitoring

### Inspect Local Redis (Optional)
```bash
docker run --rm -d --name redisinsight -p 5540:5540 redis/redisinsight:latest
open http://localhost:5540/
```

## Recommended Next Steps

For production-ready development and the full feature set, migrate to [Catalyst deployment](../README.md).