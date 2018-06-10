from pyatc import PyATC
import os
import filecmp

print_prefix = "===== "
path = "data/"

print(print_prefix+"TESTING READING ATC FILE")
print("Reading ATC file")
atc = PyATC.read_file(path+"in.atc")
print("Checking that the recording duration is correct")
assert(atc.get_recording_duration() == 30)

#Try loading a v4 file that should fail
print("Trying to read ATC v4 file (should raise exception)")
failed = False
try:
    PyATC.read_file(path+"in_v4.atc")
except:
    failed = True
assert(failed)

#Test json
print(print_prefix+"TESTING TO/FROM JSON")
print("Writing to json")
atc.write_json_to_file(path+"out.json")
print("Reading from json")
atc_from_json = PyATC.read_json_file(path+"out.json")
print("Removing json file")
os.remove(path+"out.json")
assert(atc == atc_from_json)


print(print_prefix+"TESTING TO/FROM ATC")
print("Writing to ATC")
atc.write_to_file(path+"out.atc")

#Does in.atc === out.atc?
print("Validating that the newly created file equals the input file")
assert(filecmp.cmp(path+"in.atc", path+"out.atc", shallow = False))

print("Reading the newly written ATC")
atc2 = PyATC.read_file(path+"out.atc")

print("Removing newly created atc")
os.remove(path+"out.atc")
assert(atc == atc2)

print(print_prefix+"TESTING TO EDF")
print("Writing EDF file")
atc.write_edf_to_file(path+"out.edf")
print("Validating contents of the written EDF")
assert(filecmp.cmp(path+"out.edf", path+"edf_target.edf", shallow = False))
print("Removing written EDF")
os.remove(path+"out.edf")
