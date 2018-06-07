"""
C-SALT
"""

__title__ = 'c_salt'
__author__ = 'Lev Golod'
__version__ = '1.0.0'
__copyright__ = 'Copyright 2018, TrueCar, Inc.'
__description__ = (
    'C-SALT (Capsela Sales And Leads Tree)'
    'Project to predict sales and leads for prospective Franchise dealers.'
    )
    
from .conv_rate import get_dlr_info
from .conv_rate import get_active_dlrs
from .conv_rate import get_dlr_size_cat
from .conv_rate import get_dealer_density
from .conv_rate import get_cz_limited_by_radius
from .conv_rate import get_sales_leads_sp
from .conv_rate import add_sales_leads
# from .conv_rate import fix_bad_zips
from .conv_rate import get_uvs_sp
from .conv_rate import add_uvs
from .conv_rate import add_density
from .conv_rate import add_size_cat
from .conv_rate import get_lead_conv_rate_table
from .conv_rate import conv_rate_table_master

from .close_rate import get_sales_leads_pag_sp
from .close_rate import add_sales_leads_pag
from .close_rate import ludovica_smoothing
from .close_rate import right_predict_function
from .close_rate import get_pred_close_rate_by_make_pag
from .close_rate import close_rate_table_master

from .simple_prediction import add_leads_prediction
from .simple_prediction import get_uvs_pag_sp
from .simple_prediction import add_sales_prediction
from .simple_prediction import simple_pred_master