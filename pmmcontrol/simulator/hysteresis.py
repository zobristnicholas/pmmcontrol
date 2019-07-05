import numpy as np
import matplotlib.pyplot as plt

class Hysteresis():
    def __init__(self, xSaturation, ySaturation, yRemanence, N=10, xParam='', yParam=''):

        if not isinstance(N, int):
            raise ValueError("Matrix size must be an integer value")

        if not (N%2 == 0):
            raise ValueError("Matrix size must be even")

        if not ySaturation > yRemanence:
            raise ValueError("The y-intercept (remanence) must be lower than the ySaturation value")

        # store size of matrix
        self.__size = N

        # configure plotting details
        self.__xLabel = xParam
        self.__yLabel = yParam

        # matrix of relays that can be flipped up (+1) or down (-1)
        self.__relay = np.zeros((N,N))

        # matrix of weights to be applied to each relay
        self.__weights = np.ones((N,N))

        # fill the weights matrix to adjust behavior of hysteresis
        self.__diagFill(self.__weights)

        self.__xSaturation = xSaturation
        self.__ySaturation = ySaturation
        self.__yRemanence = yRemanence

        # Scale according to input parameters
        self.__parameterScale()

        # scaling of plot window
        self.__yMax = self.__sumHalf(self.__weights, np.ones((N,N)))

        # fill the relay matrix in starting position
        self.__relayFill()

        # starting point
        self.__x = int(0)
        self.__y = self.__sumHalf(self.__relay, self.__weights)

        # list of data points to be appended to
        self.__xValues = np.append(np.array([]), self.__x)
        self.__yValues = np.append(np.array([]), self.__y)

    def setX(self, x):
        '''
        Change x-coordinate of hysteresis function
        '''

        # need to use an integer value (xScaled) when dealing with the relay matrix
        xScaled = int(x * self.__xScale)

        if xScaled > self.__x:
            for i in range(self.__x, xScaled):
                self.increment('up')
        if xScaled < self.__x:
            for i in range(xScaled, self.__x):
                self.increment('down')

        return self.__y

    def increment(self, direction):
        '''
        Change x-coordinate of hysteresis plot by +/- 1 depending on if direction is set as 'up' or 'down'
        '''

        if not (direction == 'up' or direction == 'down'):
            raise ValueError("\"direction\" must be set to either \"up\" or \"down\"")

        if direction == 'up':

            # only adjust matrix if x-coord is within +/- N/2
            # otherwise let x-coord increase without change of y-coord. This represents saturation
            if self.__x >= -self.__size/2 and self.__x < self.__size/2:

                #fill one row (at current coordinate) of relay matrix with "up" relays
                self.__relay[self.__size - (self.__x + self.__size//2)- 1].fill(1)

            self.__x = self.__x + 1

        if direction == 'down':
            # only adjust matrix if x-coord is within +/- N/2
            # otherwise let x-coord increase without change of y-coord. This represents saturation
            if self.__x > -self.__size/2 and self.__x <= self.__size/2:

                #fill one column of relay matrix with "down" relays
                self.__relay[:, (self.__x + self.__size//2) - 1].fill(-1)

            self.__x = self.__x - 1

        # update y-coord using a weighted sum of relay matrix
        self.__y = self.__sumHalf(self.__relay, self.__weights)

        # update coordinate lists
        self.__xValues = np.append(self.__xValues, self.__x / self.__xScale)
        self.__yValues = np.append(self.__yValues, self.__y)

        #FOR TESTING PURPOSES
        #self.plot()
        #self.__printHalf(self.__relay)

        return True

    def getXYData(self):
        '''
        Returns 2D array with first index xValues and second index yValues
        '''
        return np.array([self.__xValues, self.__yValues])

    def plot(self):
        '''
        Can be used to visually inspect relay weight distribution
        '''

        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)

        xlim = ((self.__size / self.__xScale) / 1.7)
        ylim = self.__yMax * 1.1

        ax.plot(self.__xValues, self.__yValues)
        ax.set_xlim(-xlim , xlim)
        ax.set_ylim(-ylim, ylim)
        ax.set_xlabel(self.__xLabel)
        ax.set_ylabel(self.__yLabel)

        plt.show()

        return True

    def __parameterScale(self):
        # scale weights according to the remanence parameter
        remScale = self.__yRemanence / self.__weights[0:self.__size // 2, 0:self.__size // 2].sum()
        self.__weights = self.__weights * remScale

        satAdjust = np.ones((self.__size//2, self.__size//2))
        self.__diagFill(satAdjust)

        satAdjust = (self.__ySaturation - self.__yRemanence) * \
                    (satAdjust / (2 * self.__sumHalf(satAdjust, np.ones((self.__size//2, self.__size//2)))))

        self.__weights[0:self.__size // 2, self.__size//2: self.__size] = satAdjust
        self.__weights[self.__size//2: self.__size, 0:self.__size // 2] = satAdjust

        # scale x values according to the saturation parameter
        self.__xScale = (self.__size / 2) / self.__xSaturation

        self.__printHalf(self.__weights)

        return True

    def __diagFill(self, mat):
        '''
        Function for filling weight matrix
        '''

        # currently distributed as a gradient that decreases away from the center diagonal
        for n in range(0, self.__size):
            fill = 1-(1/(self.__size - 1) * n)
            fillArr = np.ones(self.__size - n) * fill
            np.fill_diagonal(mat[n:], fillArr)
            np.fill_diagonal(mat[:,n:], fillArr)

        return True

    def __relayFill(self):
        '''
        Optional function to set initial state of all relays
        '''
        np.fill_diagonal(self.__relay[0:], np.zeros(self.__size))
        for n in range(0, self.__size):
            np.fill_diagonal(self.__relay[n:], np.ones(self.__size - n))
            np.fill_diagonal(self.__relay[:,n:], -1 * np.ones(self.__size - n))


        return True

    def __sumHalf(self, mat1, mat2):
        '''
        Returns a scalar product of the upper-left triangle between two matrices
        '''

        if not mat1.shape == mat2.shape:
            raise ValueError("Matrix 1 and 2 must be the same shape")

        if not mat1.shape[0] == mat2.shape[1]:
            raise ValueError("Matrices must be square")

        size = mat1.shape[0]

        rowSum = np.zeros(size)

        # sum up scalar product of each row
        for row in range(0, size):
            row1 = mat1[row][:(size-row)]
            row2 = mat2[row][:(size-row)]
            rowSum[row] = np.dot(row1, row2)

        return np.sum(rowSum)

    def __printHalf(self, mat):
        '''
        Prints the upper-left half of a matrix
        '''

        size = mat.shape[0]

        for row in range(0, size):
            print(mat[row][:(size-row)])

        return True