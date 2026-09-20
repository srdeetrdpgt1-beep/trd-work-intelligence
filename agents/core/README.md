# Agent Core

All agents use the common `Agent` interface.

The orchestrator should communicate with agents through this interface rather
than depending on a specific AI model.

This allows agents and AI providers to be replaced independently.
