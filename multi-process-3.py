import multiprocessing as mp
import os

def foo(q):
    q.put('Hello {}'.format(os.getpid()))

if __name__ == '__main__':
    mp.set_start_method('fork')
    q = mp.Queue()
    p = mp.Process(target=foo, args=(q,))
    p.start()
    print(q.get())
    p.join()

    p = mp.Process(target=foo, args=(q,))
    p.start()
    print(q.get())
    p.join()
