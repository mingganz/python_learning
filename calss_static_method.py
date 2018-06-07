class Pets:
    name = 'This is a Pet'
    @classmethod
    def about(cls):
        print(cls.name)

class Dogs(Pets):
    name = 'This is a Dog'

class Cats(Pets):
    name = 'This is a Cat'

def main():
    p = Pets()
    p.about()

    d = Dogs()
    d.about()

    c = Cats()
    c.about()

    print(issubclass(Dogs, Pets))

if __name__ == '__main__':
    main()

