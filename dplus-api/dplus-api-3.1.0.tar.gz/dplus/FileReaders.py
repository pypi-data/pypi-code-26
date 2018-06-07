import os
import json
import math
import numpy as np
from collections import OrderedDict


def handle_infinity(obj):
    if isinstance(obj, float):
        if obj==math.inf:
            return("inf")
        if obj==-math.inf:
            return("-inf")
    elif isinstance(obj, dict):
        return dict((k, handle_infinity(v)) for k, v in obj.items())
    elif isinstance(obj, list):
        return [handle_infinity(x) for x in obj]
    elif isinstance(obj, tuple):
        return map(handle_infinity, obj)
    return obj

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(MyEncoder, self).default(obj)


class SignalFileReader:
    def __init__(self, filename):
        self.signal_filename=filename
        self._read()

    def _read(self):
        self.expected_graph = OrderedDict()
        self.x_vec = []
        self.y_vec = []
        with open(self.signal_filename) as signal_file:
            for line in signal_file:
                if '#' in line:  # a header line
                    continue
                values = line.split()
                if len(values) > 1:  # two float values
                    try:
                        x = float(values[0])
                        y = float(values[1])
                        self.x_vec.append(x)
                        self.y_vec.append(y)
                        self.expected_graph[float(x)] = float(y)
                    except ValueError:  # in the c++ code, if they werne't floats, it just continued
                        continue


class Amplitude(object):
    def __init__(self):
        self.arr=[]
        self.header=[]

    @staticmethod
    def load(filename, qmax):
        a=Amplitude()
        a.read_amp(filename, qmax)
        return a

    def save(self, filename):
        with open(filename, 'wb') as f:
            for header in self.header:
                f.write(header)
            amps=np.float64(self.arr)
            amps.tofile(f)

    def _peek(self, File, length):
        pos = File.tell()
        data = File.read(length)
        File.seek(pos)
        return data

    def read_amp(self, name, qmax):
        f = open(name, "rb+")
        header = []
        offset = 0
        if self._peek(f, 1).decode('ascii') == '#':
            desc = f.read(2)
            tempdesc = desc.decode('ascii')
            if (tempdesc[1] == '@'):
                offset = np.fromfile(f, dtype=np.uint32, count=1, sep="")
                del_ = f.readline()
            elif (tempdesc[1] != '\n'):
                tmphead = f.readline()
                header.append(tmphead)

        while self._peek(f, 1).decode('ascii') == '#':
            header.append(f.readline())
        if offset > 0:
            f.seek(offset[0], 0)

        version_r = f.readline().rstrip()
        version = int(version_r.decode('ascii'))
        size_element_r = f.readline().rstrip()
        size_element = int(size_element_r.decode('ascii'))

        if size_element != int(2 * np.dtype(np.float64).itemsize):
            print("error in file: " + name + "dtype is not float64\n")
            exit(1)

        tmpGridsize_r = f.readline().rstrip()
        tmpGridsize = int(tmpGridsize_r.decode('ascii'))

        tmpExtras_r = f.readline().rstrip()
        tmpExtras = int(tmpExtras_r.decode('ascii'))
        Gridsize = (tmpGridsize - tmpExtras) * 2

        # Total size of the grid
        thetaDivisions = 3
        phiDivisions = 6

        stepSize = qmax / float(Gridsize / 2)
        self.stepSize = stepSize
        actualGridSize = Gridsize / 2 + tmpExtras

        i = actualGridSize
        totalsz = int((phiDivisions * i * (i + 1) * (3 + thetaDivisions + 2 * thetaDivisions * i)) / 6)
        totalsz = totalsz + 1
        totalsz = totalsz * 2

        step_size = np.fromfile(f, dtype=np.float64, count=1, sep="")

        Amplitude = np.fromfile(f, dtype=np.float64, count=totalsz, sep="")

        f.close()
        pos = 0
        header_List = []
        header_List.append(desc)
        pos = pos + len(desc)

        header_List.append(offset[0].tobytes())
        pos = pos + len(offset[0].tobytes())
        header_List.append(del_)
        pos = pos + len(del_)

        for i in header:
            header_List.append(i)
            pos = pos + len(i)
            header_List.append(del_)
            header_List.append(del_)
            pos = pos + 2 * len(del_)
        pos = np.int32(pos)
        if pos != offset[0]:
            header_List[1] = pos.tobytes()

        header_List.append(version_r + b"\n")
        header_List.append(size_element_r + b"\n")
        header_List.append(tmpGridsize_r + b"\n")
        header_List.append(tmpExtras_r + b"\n")
        header_List.append(step_size.tobytes())

        self.arr=Amplitude
        self.header=header_List

    def q_indices(self):
        if self.arr.__len__() == 0:
            return None;
        phiDivisions = 6
        thetaDivisions = 3
        DTP = np.int64
        for index in range(0,int(self.arr.__len__()/2) ):
            qI = np.int64(0)
            tI = np.int64(0)
            pI = np.int64(0)
            if index == 0:
                yield (qI,tI,pI)
                continue
            # This code was taken from d+ : JacobianSphereGrid::Fill and JacobianSphereGrid::IndicesFromIndex
            lqi = np.int64(np.int32(((3*index)/(thetaDivisions*phiDivisions))**(1/3.0)))
            bot = DTP((lqi * phiDivisions * (lqi + 1) * (3 + thetaDivisions + 2 * thetaDivisions * lqi))/6)
            if index > bot:
                lqi += 1
            lqi -= 1
            bot = DTP((lqi * phiDivisions * (lqi + 1) * (3 + thetaDivisions + 2 * thetaDivisions * lqi))/6)
            lqi += 1
            qi = int(lqi)
            rem = index - bot - 1

            thi = DTP(rem / (phiDivisions * qi))
            phi = DTP(rem % (phiDivisions * qi))

            qI = np.float64(qi) * self.stepSize
            tI =  math.pi * np.float64(thi) / np.float64(thetaDivisions * qi)
            pI = 2*math.pi * np.float64(phi) / np.float64(phiDivisions * qi);

            yield (qI,tI, pI)

    def num_indices(self):
        return int(self.arr.__len__()/2)

    def complex_amplitude_array(self):
        complex_arr = np.zeros((int(self.arr.__len__()/2), 1), dtype=np.complex)
        for index in range(0,complex_arr.__len__()):
            complex_arr[index] = self.arr[2*index] + 1j * self.arr[2*index+1]
        return complex_arr

class PDBFileReader:
    pass

