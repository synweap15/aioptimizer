# OpenAI Agents SDK Guide

This document provides guidance on using the OpenAI Agents SDK in the AI Optimizer project.

## Overview

The OpenAI Agents SDK is a lightweight, powerful framework for building multi-agent workflows. It's a production-ready upgrade of OpenAI's Swarm experimentation framework.

## Installation

Already included in the project dependencies:

```bash
poetry add openai-agents
```

## Core Concepts

### 1. Agents

Agents are LLMs equipped with instructions and tools. They're the basic building blocks.

```python
from agents import Agent

agent = Agent(
    name="Math Tutor",
    instructions="You are a helpful math tutor. Help students understand concepts.",
    model="gpt-4o",
)
```

### 2. Tools

Functions that agents can call to perform actions:

```python
def calculate(expression: str) -> str:
    """Calculate a mathematical expression."""
    try:
        result = eval(expression)  # Use safe eval in production
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

agent = Agent(
    name="Calculator Agent",
    instructions="You help with calculations.",
    tools=[calculate],
)
```

### 3. Handoffs

Allow agents to delegate tasks to other specialized agents:

```python
math_tutor = Agent(
    name="Math Tutor",
    instructions="You help with math problems.",
)

history_tutor = Agent(
    name="History Tutor",
    instructions="You help with history questions.",
)

triage_agent = Agent(
    name="Triage Agent",
    instructions="Determine which tutor to use based on the question.",
    handoffs=[math_tutor, history_tutor],
)
```

### 4. Sessions

Maintain conversation history across multiple agent runs:

```python
from agents import Runner

async def main():
    result = await Runner.run(
        agent=triage_agent,
        input="What's the derivative of x^2?",
    )
    print(result.final_output)
```

### 5. Guardrails

Validate agent inputs and outputs:

```python
async def content_guardrail(ctx, agent, input_data):
    """Block inappropriate content."""
    # Check input
    is_safe = await check_content_safety(input_data)

    return GuardrailFunctionOutput(
        output_info={"is_safe": is_safe},
        tripwire_triggered=not is_safe,
    )

agent = Agent(
    name="Chat Agent",
    instructions="You are a helpful assistant.",
    input_guardrails=[content_guardrail],
)
```

## Integration with FastAPI

### Service Layer Pattern

Create an agent service for managing OpenAI agents:

```python
# backend/services/agent_service.py
from agents import Agent, Runner
from settings import OPENAI_API_KEY

class AgentService:
    """Service for managing OpenAI agents"""

    def __init__(self):
        self.agents = {}
        self._initialize_agents()

    def _initialize_agents(self):
        """Initialize all agents"""
        self.agents['math'] = Agent(
            name="Math Tutor",
            instructions="You help with math problems.",
        )

        self.agents['triage'] = Agent(
            name="Triage Agent",
            instructions="Route to appropriate agent.",
            handoffs=[self.agents['math']],
        )

    async def run_agent(self, agent_name: str, input_text: str):
        """Run an agent with input"""
        agent = self.agents.get(agent_name)
        if not agent:
            raise ValueError(f"Agent {agent_name} not found")

        result = await Runner.run(agent=agent, input=input_text)
        return result.final_output
```

### Router Integration

```python
# backend/routers/agent.py
from fastapi import APIRouter, Depends
from services.agent_service import AgentService
from schemas.request.agent import AgentRunRequest
from schemas.response.agent import AgentRunResponse

router = APIRouter(prefix="/agents", tags=["agents"])

def get_agent_service() -> AgentService:
    return AgentService()

@router.post("/run", response_model=AgentRunResponse)
async def run_agent(
    request: AgentRunRequest,
    agent_service: AgentService = Depends(get_agent_service),
):
    """Run an agent with the provided input"""
    result = await agent_service.run_agent(
        agent_name=request.agent_name,
        input_text=request.input_text,
    )
    return AgentRunResponse(output=result)
```

## Common Patterns

### 1. Routing Pattern

Use a triage agent to route requests to specialized agents:

```python
support_agent = Agent(name="Support", instructions="Handle support queries")
sales_agent = Agent(name="Sales", instructions="Handle sales queries")

router_agent = Agent(
    name="Router",
    instructions="Route to the appropriate department.",
    handoffs=[support_agent, sales_agent],
)
```

