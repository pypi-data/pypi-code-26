# network tools
import urllib.request
import urllib.parse
import requests
import json
import platform
# threading tools
import queue
import threading
import sys
import subprocess
from time import time
import BinaryString

API00 = 'http://35.197.80.18:3000/binary'
API10 = 'http://35.197.80.18:3000/binary'
API01 = 'http://35.197.80.18:3000/binary'
API11 = 'http://35.197.80.18:3000/binary'

SIGNATURE = 'BRUCK'

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

    path = BinaryString.getMutationPath(seq, stored_paths, assemble)

    return path

def remoteAnswer(answers, seq, assemble=False):
    start_time = time()
    # format data to post
    raw_data = BinaryString.binaryToString(seq)
    data = raw_data.encode()
    
    # choose which server to call
    seed = BinaryString.get_seed(seq)
    
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

    print("remote result! time:", time() - start_time)
    answers.put(response.read().decode())

def localPythonAnswer(answers, seq, assemble=False):
    # start time
    start_time = time()
    # obtain and print result
    result = SIGNATURE + str(getMutationPathWrapperReal(seq, assemble=assemble))
    # print(result)
    end_time = time()

    print("local result! time:", end_time - start_time)
    answers.put(result)

def localGoAnswer(answers, seq, assemble=False):
    start_time = time()
    seq_str = BinaryString.binaryToString(seq)
    result = subprocess.check_output([r"./heuristic_cache/" + get_go_executable(), "-target=" + seq_str, "-full=" + str(assemble)])
    result = str(result, 'utf-8')
    end_time = time();
    print("go result! time:", end_time - start_time)
    answers.put(result)

def is_answer_valid(answer):
    return True or answer.startswith(SIGNATURE)

def get_answer(seq, assemble=False):
    functions = [remoteAnswer, localPythonAnswer, localGoAnswer]
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


def compute_initial_heuristic(seq, assemble=False):
    raise Exception(get_answer(seq, assemble))

def solve_main(seq, assemble):
    seq = BinaryString.stringToBinary(seq)

    print(get_answer(seq, assemble=assemble))
    
    
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
