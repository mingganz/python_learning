from multiprocessing import Process
import os

def info(title):
    print(title)
    print('Module name: {}'.format(__name__))
    print('Parent process: {}'.format(os.getppid()))
    print('Process Id: {}'.format(os.getpid()))

def f(name):
    info('Function f')
    print('Hello {}'.format(name))

if __name__ == "__main__":
    info('Main process')
    p = Process(target=f, args=('bob', ))
    p.start()
    p.join()
