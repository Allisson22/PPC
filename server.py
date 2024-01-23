import sysv_ipc
import time

key = 128

que = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)

on = True
while on :
    mess,_ = que.receive()
    print(mess.decode())
    time.sleep(5)