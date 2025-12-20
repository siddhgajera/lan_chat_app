import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog
import sys
import datetime

class ChatClient:
    def __init__(self, host='127.0.0.1', port=5555):
        self.host = host
        self.port = port
        self.client_socket = None
        self.username = None
        self.running = False
        self.muted = False
        
        # Create GUI
        self.window = tk.Tk()
        self.window.title("LAN Chat Application")
        self.window.geometry("600x500")
        self.window.configure(bg="#2c3e50")
        
        # Setup GUI components
        self.setup_gui()
        
        # Connect to server
        self.connect_to_server()
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_gui(self):
        """Setup the GUI components"""
        # Title Label
        title_frame = tk.Frame(self.window, bg="#34495e", pady=10)
        title_frame.pack(fill=tk.X)
        
        title_label = tk.Label(
            title_frame, 
            text="💬 LAN Chat Room", 
            font=("Arial", 18, "bold"),
            bg="#34495e",
            fg="#ecf0f1"
        )
        title_label.pack()
        
        # Status Label
        self.status_label = tk.Label(
            title_frame,
            text="Connecting...",
            font=("Arial", 10),
            bg="#34495e",
            fg="#95a5a6"
        )
        self.status_label.pack()
        
        # Chat display area
        chat_frame = tk.Frame(self.window, bg="#2c3e50")
        chat_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg="#ecf0f1",
            fg="#2c3e50",
            state=tk.DISABLED,
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for styling
        self.chat_display.tag_config("system", foreground="#7f8c8d", font=("Consolas", 9, "italic"))
        self.chat_display.tag_config("user", foreground="#2980b9", font=("Consolas", 10, "bold"))
        self.chat_display.tag_config("message", foreground="#2c3e50")
        self.chat_display.tag_config("muted", foreground="#e74c3c", font=("Consolas", 9, "italic"))
        
        # Input area
        input_frame = tk.Frame(self.window, bg="#34495e", pady=10)
        input_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.message_entry = tk.Entry(
            input_frame,
            font=("Arial", 11),
            bg="#ecf0f1",
            fg="#2c3e50",
            relief=tk.FLAT,
            insertbackground="#2c3e50"
        )
        self.message_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 5), ipady=8)
        self.message_entry.bind("<Return>", lambda e: self.send_message())
        
        self.send_button = tk.Button(
            input_frame,
            text="Send",
            command=self.send_message,
            font=("Arial", 11, "bold"),
            bg="#27ae60",
            fg="white",
            relief=tk.FLAT,
            padx=20,
            cursor="hand2",
            activebackground="#229954"
        )
        self.send_button.pack(side=tk.RIGHT, padx=(5, 10))
        
        # Help text
        help_text = "Commands: /exit (quit) | /mute (toggle notifications)"
        help_label = tk.Label(
            self.window,
            text=help_text,
            font=("Arial", 8),
            bg="#2c3e50",
            fg="#95a5a6"
        )
        help_label.pack(pady=(0, 5))
    
    def connect_to_server(self):
        """Connect to the chat server"""
        try:
            # Get username from user
            self.username = simpledialog.askstring(
                "Username",
                "Enter your username:",
                parent=self.window
            )
            
            if not self.username:
                messagebox.showerror("Error", "Username is required!")
                self.window.destroy()
                return
            
            # Connect to server
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            
            # Receive username request and send username
            request = self.client_socket.recv(1024).decode('utf-8')
            if request == "USERNAME":
                self.client_socket.send(self.username.encode('utf-8'))
            
            self.running = True
            self.status_label.config(text=f"Connected as: {self.username}", fg="#27ae60")
            self.window.title(f"LAN Chat - {self.username}")
            
            # Start receiving messages in a separate thread
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            self.display_message("Connected to chat server!", "system")
            
        except ConnectionRefusedError:
            messagebox.showerror(
                "Connection Error",
                "Could not connect to server. Please make sure the server is running."
            )
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            self.window.destroy()
    
    def receive_messages(self):
        """Receive messages from server"""
        while self.running:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message:
                    self.display_message(message, "server")
                else:
                    break
            except:
                break
        
        self.running = False
    
    def send_message(self):
        """Send message to server"""
        message = self.message_entry.get().strip()
        
        if not message:
            return
        
        # Clear input field
        self.message_entry.delete(0, tk.END)
        
        # Handle commands
        if message.startswith('/'):
            self.handle_command(message)
            return
        
        # Send message to server
        try:
            self.client_socket.send(message.encode('utf-8'))
            # Display own message
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            self.display_message(f"[{timestamp}] You: {message}", "own")
        except Exception as e:
            self.display_message(f"Failed to send message: {e}", "system")
    
    def handle_command(self, command):
        """Handle client commands"""
        command = command.lower()
        
        if command == '/exit':
            self.on_closing()
        elif command == '/mute':
            self.muted = not self.muted
            status = "ON" if self.muted else "OFF"
            self.display_message(f"🔇 Mute mode: {status}", "muted")
        else:
            self.display_message(f"Unknown command: {command}", "system")
    
    def display_message(self, message, msg_type="server"):
        """Display message in chat window"""
        self.chat_display.config(state=tk.NORMAL)
        
        # Don't display server messages if muted (except system messages)
        if self.muted and msg_type == "server" and "joined" not in message and "left" not in message:
            self.chat_display.config(state=tk.DISABLED)
            return
        
        if msg_type == "system" or msg_type == "muted":
            self.chat_display.insert(tk.END, message + "\n", "system")
        elif msg_type == "own":
            self.chat_display.insert(tk.END, message + "\n", "user")
        else:
            # Parse server messages
            self.chat_display.insert(tk.END, message + "\n", "message")
        
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def on_closing(self):
        """Handle window closing"""
        if self.running:
            try:
                self.running = False
                self.client_socket.close()
            except:
                pass
        
        self.window.destroy()
        sys.exit(0)
    
    def run(self):
        """Run the GUI"""
        self.window.mainloop()

if __name__ == "__main__":
    # You can change the host IP to connect to a server on LAN
    # For example: client = ChatClient(host='192.168.1.100')
    client = ChatClient(host='127.0.0.1', port=5555)
    client.run()
