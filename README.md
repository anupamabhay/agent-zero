# Agent Zero

**Zero** is your production-ready autonomous agent, designed to execute tasks with precision and minimal overhead.

## Overview

A robust, modular AI agent using a **State Machine Architecture** (via **LangGraph**) rather than a simple loop. This ensures deterministic behavior, "time-travel" debugging, and better error recovery. The system will prioritize **Type Safety** (Pydantic) and **Observability** (Structured Logging/Tracing).

## Getting Started

1. Install dependencies:
   ```bash
   poetry install
   ```

2. Run the agent:
   ```bash
   poetry run python -m src.main
   ```
