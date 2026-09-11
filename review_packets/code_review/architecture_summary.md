# 🏛️ Integration Contract & API Boundary Validation Report

## 🔒 Contract Boundaries (`v3.0.0-Truth`)
All local inter-process sockets operate through contract guards:

1. **Telemetry Publisher Port (`5555`)**: Streams live hardware state frames from `sensor_stream.py` to the observer network[cite: 1].
2. **Analytics Ingress Port (`5556`)**: Ingests frames into `analytics_worker.py` for health checks[cite: 1].
3. **Validation Invariant**: All payloads must pass `validate_contract()` before dispatch[cite: 1]. Out-of-spec frames raise an immediate `SchemaValidationError` and are safely dropped before reaching execution logic[cite: 2, 3].