### 2. Sequential Workflow

Chain agents for multi-step processes:

```python
researcher = Agent(
    name="Researcher",
    instructions="Research the topic thoroughly.",
)

writer = Agent(
    name="Writer",
    instructions="Write content based on research.",
)

editor = Agent(
    name="Editor",
    instructions="Edit and polish the content.",
    handoffs=[researcher, writer],
)
```

### 3. Human-in-the-Loop

Use Temporal integration for long-running workflows:

```python
from agents.temporal import TemporalAgent

approval_agent = TemporalAgent(
    name="Approval Agent",
    instructions="Request human approval for actions.",
    requires_human_approval=True,
)
```

## Tracing and Monitoring

The SDK includes built-in tracing to the OpenAI Dashboard:

```python
from agents import Runner

# Tracing is automatic
result = await Runner.run(
    agent=my_agent,
    input="Hello",
    context={"user_id": 123},  # Add context for better tracing
)
```

View traces in the [OpenAI Dashboard](https://platform.openai.com/agents).

## Best Practices

### 1. Clear Instructions

Give agents specific, clear instructions:

```python
# Bad
agent = Agent(name="Helper", instructions="Help the user")

# Good
agent = Agent(
    name="Customer Support Agent",
    instructions="""
    You are a customer support agent for TechCo.
    - Be polite and professional
    - Address issues with urgency
    - Escalate to humans when needed
    - Never make promises about refunds without approval
    """,
)
```

### 2. Structured Outputs

Use Pydantic models for tool return values:

```python
from pydantic import BaseModel

class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str

def web_search(query: str) -> list[SearchResult]:
    """Search the web and return structured results."""
    # Implementation
    pass
```

### 3. Error Handling

Always handle errors in tools and agent calls:

```python
async def safe_agent_run(agent: Agent, input_text: str):
    try:
        result = await Runner.run(agent=agent, input=input_text)
        return result.final_output
    except Exception as e:
        logger.error(f"Agent error: {e}")
        return "I apologize, but I encountered an error. Please try again."
```

### 4. Testing

Write tests for your agents:

```python
import pytest
from agents import Runner

@pytest.mark.asyncio
async def test_math_agent():
    result = await Runner.run(
        agent=math_agent,
        input="What is 2 + 2?",
    )
    assert "4" in result.final_output
```

## Environment Setup

Required environment variables:

```bash
# .env
OPENAI_API_KEY=sk-...
```

## Resources

- [OpenAI Agents SDK Documentation](https://openai.github.io/openai-agents-python/)
- [GitHub Repository](https://github.com/openai/openai-agents-python)
- [Quickstart Guide](https://openai.github.io/openai-agents-python/quickstart/)
- [OpenAI Dashboard](https://platform.openai.com/agents)

## Example: Complete Agent Implementation

```python
# backend/services/customer_support_service.py
from agents import Agent, Runner
from typing import Optional

class CustomerSupportService:
    """Customer support agent service"""

    def __init__(self):
        self.support_agent = self._create_support_agent()

    def _create_support_agent(self) -> Agent:
        return Agent(
            name="Customer Support",
            instructions="""
            You are a helpful customer support agent.
            - Be empathetic and professional
            - Solve issues when possible
            - Escalate complex issues to human agents
            - Always end with asking if there's anything else to help with
            """,
            tools=[self.search_orders, self.track_shipment],
        )

    def search_orders(self, order_id: str) -> str:
        """Search for order by ID."""
        # Implementation
        return f"Order {order_id}: Status - Shipped"

    def track_shipment(self, tracking_number: str) -> str:
        """Track shipment by tracking number."""
        # Implementation
        return f"Tracking {tracking_number}: In transit"

    async def handle_query(self, user_query: str) -> str:
        """Handle a customer support query."""
        result = await Runner.run(
            agent=self.support_agent,
            input=user_query,
        )
        return result.final_output
```

## Next Steps

1. Experiment with simple agents in the playground
2. Build a multi-agent workflow for your use case
3. Add tools for database queries or API calls
4. Implement guardrails for safety
5. Set up monitoring and tracing
6. Deploy to production with proper error handling
