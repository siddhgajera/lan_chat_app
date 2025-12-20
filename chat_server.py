import socket
import threading
import datetime
import sys

class ChatServer:
    def __init__(self, host='0.0.0.0', port=5555):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []  # List of client sockets
        self.usernames = {}  # Dictionary mapping socket to username
        self.lock = threading.Lock()  # Thread lock for safe access to clients list
        self.log_file = 'chat_logs.txt'
        
    def start(self):
        """Start the chat server"""
        try:
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            
            log_msg = f"[{self.get_timestamp()}] Server started on {self.host}:{self.port}"
            print(log_msg)
            self.log_message(log_msg)
            
            # Accept connections in a loop
            while True:
                client_socket, address = self.server_socket.accept()
                print(f"[{self.get_timestamp()}] New connection from {address}")
                
                # Start a new thread for each client
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_thread.daemon = True
                client_thread.start()
                
        except KeyboardInterrupt:
            print("\n[SERVER] Shutting down server...")
            self.shutdown()
        except Exception as e:
            print(f"[SERVER ERROR] {e}")
            self.shutdown()
    
    def handle_client(self, client_socket):
        """Handle individual client connection"""
        username = None
        try:
            # Request username from client
            client_socket.send("USERNAME".encode('utf-8'))
            username = client_socket.recv(1024).decode('utf-8').strip()
            
            if not username:
                client_socket.close()
                return
            
            # Add client to the list
            with self.lock:
                self.clients.append(client_socket)
                self.usernames[client_socket] = username
            
            # Notify all clients about the new user
            join_msg = f"[{self.get_timestamp()}] {username} joined the chat!"
            print(join_msg)
            self.log_message(join_msg)
            self.broadcast(join_msg, client_socket)
            
            # Send welcome message to the new client
            welcome_msg = f"[{self.get_timestamp()}] Welcome to the chat, {username}!"
            client_socket.send(welcome_msg.encode('utf-8'))
            
            # Listen for messages from this client
            while True:
                message = client_socket.recv(1024).decode('utf-8')
                
                if not message:
                    break
                
                # Format and broadcast the message
                formatted_msg = f"[{self.get_timestamp()}] {username}: {message}"
                print(formatted_msg)
                self.log_message(formatted_msg)
                self.broadcast(formatted_msg, client_socket)
                
        except ConnectionResetError:
            pass
        except Exception as e:
            print(f"[ERROR] {e}")
        finally:
            # Remove client and notify others
            if client_socket in self.clients:
                with self.lock:
                    self.clients.remove(client_socket)
                    if client_socket in self.usernames:
                        username = self.usernames[client_socket]
                        del self.usernames[client_socket]
                
                if username:
                    leave_msg = f"[{self.get_timestamp()}] {username} left the chat."
                    print(leave_msg)
                    self.log_message(leave_msg)
                    self.broadcast(leave_msg, None)
            
            client_socket.close()
    
    def broadcast(self, message, sender_socket):
        """Broadcast message to all clients except sender"""
        with self.lock:
            for client in self.clients:
                if client != sender_socket:
                    try:
                        client.send(message.encode('utf-8'))
                    except:
                        # If sending fails, remove the client
                        if client in self.clients:
                            self.clients.remove(client)
                        if client in self.usernames:
                            del self.usernames[client]
    
    def log_message(self, message):
        """Save message to log file"""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(message + '\n')
        except Exception as e:
            print(f"[LOG ERROR] {e}")
    
    def get_timestamp(self):
        """Get formatted timestamp"""
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def shutdown(self):
        """Shutdown the server gracefully"""
        log_msg = f"[{self.get_timestamp()}] Server shutting down..."
        print(log_msg)
        self.log_message(log_msg)
        
        with self.lock:
            for client in self.clients:
                try:
                    client.close()
                except:
                    pass
        
        self.server_socket.close()
        sys.exit(0)

if __name__ == "__main__":
    server = ChatServer()
    print("=" * 50)
    print("     PYTHON LAN CHAT SERVER")
    print("=" * 50)
    server.start()
