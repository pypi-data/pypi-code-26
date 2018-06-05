class GDBClient:
    @staticmethod
    def start():
        print('GNU gdb (GDB) 7.6.2')
        print('Copyright (C) 2013 Free Software Foundation, Inc.')
        print('License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>')
        print('This is free software: you are free to change and redistribute it.')
        print('There is NO WARRANTY, to the extent permitted by law.  Type "show copying"')
        print('and "show warranty" for details.')
        print('This GDB was configured as "--host=armv6l-unknown-linux-gnueabihf --target=arm-none-eabi".')
        print('For bug reporting instructions, please see:')
        print('<http://www.gnu.org/software/gdb/bugs/>.')
        print('(gdb)')

if __name__ == '__main__':
        gdb = GDBClient()
        gdb.start()
