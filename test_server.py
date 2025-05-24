import socket

broker = "172.17.34.107"
broker = "test.mosquitto.org"

def check_server(host, port, timeout=5):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            print(f"✅ Connection to {host}:{port} succeeded!")
            return True
    except Exception as e:
        print(f"❌ Connection to {host}:{port} failed: {e}")
        return False

# Example usage
check_server(broker, 1883)  # Replace with your server and port