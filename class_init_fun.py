class Graph:
    versin = 1.0
    info = [{'TT': 2010}]
    def __init__(self, name, author):
        self.name = name
        self.author = author
        print("__init__")

class AbsGraph(Graph):
    def __init__(self, name, author, style = 'Abs'):
        Graph.__init__(self, name, author)
        self.style = style
        print("ABS __init__")


def main():
    g = AbsGraph('Happy', 'Picaso')
    g.versin = 2.0
    print(g.versin)
    print(Graph.versin)

    print(g.info)
    g.info.append({'DD': 1983})
    print(g.info)
    print(Graph.info)

    print(g.__dict__)
    print(Graph.__dict__)

if __name__ == '__main__':
    main()