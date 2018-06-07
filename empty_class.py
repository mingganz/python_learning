class MyData():
    'This is my Data class'
    pass

def main():
    data = MyData()
    data.x = 4
    data.y = 5
    print("data.x(%d) + data.y(%d) = %d" % (data.x, data.y, data.x + data.y))

if __name__ == '__main__':
    main()