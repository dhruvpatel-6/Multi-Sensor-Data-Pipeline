```Mermaid![](image.png)
graph TD
    %% Global Styling
    classDef hardware fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    classDef logic fill:#fff3e0,stroke:#e65100,stroke-width:2px;
    classDef safety fill:#ffebee,stroke:#c62828,stroke-width:2px;
    classDef storage fill:#f1f8e9,stroke:#33691e,stroke-width:2px;

    %% Nodes and Connections
    subgraph DRIVERS [Drivers Layer - Asynchronous IO]
        A[pipeline_sim.py] -->|Raw Sensor Packets| B(Buffer Stream)
    end

    subgraph CORE [Core Orchestrator - 10Hz Deterministic Loop]
        B --> C{main_telemetry.py}
        C -->|Heartbeat Trigger| D{Safety Guard}
        
        %% Recovery Path
        D -->|NoneType Error| E[Recovery Flow: continue]
        
        %% Logic Path
        D -->|Valid Packet| F[fid.py: Failure Intel]
    end

    subgraph LAYERS [Output & Storage Layer]
        F --> G[pipeline_sync.py: Data Contract]
        G --> H[(telemetry_data.jsonl)]
        G --> I[Terminal Monitor]
    end

    %% Applying Styles
    class A,B hardware;
    class C,F,G logic;
    class D,E safety;
    class H,I storage;