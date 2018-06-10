class Pets:
    name = 'This is a Pet'
    @classmethod
    def about(cls):
        print(cls.name)

    @staticmethod
    def info():
        print('static: info')

    def __new__(cls):
        print("Pets: %s" % cls.name)
        return cls

class Dogs(Pets):
    name = 'This is a Dog'

class Cats(Pets):
    name = 'This is a Cat'

def main():
    p = Pets()
    p.about()
    p.info()

    d = Dogs()
    d.about()
    d.info()

    c = Cats()
    c.about()

    print(issubclass(Dogs, Pets))

if __name__ == '__main__':
    main()

