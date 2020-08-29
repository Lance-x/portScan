import os
import socket
from threading import Thread
import threading
from queue import Queue
from time import sleep

PORT = 3389
IP_FILE = r'ips.txt'
RESULT_FILE = r'result3389.txt'


def port_scan(ip_queue: Queue, result_queue: Queue, port):
    while True:
        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sk.settimeout(1)
        ip = ip_queue.get()
        if ip == "0" or ip == "":
            ip_queue.put("0")
            break
        message = "{:<15}{:<18}{:<6}".format(threading.current_thread().name, ip, port)
        content = ""
        # noinspection PyBroadException
        try:
            sk.connect((ip, port))
            content += message + 'True '
            # result_queue.put(message + 'ok')
            print(message + 'True')
        except Exception:
            content += message + 'False'
            # result_queue.put(message + 'False')
            print(message + 'False')
        sk.close()

        result = os.system(r'ping -n 1 {}'.format(ip))
        if result == 0:
            ping = "True"
        else:
            ping = "False"
        content += '\tPing: {:<6}'.format(ping)
        result_queue.put(content)


def file_read():
    with open(IP_FILE, 'r', encoding='utf-8') as f:
        content = list(f.read().split('\n'))
    return content


def put_queue(f, ip_queue: Queue):
    for ip in f:
        ip_queue.put(ip)
    ip_queue.put("0")


def write_file(result_queue: Queue):
    with open(RESULT_FILE, 'a') as f:
        while True:
            result = result_queue.get()
            if result == "0":
                break
            f.writelines(result + "\n")


if __name__ == '__main__':
    q = Queue(maxsize=300)
    qw = Queue(maxsize=100)
    a = file_read()
    rt1 = Thread(name="Threading-rt1", target=put_queue, args=(a, q))
    wt1 = Thread(name="Threading-Wt1", target=write_file, args=(qw,))
    t = []
    rt1.start()
    wt1.start()
    sleep(1)
    for i in range(20):
        t.append("t{}".format(i))
        t[i] = Thread(name="Threading-{}".format(t[i]), target=port_scan, args=(q, qw, PORT))
        t[i].start()
        sleep(0.01)
    while True:
        sleep(1)
        a = len(threading.enumerate())
        # print(a)
        if a == 2:
            qw.put("0")
            break
