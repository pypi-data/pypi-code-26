from uuid import uuid4
import logging
import numpy as np

def excel_to_array(s_, header_rows=1):
    s_ = s_.rstrip().lstrip()
    tmpfile = "/tmp/{}".format(uuid4())
    with open(tmpfile, 'w') as F:
        F.write(s_)

    a = np.genfromtxt(tmpfile, delimiter="\t", dtype=np.float32)
    if not(np.all(np.isnan(a[0,:]))) and header_rows==1:
        logging.warning("Not all elements in the first line were interpreted as strings.  Are you sure the default header_rows=1 is what you want?")
    a = a[header_rows:,:]
    header = np.genfromtxt(tmpfile, delimiter="\t", skip_footer=len(a), dtype=np.str)

    return header, a

def spreadsheet_to_array(*args, **kwargs):
    return excel_to_array(*args, **kwargs)

