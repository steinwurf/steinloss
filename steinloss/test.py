import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # For UDP

udp_host = socket.gethostname()  # Host IP
udp_port = 5050  # specified port to connect

# print type(sock) ============> 'type' can be used to see type
# of any variable ('sock' here)
print(udp_host)

sock.bind(('', udp_port))

while True:
    print("Waiting for client...")
    data, addr = sock.recvfrom(1024)  # receive data from client
    print("Received Messages:", data, " from", addr)
