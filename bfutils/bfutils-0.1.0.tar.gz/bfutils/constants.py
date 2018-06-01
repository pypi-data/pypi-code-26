import os

__author__ = 'Landon T. Clipp'
__email__ = 'clipp2@illinois.edu'

ROOT_DIR = os.path.dirname( os.path.abspath( __file__ ) )
DATA_DIR = os.path.join( ROOT_DIR, 'data' )

ORBIT_INFO_TXT = os.path.join( DATA_DIR, 'Orbit_Path_Time.txt' )
ORBIT_INFO_JSON = os.path.join( DATA_DIR, 'Orbit_Path_Time.json' )
CONFIG_YAML = os.path.join( DATA_DIR, 'config.yml' )

# CONFIG will be initialized with the values in config.yml
CONFIG = None

MOP_re='^MOP01-[0-9]+-L[0-9]+V[0-9]+.[0-9]+.[0-9]+.he5$'
CER_re='^CER_SSF_Terra-FM[0-9]-MODIS_Edition[0-9]+A_[0-9]+.[0-9]+$'
MOD_re='^MOD0((21KM)|(2HKM)|(2QKM)|(3)).A[0-9]+.[0-9]+.[0-9]+.[0-9]+.hdf$'
AST_re='^AST_L1T_[0-9]+_[0-9]+_[0-9]+.hdf$'
MIS_re_GRP='^MISR_AM1_GRP_ELLIPSOID_GM_P[0-9]{3}_O[0-9]+_(AA|AF|AN|BA|BF|CA|CF|DA|DF)_F[0-9]+_[0-9]+.hdf$' 
MIS_re_AGP='^MISR_AM1_AGP_P[0-9]{3}_F[0-9]+_[0-9]+.hdf$'
MIS_re_GP='^MISR_AM1_GP_GMP_P[0-9]{3}_O[0-9]+_F[0-9]+_[0-9]+.hdf$'
MIS_re_HRLL='^MISR_HRLL_P[0-9]{3}\.hdf$'

BF_template = 'TERRA_BF_L1B_O{}_{}_F{}_V{}.h5'
BF_re = '^TERRA_BF_L1B_O[0-9]+_[0-9]+_F[0-9]+_V[0-9]+\.h5$'


