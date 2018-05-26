import os
import sys
import ctypes
import enum
import platform
import logging
import struct

from ctypes.wintypes import HANDLE, BOOL, DWORD, HWND, HINSTANCE, HKEY, LPVOID, LPWSTR, PBOOL
from ctypes import c_ulong, c_char_p, c_int, c_void_p, WinError, get_last_error

from privileges import enable_debug_privilege

if platform.system() != 'Windows':
	raise Exception('This script will ovbiously only work on Windows')

# https://stackoverflow.com/questions/1405913/how-do-i-determine-if-my-python-shell-is-executing-in-32bit-or-64bit-mode-on-os
IS_PYTHON_64 = False if (8 * struct.calcsize("P")) == 32 else True

class MINIDUMP_TYPE(enum.IntFlag): 
	MiniDumpNormal						  = 0x00000000
	MiniDumpWithDataSegs					= 0x00000001
	MiniDumpWithFullMemory				  = 0x00000002
	MiniDumpWithHandleData				  = 0x00000004
	MiniDumpFilterMemory					= 0x00000008
	MiniDumpScanMemory					  = 0x00000010
	MiniDumpWithUnloadedModules			 = 0x00000020
	MiniDumpWithIndirectlyReferencedMemory  = 0x00000040
	MiniDumpFilterModulePaths			   = 0x00000080
	MiniDumpWithProcessThreadData		   = 0x00000100
	MiniDumpWithPrivateReadWriteMemory	  = 0x00000200
	MiniDumpWithoutOptionalData			 = 0x00000400
	MiniDumpWithFullMemoryInfo			  = 0x00000800
	MiniDumpWithThreadInfo				  = 0x00001000
	MiniDumpWithCodeSegs					= 0x00002000
	MiniDumpWithoutAuxiliaryState		   = 0x00004000
	MiniDumpWithFullAuxiliaryState		  = 0x00008000
	MiniDumpWithPrivateWriteCopyMemory	  = 0x00010000
	MiniDumpIgnoreInaccessibleMemory		= 0x00020000
	MiniDumpWithTokenInformation			= 0x00040000
	MiniDumpWithModuleHeaders			   = 0x00080000
	MiniDumpFilterTriage					= 0x00100000
	MiniDumpValidTypeFlags				  = 0x001fffff
	
class WindowsBuild(enum.Enum):
	WIN_XP  = 2600
	WIN_2K3 = 3790
	WIN_VISTA = 6000
	WIN_7 = 7600
	WIN_8 = 9200
	WIN_BLUE = 9600
	WIN_10_1507 = 10240
	WIN_10_1511 = 10586
	WIN_10_1607 = 14393
	WIN_10_1707 = 15063
	
class WindowsMinBuild(enum.Enum):
	WIN_XP = 2500
	WIN_2K3 = 3000
	WIN_VISTA = 5000
	WIN_7 = 7000
	WIN_8 = 8000
	WIN_BLUE = 9400
	WIN_10 = 9800
	
#utter microsoft bullshit commencing..
def getWindowsBuild():   
    class OSVersionInfo(ctypes.Structure):
        _fields_ = [
            ("dwOSVersionInfoSize" , ctypes.c_int),
            ("dwMajorVersion"      , ctypes.c_int),
            ("dwMinorVersion"      , ctypes.c_int),
            ("dwBuildNumber"       , ctypes.c_int),
            ("dwPlatformId"        , ctypes.c_int),
            ("szCSDVersion"        , ctypes.c_char*128)];
    GetVersionEx = getattr( ctypes.windll.kernel32 , "GetVersionExA")
    version  = OSVersionInfo()
    version.dwOSVersionInfoSize = ctypes.sizeof(OSVersionInfo)
    GetVersionEx( ctypes.byref(version) )    
    return version.dwBuildNumber
	
DELETE = 0x00010000
READ_CONTROL = 0x00020000
WRITE_DAC = 0x00040000
WRITE_OWNER = 0x00080000

SYNCHRONIZE = 0x00100000

STANDARD_RIGHTS_REQUIRED = DELETE | READ_CONTROL | WRITE_DAC | WRITE_OWNER
STANDARD_RIGHTS_ALL = STANDARD_RIGHTS_REQUIRED | SYNCHRONIZE

if getWindowsBuild() >= WindowsMinBuild.WIN_VISTA.value:
	PROCESS_ALL_ACCESS = STANDARD_RIGHTS_REQUIRED | SYNCHRONIZE | 0xFFFF
else:
	PROCESS_ALL_ACCESS = STANDARD_RIGHTS_REQUIRED | SYNCHRONIZE | 0xFFF
	
FILE_SHARE_READ = 1
FILE_SHARE_WRITE = 2
FILE_SHARE_DELETE = 4
FILE_FLAG_OPEN_REPARSE_POINT = 0x00200000
FILE_FLAG_BACKUP_SEMANTICS = 0x2000000

FILE_CREATE_NEW = 1
FILE_CREATE_ALWAYS = 2
FILE_OPEN_EXISTING = 3
FILE_OPEN_ALWAYS = 4
FILE_TRUNCATE_EXISTING = 5

FILE_GENERIC_READ = 0x80000000
FILE_GENERIC_WRITE = 0x40000000
FILE_GENERIC_EXECUTE = 0x20000000
FILE_GENERIC_ALL = 0x10000000


