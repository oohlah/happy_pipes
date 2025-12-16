import socket
import threading

class SensorListener:
    def __init__(self, host='0.0.0.0', port=5000, buffer_size=1024):
        #Initialise the UDP Listener.
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.running = False
        self.callback = None

    def start(self):      
        #Start in a separate thread.
        self.running = True
        threading.Thread(target=self._listen, daemon=True).start()

    def stop(self):
        #Stop the UDP listener.
        self.running = False

    def _listen(self):
        #Internal method to listen for UDP packets and handle them.
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server:
            server.bind((self.host, self.port))
            print(f"UDP Listener started on {self.host}:{self.port}")
            while self.running:
                try:
                    data, address = server.recvfrom(self.buffer_size)
                    print(f"Received data: {data.decode()} from {address}")
                    if self.callback:
                        self.callback(data.decode())
                except Exception as e:
                    print(f"Error receiving data: {e}")
            print("UDP Listener stopped.")

if __name__ == "__main__":
    # Example usage
    def handle_data(data):
        print(f"Processing data: {data}")

    listener = SensorListener(port=5000)
    listener.callback=handle_data
    listener.start()

    try:
        while True:
            pass  # Keep the main thread alive
    except KeyboardInterrupt:
        listener.stop()
