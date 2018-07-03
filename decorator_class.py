class Decorator:
    def __init__(self, max):
        self.max = max
        self.count = 0

    def __call__(self, fun):
        self.fun = fun
        return self.call_fun

    def call_fun(self, *args, **kwargs):
        if self.max <= self.count:
            print("Already run {} times, you must exit!".format(self.max))
        else:
            self.fun(args, kwargs)
        self.count += 1

@Decorator(5)
def do_sth(*args, **kwargs):
    print('Play with decorator class! Is it fun?  Show me...')

if __name__ == '__main__':
    for i in range(10):
        do_sth()