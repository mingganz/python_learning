class trick:
    def __init__(self, name='Musk'):
        self.name = name
        print(self.name)

    def disp(self):
        print('disp: {}'.format(self.name))

    def __call__(self, *args, **kwargs):
            self.name = args
            print(self.name)

if __name__ == '__main__':
    t = trick()
    t('Einstein')
    t.disp()
