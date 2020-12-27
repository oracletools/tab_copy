import time
import Queue
import sys
import threading
import subprocess
PIPE = subprocess.PIPE


def read_output(pipe, funcs):
    for line in iter(pipe.readline, ''):
        for func in funcs:
            func(line)
            # time.sleep(1)
    pipe.close()

def write_output(get):
    for line in iter(get, None):
        sys.stdout.write(line)

process = subprocess.Popen(
    ['random_print.py'], stdout=PIPE, stderr=PIPE, close_fds=True, bufsize=1)
q = Queue.Queue()
out, err = [], []
tout = threading.Thread(
    target=read_output, args=(process.stdout, [q.put, out.append]))
terr = threading.Thread(
    target=read_output, args=(process.stderr, [q.put, err.append]))
twrite = threading.Thread(target=write_output, args=(q.get,))
for t in (tout, terr, twrite):
    t.daemon = True
    t.start()
process.wait()
for t in (tout, terr):
    t.join()
q.put(None)
print(out)
print(err)