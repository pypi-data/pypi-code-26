class hp3458(object):
        
    def read_DCV(instr):
        instr.write('RESET;END ALWAYS;DCV;TARM HOLD;TARM SGL')
        data=instr.read()
        return data
    def read_ACV(addr):
        instr.write('RESET;END ALWAYS;ACV;TARM HOLD;TARM SGL')
        data=instr.read()
        return data
    def read_DCI(addr):
        instr.write('RESET;END ALWAYS;DCI;TARM HOLD;TARM SGL')
        data=instr.read()
        return data
    def read_ACI(addr):
        instr.write('RESET;END ALWAYS;ACI;TARM HOLD;TARM SGL')
        data=instr.read()
        return data

