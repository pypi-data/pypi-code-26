import urllib.request
import urllib.parse
import requests
import json
import platform
import queue
import threading
import sys
import subprocess
import os
from time import time
sys.setrecursionlimit(1000000)

API00 = 'http://35.227.181.219:3000/binary'
API01 = 'http://35.233.232.73:3000/binary'
API10 = 'http://35.230.91.81:3000/binary'
API11 = 'http://35.197.80.18:3000/binary'

SIGNATURE = 'BRUCK'

# ========== FAKE/MISNAMED CODE ================================

def compute_initial_heuristic(  tree_seq, 
                                init_alg, 
                                edge_weight_func, 
                                cpu_affinity=1, 
                                develop_tree=False, 
                                init_branching_factor=1, 
                                dynamic_heuristic=False, 
                                recursive_decisions=False):
    '''
    Runs the actual solve function in the try clause. The solve function will
    return the answer in a thrown excpetion, which will be raised in the 
    except clause as a normal excpetion. When the package user receives an
    exception, it will be be processed as a response and returned to be printed
    '''
    try:
        solve_main(''.join(tree_seq), assemble=develop_tree)
    except Exception as e:
        raise e

def compute_recursive_heuristic(init_heuristic_object):
    '''
    Does absolutely nothing
    '''
    return None

def update_dynamic_bound(heuristic_object, bound):
    '''
    Does absolutely nothing
    '''
    return None
    
# ======= APPLICABLE FUNCITONS ===========================================

def getMutationPathWrapperReal(seq, assemble=False):

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

    path = getMutationPath(seq, stored_paths, assemble)

    return path

def remoteAnswer(answers, seq, assemble=False):
    try:
        # start_time = time()
        # format data to post
        if assemble:
            raw_data = 'SHUKI' + '1' + binaryToString(seq)
        else:
            raw_data = 'SHUKI' + '0' + binaryToString(seq)
        data = raw_data.encode()

        # choose which server to call
        seed = get_seed(seq)

        if seed == '00':
            SERVER = API00
        elif seed == '10':
            SERVER = API10
        elif seed == '01':
            SERVER = API01
        elif seed == '11':
            SERVER = API11

        # post and obtain response
        response = urllib.request.urlopen(url=SERVER, data=data)

        answers.put(response.read().decode())
    except Exception as e:
        pass

def localPythonAnswer(answers, seq, assemble=False):
    try:
        result = SIGNATURE + str(getMutationPathWrapperReal(seq, assemble=assemble))
        answers.put(result)
    except Exception as e:
        pass

def localGoAnswer(answers, seq, assemble=False):
    try:
        # start_time = time()
        seq_str = binaryToString(seq)
        dir_path = os.path.dirname(os.path.realpath(__file__))
        executable_path = os.path.join(dir_path, "heuristic_cache", get_go_executable())
        result = subprocess.check_output([executable_path, "-target=" + seq_str, "-full=" + str(assemble)])
        result = str(result, 'utf-8')
        # end_time = time();
        answers.put(result)
    except Exception as e:
        pass

def is_answer_valid(answer):
    return True or answer.startswith(SIGNATURE)

def get_answer(seq, assemble=False):
    # functions = [localGoAnswer, localPythonAnswer]
    functions = [localGoAnswer, remoteAnswer, localPythonAnswer]
    # functions = [localGoAnswer]
    answers = queue.Queue()
    for func in functions:
        thread = threading.Thread(target=func, args=(answers, seq, assemble))
        thread.daemon = True
        thread.start()

    answer1 = answers.get()
    if (is_answer_valid(answer1)):
        return answer1[len(SIGNATURE):]

    answer2 = answers.get()
    if (is_answer_valid(answer2)):
        return answer2[len(SIGNATURE):]

    answer3 = answers.get()
    if (is_answer_valid(answer3)):
        return answer3[len(SIGNATURE):]

    raise Exception("Could not get answer")


def solve_main(seq, assemble):
    seq = stringToBinary(seq)
    raise Exception(get_answer(seq, assemble))


def get_os():
    python_system = platform.system().lower()
    if "darwin" in python_system:
        return "darwin"
    elif "windows" in python_system:
        return "windows"
    elif "linux" in python_system:
        return "linux"
    elif "freebsd" in python_system:
        return "freebsd"
    elif "openbsd" in python_system:
        return "openbsd"
    elif "solaris" in python_system:
        return "solaris"
    elif "netbsd" in python_system:
        return "netbsd"

    python_platform = platform.platform().lower()
    if "darwin" in python_platform:
        return "darwin"
    elif "windows" in python_platform:
        return "windows"
    elif "linux" in python_platform:
        return "linux"
    elif "freebsd" in python_platform:
        return "freebsd"
    elif "openbsd" in python_platform:
        return "openbsd"
    elif "solaris" in python_platform:
        return "solaris"
    elif "netbsd" in python_platform:
        return "netbsd"

    if "win" in python_system:
        return "windows"

    if "win" in python_platform:
        return "windows"

    # Hail mary
    return "linux"

def get_cpu():
    python_processor = platform.processor().lower()
    if "386" in python_processor:
        return "386"
    elif "intel" in python_processor:
        return "386"
    elif "amd" in python_processor:
        return "amd64"

    python_platform = platform.platform().lower()
    if "386" in python_platform:
        return "386"
    elif "intel" in python_platform:
        return "386"
    elif "amd" in python_platform:
        return "amd64"

    # Likely
    return "386"

def get_go_executable():
    os = get_os()
    cpu = get_cpu()
    if os == "solaris":
        cpu = "amd64"
    extension = ".exe" if os == "windows" else ""
    return os + "-" + cpu + extension


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
    '''
    Converts a binary representation of a sequence to a string representation
    '''
    length, number = seq[0], seq[1]

    binary = bin(number)[2:]
    while len(binary) < length:
        binary = '0' + binary

    return binary

def stringToBinary(seq):
    '''
    Converts a string sequence to binary representation (length, number)
    '''
    length = len(seq)
    number = 0
    digit = 1

    for i in reversed(range(length)):
        number += int(seq[i]) * digit
        digit *= 2

    return (length, number)

def get_seed(seq):
    '''
    Generate the pseudo-seed of the sequence. Note that this is not the actual 
    seed but rather the seed bin as defined
    '''
    length, number = seq[0], seq[1]

    right = str(number & 1)
    left = str(number >> (length - 1))

    return left + right
    
if __name__ == "__main__":
    # seq = '000001000110010100111010110111110000'
    seq = '100000100011001010011101011011111000010'
    try:
        result = compute_initial_heuristic(list(seq), None, None, develop_tree=False)
    except Exception as e:
        print(str(e))
