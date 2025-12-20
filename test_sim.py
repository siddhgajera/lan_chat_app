import socket
import time

def simulate_client(username, messages):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', 55555))
        s.send(username.encode('utf-8'))
        time.sleep(1)
        
        for msg in messages:
            s.send(msg.encode('utf-8'))
            time.sleep(1)
            
        s.send("/exit".encode('utf-8'))
        s.close()
    except Exception as e:
        print(f"Error in {username}: {e}")

if __name__ == "__main__":
    from threading import Thread
    
    t1 = Thread(target=simulate_client, args=("Alice", ["Hello world!", "How is everyone?", "Testing /mute now"]))
    t2 = Thread(target=simulate_client, args=("Bob", ["Hi Alice!", "I am doing great.", "Nice app!"]))
    
    t1.start()
    t2.start()
    
    t1.join()
    t2.join()
    print("Simulation finished.")
