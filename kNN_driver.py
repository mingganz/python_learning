import kNN
from numpy import *
import matplotlib
import matplotlib.pyplot as plt

def main():
    group,labels = kNN.createDataSet()

    predict = kNN.classify0([0, 0], group, labels, 3)

    print predict

    datingDataMat,datingLabels = kNN.file2matrix('datingTestSet.txt')
    print datingDataMat
    print datingLabels

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(datingDataMat[:, 0], datingDataMat[:, 1], 15.0*array(datingLabels), 15.0*array(datingLabels))
    plt.xlabel('Percentage of Time Spent Playing Video Games')
    plt.ylabel('Liters of Ice Cream Consumed Per Week')
    plt.show()

print __name__
if __name__ == "__main__":
    main()