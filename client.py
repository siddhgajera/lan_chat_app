import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox

# Configuration
SERVER_HOST = '127.0.0.1'  # Change to server's IP for actual LAN use
SERVER_PORT = 55555

class ChatClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.username = ""
        self.is_muted = False
        self.is_connected = False

        # UI Setup
        self.root = tk.Tk()
        self.root.title("LAN Chat App")
        self.root.configure(bg="#2c3e50")

        self.setup_login_ui()

    def setup_login_ui(self):
        self.login_frame = tk.Frame(self.root, bg="#2c3e50")
        self.login_frame.pack(pady=20, padx=20)

        tk.Label(self.login_frame, text="Enter username:", fg="white", bg="#2c3e50", font=("Arial", 12)).pack()
        self.username_entry = tk.Entry(self.login_frame, font=("Arial", 12))
        self.username_entry.pack(pady=10)
        self.username_entry.bind("<Return>", lambda e: self.connect())

        self.connect_btn = tk.Button(self.login_frame, text="Connect", command=self.connect, bg="#3498db", fg="white", font=("Arial", 10, "bold"))
        self.connect_btn.pack()

    def setup_chat_ui(self):
        self.login_frame.pack_forget()

        self.chat_frame = tk.Frame(self.root, bg="#2c3e50")
        self.chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.chat_area = scrolledtext.ScrolledText(self.chat_frame, wrap=tk.WORD, state=tk.DISABLED, bg="#ecf0f1", font=("Arial", 10))
        self.chat_area.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.input_frame = tk.Frame(self.chat_frame, bg="#2c3e50")
        self.input_frame.pack(fill=tk.X)

        self.msg_entry = tk.Entry(self.input_frame, font=("Arial", 11))
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.msg_entry.bind("<Return>", lambda e: self.send_message())

        self.send_btn = tk.Button(self.input_frame, text="Send", command=self.send_message, bg="#2ecc71", fg="white", font=("Arial", 10, "bold"))
        self.send_btn.pack(side=tk.RIGHT)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def connect(self):
        self.username = self.username_entry.get().strip()
        if not self.username:
            messagebox.showwarning("Warning", "Username cannot be empty!")
            return

        try:
            self.client_socket.connect((self.host, self.port))
            self.client_socket.send(self.username.encode('utf-8'))
            self.is_connected = True
            
            self.setup_chat_ui()
            
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not connect to server: {e}")

    def send_message(self):
        msg = self.msg_entry.get()
        if not msg:
            return

        self.msg_entry.delete(0, tk.END)

        if msg == "/exit":
            self.on_closing()
            return
        
        if msg == "/mute":
            self.is_muted = not self.is_muted
            status = "muted" if self.is_muted else "unmuted"
            self.display_message(f"SYSTEM: Chat is now {status}.")
            return

        try:
            self.client_socket.send(msg.encode('utf-8'))
            self.display_message(f"You: {msg}")
        except:
            self.display_message("SYSTEM: Failed to send message.")

    def receive_messages(self):
        while self.is_connected:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if not message:
                    break
                
                if not self.is_muted or "SERVER:" in message:
                    self.display_message(message)
            except:
                break
        
        if self.is_connected:
            self.display_message("SYSTEM: Disconnected from server.")
            self.is_connected = False

    def display_message(self, message):
        self.chat_area.configure(state=tk.NORMAL)
        self.chat_area.insert(tk.END, message + "\n")
        self.chat_area.configure(state=tk.DISABLED)
        self.chat_area.yview(tk.END)

    def on_closing(self):
        if self.is_connected:
            try:
                self.client_socket.send("/exit".encode('utf-8'))
            except:
                pass
        self.is_connected = False
        self.client_socket.close()
        self.root.destroy()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    client = ChatClient(SERVER_HOST, SERVER_PORT)
    client.run()
