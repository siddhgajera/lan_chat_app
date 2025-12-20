# Python LAN Chat Application

A real-time chat application for Local Area Networks (LAN) built using Python's `socket`, `threading`, and `Tkinter` libraries.

## 🚀 Features
- **Real-time Messaging**: Broadcast messages to all connected clients instantly.
- **Multi-threaded Server**: Supports multiple users simultaneously.
- **Tkinter GUI**: A user-friendly desktop interface for chatting.
- **Activity Logging**: Automatically saves all chat history and events to `chat_logs.txt`.
- **In-Chat Commands**:
  - `/mute`: Toggle muting incoming messages from other users.
  - `/exit`: Securely disconnect from the chat.

## 🛠️ Requirements
- Python 3.x
- No external libraries required (uses standard Python libraries).

## 📂 Project Structure
- `server.py`: The backend that manages connections and message broadcasting.
- `client.py`: The frontend UI for users to connect and chat.
- `chat_logs.txt`: File where chat history is persisted.

## 📖 How to Run

### 1. Start the Server
Run the following command in a terminal to start the message relay server:
```bash
python server.py
```

### 2. Start Clients
Open separate terminal windows for each user you want to add and run:
```bash
python client.py
```

### 3. Usage
- Enter a **Username** and click **Connect**.
- Type your message in the text box and press **Enter** or click **Send**.
- To test by yourself, open at least two client windows to see messages being exchanged.

## 📝 Commands
| Command | Description |
| :--- | :--- |
| `/mute` | Stops printing new messages in the UI (System/Server messages still appear). |
| `/exit` | Closes the connection and the application. |

---
*Created as part of the LAN Chat App project.*
