import sys
from time import time
sys.setrecursionlimit(1000000)

def getMutationPathWrapper(seq, assemble=False):

    if assemble:
        stored_paths = {
            (1, 0) : [(1, 0)],
            (1, 1) : [(1, 1)],
            (2, 1) : [(2, 1)],
            (2, 2) : [(2, 2)],
            (3, 2) : [(3, 2)],
            (3, 5) : [(3, 5)]
        }

    else:
        stored_paths = {
            (1, 0) : 0,
            (1, 1) : 0,
            (2, 1) : 0,
            (2, 2) : 0,
            (3, 2) : 0,
            (3, 5) : 0
        }

    path = getMutationPath(seq, stored_paths)

    return path

def getMutationPath(seq, stored_paths, assemble):
    '''
    Returns the shortest duplication path from seed to ending string
    '''

    # start = time()
    if seq in stored_paths:
        return stored_paths[seq]

    length, number = seq[0], seq[1]

    # first size of window to examine
    largest_mask = (1 << length) - 1
    max_dup_size = length >> 1

    best_path = None if assemble else sys.maxsize

    # Iterate through every possible even subsequence length
    for dup_size in range(1, max_dup_size + 1):
        # The masks for comparing two substrings
        right_mask = (1 << dup_size) - 1
        left_mask = right_mask << dup_size
        right_child_mask = right_mask
        left_child_mask = largest_mask & ~(right_child_mask | left_mask)
        child_size = length - dup_size

        # Shift windows until out of bounds
        while left_mask <= largest_mask:
            # Check if equal substrings
            if (left_mask & number) >> dup_size == (right_mask & number):
                left_child = (number & left_child_mask) >> dup_size
                right_child = number & right_child_mask
                child = (child_size, left_child | right_child)
                if assemble:
                    child_path = getMutationPath(child, stored_paths, assemble)
                    if (best_path is None) or (len(child_path) < len(best_path)):
                        best_path = child_path
                else:
                    best_path = min(best_path, getMutationPath(child, stored_paths, assemble))


            right_mask <<= 1
            left_mask <<= 1
            right_child_mask <<= 1
            right_child_mask += 1
            left_child_mask = largest_mask & ~(right_child_mask | left_mask)

    if assemble:
        best_path.append(seq)
        stored_paths[seq] = best_path
        return best_path
    else:
        path = best_path + 1
        stored_paths[seq] = path
        return path

def binaryToString(seq):
    length, number = seq[0], seq[1]

    binary = bin(number)[2:]
    while len(binary) < length:
        binary = '0' + binary

    return binary

def stringToBinary(seq):
    """
    Converts a string sequence to binary representation (length, number)
    """
    length = len(seq)
    number = 0
    digit = 1

    for i in reversed(range(length)):
        number += int(seq[i]) * digit
        digit *= 2

    return (length, number)
    
def get_seed(seq):
    length, number = seq[0], seq[1]
    
    right = str(number & 1)
    left = str(number >> (length - 1))
    
    return left + right

if __name__ == "__main__":
    start = time()
    target = stringToBinary("000001000110010100111010110111110000")
    print(getMutationPathWrapper(target, False))
    end = time()
    print("Total time - " + str(end - start))