FILE_ATTRIBUTE_READONLY = 0x1
FILE_ATTRIBUTE_HIDDEN = 0x2
FILE_ATTRIBUTE_DIRECTORY = 0x10
FILE_ATTRIBUTE_NORMAL = 0x80
FILE_ATTRIBUTE_REPARSE_POINT = 0x400
GENERIC_READ = 0x80000000
FILE_READ_ATTRIBUTES = 0x80

"""
class SECURITY_ATTRIBUTES(ctypes.Structure):
    _fields_ = (
        ('length', ctypes.wintypes.DWORD),
        ('p_security_descriptor', ctypes.wintypes.LPVOID),
        ('inherit_handle', ctypes.wintypes.BOOLEAN),
        )
LPSECURITY_ATTRIBUTES = ctypes.POINTER(SECURITY_ATTRIBUTES)	
"""
LPSECURITY_ATTRIBUTES = LPVOID #we dont pass this for now
# https://msdn.microsoft.com/en-us/library/windows/desktop/aa363858(v=vs.85).aspx
CreateFile = ctypes.windll.kernel32.CreateFileW
CreateFile.argtypes = (
	LPWSTR,
	DWORD,
	DWORD,
    LPSECURITY_ATTRIBUTES,
	DWORD,
	DWORD,
	HANDLE,
    )
CreateFile.restype = ctypes.wintypes.HANDLE

PHANDLE = ctypes.POINTER(HANDLE)
PDWORD = ctypes.POINTER(DWORD)

GetCurrentProcess = ctypes.windll.kernel32.GetCurrentProcess
GetCurrentProcess.argtypes = ()
GetCurrentProcess.restype = HANDLE

# https://msdn.microsoft.com/en-us/library/ms684139.aspx
IsWow64Process  = ctypes.windll.kernel32.IsWow64Process 
IsWow64Process.argtypes = (HANDLE, PBOOL)
IsWow64Process.restype = BOOL

CloseHandle = ctypes.windll.kernel32.CloseHandle
CloseHandle.argtypes = (HANDLE, )
CloseHandle.restype = BOOL

# https://msdn.microsoft.com/en-us/library/windows/desktop/ms684320(v=vs.85).aspx
OpenProcess = ctypes.windll.kernel32.OpenProcess
OpenProcess.argtypes = (DWORD, BOOL, DWORD )
OpenProcess.restype = HANDLE

# https://msdn.microsoft.com/en-us/library/windows/desktop/ms680360(v=vs.85).aspx
MiniDumpWriteDump = ctypes.windll.DbgHelp.MiniDumpWriteDump
MiniDumpWriteDump.argtypes = (HANDLE , DWORD , HANDLE, DWORD, DWORD, DWORD, DWORD)
MiniDumpWriteDump.restype = BOOL

def is64bitProc(process_handle):
	is64 = BOOL()
	res = IsWow64Process(process_handle, ctypes.byref(is64))
	if res == 0:
		logging.warning('Failed to get process version info!')
		WinError(get_last_error())
	return not bool(is64.value)

def create_dump(pid, output_filename, mindumptype, with_debug = False):
	if with_debug:
		logging.debug('Enabling SeDebugPrivilege')
		assigned = enable_debug_privilege()
		msg = ['failure', 'success'][assigned]
		logging.debug('SeDebugPrivilege assignment %s' % msg)
	
	logging.debug('Opening process PID: %d' % pid)
	process_handle = OpenProcess(PROCESS_ALL_ACCESS, False, pid)
	if process_handle is None:
		logging.warning('Failed to open process PID: %d' % pid)
		logging.error(WinError(get_last_error()))
		return
	logging.debug('Process handle: 0x%04x' % process_handle)
	is64 = is64bitProc(process_handle)
	if is64 != IS_PYTHON_64:
		logging.warning('process architecture mismatch! This could case error! Python arch: %s Target process arch: %s' % ('x86' if not IS_PYTHON_64 else 'x64', 'x86' if not is64 else 'x64'))
	
	logging.debug('Creating file handle for output file')
	file_handle = CreateFile(output_filename, FILE_GENERIC_READ | FILE_GENERIC_WRITE, 0, None,  FILE_CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, None)
	if file_handle == -1:
		logging.warning('Failed to create file')
		logging.error(WinError(get_last_error()))
		return
	logging.debug('Dumping process to file')
	res = MiniDumpWriteDump(process_handle, pid, file_handle, mindumptype, 0,0,0)
	if not bool(res):
		logging.warning('Failed to dump process to file')
		logging.error(WinError(get_last_error()))
	logging.info('Dump file created succsessfully')
	CloseHandle(file_handle)
	CloseHandle(process_handle)
	
	
if __name__=='__main__':
	import argparse

	parser = argparse.ArgumentParser(description='Tool to create process dumps using windows API')
	parser.add_argument('pid', type=int, help='PID of the process')
	parser.add_argument('outputfile', help='file to write the dumps to')
	parser.add_argument('-d', '--with-debug', action='store_true', help='enable SeDebugPrivilege, use this if target process is not in the same user context as your script')
	parser.add_argument('-v', '--verbose', action='count', default=0)
	
	args = parser.parse_args()
	if args.verbose == 0:
		logging.basicConfig(level=logging.INFO)
	elif args.verbose == 1:
		logging.basicConfig(level=logging.DEBUG)
	else:
		logging.basicConfig(level=1)

	mindumptype = MINIDUMP_TYPE.MiniDumpNormal | MINIDUMP_TYPE.MiniDumpWithFullMemory
	create_dump(args.pid, args.outputfile, mindumptype, with_debug = args.with_debug)

	