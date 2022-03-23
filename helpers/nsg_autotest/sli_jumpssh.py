from dotenv import load_dotenv
from jumpssh import SSHSession
import os

load_dotenv()


os.putenv("jumpserver_ip", "205.206.214.248")
os.putenv("jumpserver_port", "22")
os.putenv("jumpserver_username", "x244425")

# jumpserver_ip = os.getenv("jumpserver_ip")
# jumpserver_port = os.getenv("jumpserver_port")
# jumpserver_username = os.getenv("jumpserver_username")
# jumpserver_password = os.getenv("jumpserver_password")

jumpserver_ip = "205.206.214.248"
jumpserver_port = "22"
jumpserver_username = "x244425"
jumpserver_password = "0512772669"

remote_ip = os.getenv("remote_ip")
remote_port = os.getenv("remote_port")
remote_username = os.getenv("remote_username")
remote_password = os.getenv("remote_password")

gateway_session = SSHSession(jumpserver_ip, jumpserver_username, port=jumpserver_port, password=jumpserver_password).open()

#remote_session = gateway_session.get_remote_session(remote_ip, port=remote_port, username=remote_username, password=remote_password, allow_agent=False, look_for_keys=False)
remote_session = gateway_session.get_remote_session(remote_ip, port=int(remote_port), username=remote_username, password=remote_password)
fl = open('R1.txt', 'w')
fl.write(remote_session.get_cmd_output('nsginfo'))
fl.close()
remote_session.close()
gateway_session.close()
