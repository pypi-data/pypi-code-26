import numpy as np
import os
import struct

class _TDT(object):
    '''
    Internal class for processing TDT files
    '''
    def __init__(self, block, stores):
        self.set_globals() #Set global variables

        self.block = block
        self.stores = stores
        
        #Define dictionaries
        self.headerStruct = {
            'startTime' : None,
            'stopTime' : None,
            'stores' : {},
        }
        
        self.data = {}

        self.epocs = {
            'name'       : [],
            'buddies'    : [],
            'timestamps' : [],
            'code'       : [],
            'type'       : [],
            'typeStr'    : [],
            'data'       : [],
            'dtype'      : [],
        }
        
        #get file objects
        fnames = os.listdir(self.block)
        basePath = os.path.join(self.block, [fname for fname in fnames if '.tsq' in fname][0][:-4])
        
        self.tsq = open(basePath+'.tsq','rb')
        self.tev = open(basePath+'.tev','rb')
        self.tnt = open(basePath+'.tnt','rt') #read text

        self.Tbk = open(basePath+'.Tbk','rb')
        self.Tdx = open(basePath+'.Tdx','rb')
        self.tin = open(basePath+'.tin','rb')
        
    def extract(self):
        #Read notes
        self.read_tnt()

        #Look for sort IDs
        self.get_sortIDs()

        #Read block notes
        self.read_blockNotes()
        
        #Read headers
        self.read_headers()

        #Extract data from .TEV file
        self.read_TEV()

        return self.data
        
    def read_tnt(self):
        '''
        The tnt file appears to be a note file. Skipping for now
        '''
        pass

    def get_sortIDs(self):
        '''
        Looks like it loads sort IDs from a sort/ directory. Skipping for now
        '''
        pass

    def read_blockNotes(self):
        '''
        Reads blocknotes from .Tbk file into a list of dictionaries
        '''
        self.blockNotes = []

        strbits = np.fromfile(self.Tbk, dtype='uint8')
        string = ''.join([chr(item) for item in strbits])
        string = string.split('[USERNOTEDELIMITER]')[2]
        lines = string.split()

        storenum = -1
        for line in lines:
            #check if new store
            if 'StoreName' in line:
                storenum += 1
                self.blockNotes.append({})

            if ';' in line:
                items = line.split(';')
                fieldstr = items[0].split('=')[1]
                value = items[2].split('=')[1]

            self.blockNotes[storenum][fieldstr] = value
            
    def read_headers(self):
        header_dtype = np.dtype([
            ('size',         np.int32),
            ('type',         np.int32),
            ('code',         'S4'),
            ('channel',      np.uint16),
            ('sort code',    np.uint16),
            ('timestamp',    np.float64),
            ('event offset', np.uint64), #also Strobe, need to be able to convert to float64
            ('dtype',        np.int32),
            ('fs',           np.float32),
        ])

        # **NOTE**
        # All header codes get read in as byte strings (b'abcd') instead of regular strings ('abcd')
        # this may cause issues later, but i keep getting errors if I try to read the data as regular strings
        
        #Read all headers
        self.tsq.seek(0,0)
        headers = np.fromfile(self.tsq, dtype=header_dtype)
        
        #Process start/stop time
        if headers[1]['code'] != self.event_marks['STARTBLOCK']:
            print('Block start marker not found')
        if headers[-1]['code'] != self.event_marks['STOPBLOCK']:
            print('Block end marker not found')
        self.headerStruct['startTime'] = headers[1]['timestamp']
        self.headerStruct['stopTime'] = headers[1]['timestamp']

        #Process remaining headers
        headers = headers[2:-1] #remove first 2, last 1

        #Get unique codes, and determine their store types
        unique_codes = np.unique(headers['code'])
        unique_code_indxs = [np.where(headers['code'] == code)[0][0] for code in unique_codes]
        store_types = [self.code2type(headers[indx]['type']) for indx in unique_code_indxs] 

        #Add store information to store map
        for i in range(len(unique_codes)):
            header = headers[unique_code_indxs[i]]
            code = unique_codes[i].decode('utf-8') #DECODE BYTESTRING
            sType = store_types[i]
            
            #indx = unique_code_indxs[i]
            #code = unique_codes[i]

            if sType == 'epocs':
                #Need to read channel and sort code as a single string
                #There's a good chance I did this in the wrong order, but I have no way of testing it for now
                byte_str    = header['channel'].tobytes() + header['sort code'].tobytes()
                uint8_array = np.frombuffer(byte_str,dtype = 'uint8')
                buddies     = ''.join([chr(c) for c in uint8_array])
                #This is for maching epoc channels to eachother later
                
                self.epocs['name'].append(code)
                self.epocs['buddies'].append(buddies)
                #self.epocs['code'].append() Dont need because we are reading names directly
                self.epocs['timestamps'].append([])
                self.epocs['type'].append(self.epoc2type(header['type']))
                self.epocs['typeStr'].append(sType)
                #self.epocs['typeNum'].append() Also dont care about this
                self.epocs['data'].append([])
                self.epocs['dtype'].append(header['dtype'])
            else:
                self.headerStruct['stores'][code] = {
                    'name'    : code,
                    'size'    : header['size'],
                    'type'    : header['type'],
                    'typeStr' : sType,
                    'dtype'   : header['dtype']
                    }

                if store_types[i] != 'scalars':
                    self.headerStruct['stores'][code]['fs'] = header['fs']

            #Get indexes of all headers associated with this store
            store_indxs = np.where(headers['code'].astype(str) == code)
    
            #=============================================
            # COMPILE NOTES HERE. SKIPPING FOR NOW     
            #=============================================
                    
            if sType == 'epocs':
                indx = self.epocs['name'].index(code)
                self.epocs['timestamps'][indx] = headers[store_indxs]['timestamp'] - self.headerStruct['startTime']
                #Need to convert offset to double
                self.epocs['data'][indx] = np.frombuffer(headers[store_indxs]['event offset'].tobytes(),dtype='float64')
                
            else:
                self.headerStruct['stores'][code]['timestamps'] = headers[store_indxs]['timestamp']
                self.headerStruct['stores'][code]['offsets']    = headers[store_indxs]['event offset']
                self.headerStruct['stores'][code]['channel']    = headers[store_indxs]['channel']

                if self.headerStruct['stores'][code]['typeStr'] == 'snips':
                    #NOT ALLOWING FOR CUSTOM SORT, SOMEONE ELSE CAN ADD SUPPORT FOR THIS
                    self.headerStruct['stores'][code]['sortcode'] = headers[store_indxs]['channel']
                    self.headerStruct['stores'][code]['sortname'] = 'TankSort'

            
        #Put epocs into headerStruct
        for i in range(len(self.epocs['name'])): #do non-buddies first
            if self.epocs['type'][i] == 'onset':
                name = self.epocs['name'][i]
                self.headerStruct['stores'][name] = {
                    'name'    : name,
                    'onset'   : self.epocs['timestamps'][i][:-1],
                    'offset'  : self.epocs['timestamps'][i][1:],
                    'type'    : self.epocs['type'][i],
                    'typeStr' : self.epocs['typeStr'][i],
                    #'typeNum' : 2
                    'data'    : self.epocs['data'][i],
                    'dtype'   : self.epocs['dtype'][i],
                    'size'    : 10
                }

        for i in range(len(self.epocs['name'])): #buddies second
            if self.epocs['type'][i] == 'offset':
                name = self.epocs['buddies'][i]
                self.headerStruct['stores'][name]['offset'] = self.epocs['timestamps'][i]

                #Fix time ranges
                if self.headerStruct['stores'][name]['offset'][0] < self.headerStruct['stores'][name]['onset'][0]:
                    self.headerStruct['stores'][name]['onset'] = np.hstack((0,self.headerStruct['stores'][name]['onset']))
                if self.headerStruct['stores'][name]['offset'][-1] < self.headerStruct['stores'][name]['onset'][-1]:
                    self.headerStruct['stores'][name]['offset'] = np.hstack((self.headerStruct['stores'][name]['offset'],np.inf))

    def read_TEV(self):
        self.data = {
            'epocs'   : {},
            'snips'   : {},
            'streams' : {},
            'scalars' : {},
        }

        for storeName, store in self.headerStruct['stores'].items():
            if self.stores is None or storeName in self.stores:
                size = store['size']
                storeType = store['typeStr']
                dtype = self.dtypes[store['dtype']]
                #fs = store['fs']

                if store['typeStr'] == 'streams':
                    self.data['streams'][storeName] = {
                        'fs' : store['fs']
                    }

                    nChan = np.max(store['channel'])
                    chanOffsets = np.zeros(nChan,dtype=int)

                    nPts = int((size-10) * 4 / np.array(1,dtype=dtype).nbytes) #number of points per block
                    nStores = store['offsets'].size  
                    self.data['streams'][storeName]['data'] = np.zeros((nChan, int(nPts*nStores/nChan)),dtype=dtype)

                    for i in range(len(store['offsets'])):
                        self.tev.seek(store['offsets'][i],0)
                        chan = store['channel'][i] - 1
                        x = np.fromfile(self.tev, dtype=dtype, count=nPts)

                        self.data['streams'][storeName]['data'][chan, chanOffsets[chan]:chanOffsets[chan]+nPts] = x
                        chanOffsets[chan] += nPts

                elif store['typeStr'] == 'epocs':
                    pass

                elif store['typeStr'] == 'scalars':
                    pass

                elif store['typeStr'] == 'snpis':
                    pass

                else:
                    pass
            
    def get_data_info(self):
        self.data['info'] = {
            'blockpath'     : None,
            'blockname'     : None,
            'date'          : None,
            'utcStartTime'  : None,
            'utcStopTime'   : None,
            'duration'      : None,
            'streamChannel' : None,
            'snipChannel'   : None,
        }

    def code2type(self,code):
        '''
        Given a code, returns string
        '''
        if code == self.event_types['STREAM']:
            code_str = 'streams'
        elif code == self.event_types['SNIP']:
            code_str = 'snips'
        elif code == self.event_types['SCALAR']:
            code_str = 'scalars'
        elif code in [self.event_types['STRON'], self.event_types['STROFF'], self.event_types['MARK']]:
            code_str = 'epocs'
        else:
            code_str = 'unknown'
        
        return code_str

    def epoc2type(self,code):
        if code in [self.event_types['STRON'], self.event_types['MARK']]:
            code_str = 'onset'
        elif code == self.event_types['STROFF']:
            code_str = 'offset'
        else:
            code_str = 'unknown'

        return code_str
        
    def set_globals(self):
        self.event_types = {
            'UNKNOWN'      : int('0x00000000',16),
            'STRON'        : int('0x00000101',16),
            'STROFF'       : int('0x00000102',16),
            'SCALAR'       : int('0x00000201',16),
            'STREAM'       : int('0x00008101',16),
            'SNIP'         : int('0x00008201',16),
            'MARK'         : int('0x00008801',16),
            'HASDATA'      : int('0x00008000',16),
            'UCF'          : int('0x00000010',16),
            'PHANTOM'      : int('0x00000020',16),
            'MASK'         : int('0x0000FF0F',16),
            'INVALID_MASK' : int('0xFFFF0000',16),
        }
        self.event_marks = {
            'STARTBLOCK' : b'\x01', #int('0x0001',16),
            'STOPBLOCK'  : b'\x02', #int('0x0002',16),
        }
        self.data_formats = {
            'FLOAT'      : 0,
            'LONG'       : 1,
            'SHORT'      : 2,
            'BYTE'       : 3,
            'DOUBLE'     : 4,
            'QWORD'      : 5,
            'TYPE_COUNT' : 6
        }

        self.dtypes = ['float32','int32','int16','int8','float64','']
        
    def __del__(self):
        pass


def loadTDT(block, stores=None):
    '''
    Load TDT block.

    Parameters
    ----------
    Required
        block : str
            Path to TDT block
    Optional
        stores : str or list, defaults to None
            String or list of strings specifing which store(s) to extract

    Returns
    -------
    data : dict
        Dictionary with different types of data as keys ('epocs', 'scalars',
        'streams', 'snips'), each of which contains keys for specific data
        stores.
    '''
    obj = _TDT(block, stores)
    data = obj.extract()
    return data
