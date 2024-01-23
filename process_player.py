import sysv_ipc
import time

key = 128

que = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)

on = True
while on :
    l = "thomzs bleu\n prout"
    que.send(l.encode())
    time.sleep(5)