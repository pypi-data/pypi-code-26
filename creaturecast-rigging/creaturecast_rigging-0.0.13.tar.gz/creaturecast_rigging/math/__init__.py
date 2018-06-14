

def zero(m, n):
    # Create zero matrix
    new_matrix = [[0 for row in range(n)] for col in range(m)]
    return new_matrix

def convertMatrix(matrix):
    newMatrix = []
    mit = 0
    for itr in range(len(matrix)/4):
        newMatrix.append([matrix[mit], matrix[mit+1], matrix[mit+2], matrix[mit+3]])
        mit = mit + 4
    return newMatrix

def multMatrix(matrix1,matrix2):

    # Matrix multiplication
    if len(matrix1[0]) != len(matrix2):
        # Check matrix dimensions
        print 'Matrices must be m*n and n*p to multiply!'
    else:
        # Multiply if correct dimensions
        new_matrix = zero(len(matrix1),len(matrix2[0]))
        for i in range(len(matrix1)):
            for j in range(len(matrix2[0])):
                for k in range(len(matrix2)):
                    new_matrix[i][j] += matrix1[i][k]*matrix2[k][j]
        return new_matrix

def addList(list):
    return sum(list)

def addLists(list1, list2):
    return [L1 + L2 for L1, L2 in zip(list1, list2)]

def subtractLists(list1, list2):
    return [L1 - L2 for L1, L2 in zip(list1, list2)]

def averageLists(*args):
    newList = []
    zipList = zip(*args)
    for zz in zipList:
        newList.append(sum(zz))
    return newList


def multiplyLists(list1,list2):
    return [L1 * L2 for L1, L2 in zip(list1, list2)]

def divideLists(list1,list2):
    return [float(L1) / float(L2) for L1, L2 in zip(list1, list2)]

def negativeList(list):
    return [-L for L in list]

def squareList(list):
    newList = []
    for val in list:
        newList.append(val*val)
    return newList

def normalizeList(list):
    multVal =  1.0/float(max(list))
    return multiplyLists(list, [multVal]*len(list))

def iseven(number):
    if number%2==0:
        return True
    else:
        return False