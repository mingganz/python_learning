import trees

def main():
    myData, labels = trees.createDataSet()
    print myData

    shannonEhnt = trees.calcShannonEnt(myData)
    print shannonEhnt

    myData[0][-1] = 'maybe'
    print myData

    shannonEhnt = trees.calcShannonEnt(myData)
    print shannonEhnt

    print trees.splitDataSet(myData, 0 ,1)

    print trees.chooseBestFeatureToSplit(myData)

if __name__ == "__main__":
    main()