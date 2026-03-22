System Architecture (The Structure):

This section explains the "layers" of your software and the "types" of hardware it is designed to handle.

Modular Design: The system is built as a standalone, 4-layer stack that is "integration-ready" for future robotic platforms.

Multi-Rate Sensor Stack:

1] IMU: Operates at 10 Hz (High Frequency) as the primary timing reference.

2] Distance/Depth: Operates at 2 Hz (Medium Frequency) for terrain awareness.

3] Leak/Contact Sensors: Event-based binary sensors for internal safety and hull integrity.

Error Handling Layer: A dedicated module for injecting and detecting real-world issues like 99.9m spikes and IMU drift.
