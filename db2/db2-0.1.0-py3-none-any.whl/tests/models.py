#! usr/bin/python3.6

import sys
sys.path.append("../")
from  db2 import Base


class Patient(Base):
    id = PositiveInteger(primary_key=True, auto_increment=True)
    name = SizedString(maxlen=15) 
    age = Integer()
    sex = SizedString(maxlen=6)
    address = SizedString(maxlen=25)
    mobile = PhoneNumber(maxlen=10)
    next_of_kin = SizedString(maxlen=25)
    religion = SizedString(maxlen=15)
    marital_status = SizedString(maxlen=15)
    date = DateTimeField()
