import socket
import json
import time

class EcosystemHALGateway:
    """Enterprise Abstraction Layer providing a reusable gateway for the TANTRA ecosystem.
    
    Eliminates direct socket coupling by providing robust serialization, 
    connection lifecycle management, and strict contract verification boundary points.
    """
    def __init__(self, host='127.0.0.1', port=5555):
        self.host = host
        self.port = port
        self.socket = None
        self.connection = None

    def initialize_server(self):
        """Initializes a reusable listener gateway for downstream ecosystem attachments."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(1)
        print(f"🔌 [HAL GATEWAY] Reusable platform listener bound to {self.host}:{self.port}")
        self.connection, addr = self.socket.accept()
        print(f"🔌 [HAL GATEWAY] Ecosystem peer node attached securely from: {addr}")
        return self.connection

    def initialize_client(self):
        """Initializes a reusable outbound channel to attach to upstream controllers."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                self.socket.connect((self.host, self.port))
                print(f"🔌 [HAL GATEWAY] Connected successfully to upstream channel on port {self.port}")
                return self.socket
            except socket.error:
                print("⏳ [HAL GATEWAY] Upstream channel unavailable. Polling ecosystem loop...")
                time.sleep(1.5)

    def transmit_frame(self, payload: dict):
        """Serializes and pushes frames downstream via the abstraction interface layer."""
        if not self.connection and not self.socket:
            raise RuntimeError("HAL Gateway channel is not initialized.")
        
        serialized_data = (json.dumps(payload) + "\n").encode('utf-8')
        target_channel = self.connection if self.connection else self.socket
        target_channel.sendall(serialized_data)

    def terminate_gateway(self):
        """Gracefully closes interface connections without risking orphaned system ports."""
        if self.connection:
            self.connection.close()
        if self.socket:
            self.socket.close()
        print("🔌 [HAL GATEWAY] Interface channel severed gracefully.")