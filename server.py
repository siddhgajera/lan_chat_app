import socket
import threading
import datetime

# Configuration
HOST = '0.0.0.0'  # Listen on all network interfaces
PORT = 55555
LOG_FILE = 'chat_logs.txt'

clients = {}  # socket: username
lock = threading.Lock()

def log_message(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    with open(LOG_FILE, 'a') as f:
        f.write(log_entry)
    print(log_entry.strip())

def broadcast(message, sender_socket=None):
    with lock:
        for client_socket in clients:
            if client_socket != sender_socket:
                try:
                    client_socket.send(message.encode('utf-8'))
                except:
                    client_socket.close()
                    # We'll handle removal in the handle_client thread

def handle_client(client_socket, address):
    username = None
    try:
        # First message is expected to be the username
        username = client_socket.recv(1024).decode('utf-8')
        if not username:
            client_socket.close()
            return

        with lock:
            clients[client_socket] = username
        
        join_msg = f"SERVER: {username} has joined the chat."
        log_message(join_msg)
        broadcast(join_msg)

        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            
            if message == "/exit":
                break
            
            chat_msg = f"{username}: {message}"
            log_message(chat_msg)
            broadcast(chat_msg, client_socket)

    except ConnectionResetError:
        pass
    finally:
        if client_socket in clients:
            with lock:
                username = clients.pop(client_socket)
            leave_msg = f"SERVER: {username} has left the chat."
            log_message(leave_msg)
            broadcast(leave_msg)
        
        client_socket.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    
    log_message(f"SERVER STARTED: Listening on {HOST}:{PORT}")
    
    while True:
        client_socket, address = server.accept()
        thread = threading.Thread(target=handle_client, args=(client_socket, address))
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    start_server()
