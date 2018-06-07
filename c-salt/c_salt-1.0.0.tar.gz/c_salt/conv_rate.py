import pandas
import psycopg2
import time
import re
import datetime as dt
from pyspark.sql import Row
from pyspark.sql.types import *
from pyspark.sql.window import Window
import pyspark.sql.functions as f
from pyspark.sql import SQLContext, Row, HiveContext
from pyspark import SparkContext, SparkConf


def get_dlr_info(df, info_fields = ['dealership_name','postal_code','state','radius']):
    """
    Gets specified fields from bi_dw.
    Merges them to "df" using dealership_id as merge key.

    :df: the origin data frame with dealers
    :info_fields: names of the fields you want to add (do not modify this argument)
    :return: df_, the original df + info_fields
    """
    
    df_ = df.copy()
    
    dlr_info = run_query_redshift("""
    SELECT DISTINCT
        d.dealership_id
        ,d.dealership_name
        ,p.postal_code
        ,s.state_abbreviation as state
        ,d.lead_distance_max as radius
        
    FROM bi_dw.d_dealership d
    
    LEFT OUTER JOIN bi_dw.d_postal_code p
        ON d.postal_code = p.postal_code

    LEFT OUTER JOIN bi_dw.d_state s
        ON p.state_id = s.state_id
        """)
    
    df_ = df_.merge(dlr_info[['dealership_id']+info_fields],
                    on='dealership_id',
                    how='left')
    
    df_['unique_id'] = df_['make'] + '-' + df_['postal_code']
    df_ = df_[['dealership_id','unique_id']+info_fields]
    
    return(df_)


def get_active_dlrs(start_dt,end_dt,active_thresh=0.97):
    """
    Identifies the FRANCHISE dealers that were fully active over the specified time period [start_dt,end_dt].
    A dealership is considered fully active if it was active for at least active_thresh % of the date range. 

	:start_dt: datetime
	:end_dt: datetime
	:active_thresh: float in (0, 1]. Dealers must be active for at least this % of date range.
    :return: _dlrs, a pandas df with the active dealers (dealership_id, make).
    """
    
    _dlrs = run_query_redshift("""
    SELECT DISTINCT
        D.dealership_id
        ,lower(M.make_name)                  AS make
        ,H.date_id                           AS dt_active

    FROM bi_dw.d_dealership d

    LEFT OUTER JOIN bi_dw.agg_dealership_make_history_daily h
        ON h.dealership_id = d.dealership_id

    LEFT OUTER JOIN bi_dw.d_make m
        ON m.make_id = h.make_id

    WHERE
        H.status_id = 6
        AND d.dealership_type = 'Franchise Dealer'
        AND H.date_id BETWEEN '{}' AND '{}'
    """.format(start_dt.strftime('%Y-%m-%d'),
               end_dt.strftime('%Y-%m-%d'))
                              )
    _dlrs = (_dlrs
             .groupby(['dealership_id','make'])
             .size()
             .reset_index()
             .rename(columns={0:'n_days_active'})
            )
    _dlrs['pct_days_active'] = _dlrs['n_days_active'] / float(len(pd.date_range(start_dt,end_dt)))
    
    _dlrs = _dlrs[_dlrs['pct_days_active'] >= active_thresh]
    return(_dlrs[['dealership_id','make']])
    
    
    
def get_dlr_size_cat(cz_table, filepath_save = None, verbose = True, save=True):
    """
    Creates a spark df with dealership size categories, based on quantiles of industry sales. 
   
    :cz_table: Competition Zones table (spark df) with a row for each dealer for each customer zip. 
    	Must have total monthly sales (based on Polk industry sales data) for each dealer.
    :save: should we save the result?
    :filepath_save: where to save the result
    :returns: dealer_size_pivot_, spark df with make, DCZ Zone, and quantiles (25,50,75) of total sales.

	:sample of output:
	 +----------+----------+-------------------+-------------------+------------------+
	 |      make|  DCZ_Zone|                 q1|                 q2|                q3|
	 +----------+----------+-------------------+-------------------+------------------+
	 |    subaru|      back| 25.916666666666668| 35.708333333333336| 51.47916666666667|
	 |    subaru|      comp|  6.083333333333333| 15.666666666666666|27.416666666666668|
	 |    subaru|conq_close| 2.9479166666666665|  7.333333333333334|12.947916666666666|
	 +----------+----------+-------------------+-------------------+------------------+
    """
  
    t0 = time.time()
    if filepath_save is None:
        filepath_save = 'get_dlr_size_cat-{}'.format(dt.datetime.now().strftime('%Y.%m.%d'))
    
    if verbose:
        print('\nSaving intermediate file here: {}'.format(filepath_save))
    
    agg1_ = (cz_table
            .where('active_dealer = 1')
            .groupby(['unique_id','make','DCZ_Zone'])
            .agg(f.sum('sales').alias('dealer_industry_sales'))
       )
    
    agg1_.write.parquet(filepath_save,'overwrite')
    agg1_ = sqlContext.read.parquet(filepath_save).toPandas()
    
    ##divide by 24 to get monthly polk
    agg1_['dealer_industry_sales'] = agg1_['dealer_industry_sales'] / 24.
    
    dealer_size_ = (agg1_
               .groupby(['make','DCZ_Zone'])
               .dealer_industry_sales
               .quantile([0.25,0.5,0.75])
               .reset_index()
               .rename(columns={'level_2':'q',0:'value'})
              )
    
    dealer_size_pivot_ = dealer_size_.set_index(['make','DCZ_Zone','q']).unstack('q').reset_index()
    dealer_size_pivot_.columns = ['make','DCZ_Zone']+['q'+str(x) for x in [1,2,3]]
    
    dealer_size_pivot_ = sqlContext.createDataFrame(dealer_size_pivot_)
    
    if save:
        if verbose:
            print('\nSaving result file here: {}'.format(filepath_save))
        dealer_size_pivot_.write.parquet(filepath_save,'overwrite')
        dealer_size_pivot_ = sqlContext.read.parquet(filepath_save)
        
    t1 = time.time()
    if verbose:
        print("Time to process: {0:.3g} minutes.".format((t1-t0)/60.))
    
    return dealer_size_pivot_
    
    
    
def get_dealer_density(cz_table, gcd_cutoff = 50, filepath_save = None, verbose = True, save=True):
    """
    Returns a spark DF that shows how many car dealerships there are near each customer zip code.
    Limits to dealers that are within `gcd_cutoff` miles of the customer zip (default is 50).
    
    :cz_table: Competition Zones table (spark df) with a row for each dealer for each customer zip. 
    	Must have total monthly sales (based on Polk industry sales data) for each dealer.
    :gcd_cutoff: max distance in miles from dealer to customer (real-valued scalar)
    :save: should we save the result?
    :filepath_save: where to save the result
    :return: density_sp, a table with dealer density counts for each zip + make
    
	:sample of output:
    +-----+----------+------------------+-------------------------+
    |  zip|      make|n_dealers_{}_miles|n_active_dealers_{}_miles|
    +-----+----------+------------------+-------------------------+
    |65806|     acura|                 1|                        0|
    |90084|     acura|                14|                        7|
    |91409|     acura|                13|                        7|
    +-----+----------+------------------+-------------------------+
    """

    t0 = time.time()
    if filepath_save is None:
        filepath_save = 'get_dealer_density-{}'.format(dt.datetime.now().strftime('%Y.%m.%d'))
    
    density_sp = (cz_table
                  .where('gcd <= {}'.format(gcd_cutoff))
                  .groupby('zip','make')
                  .agg(
                      f.count('unique_id').alias('n_dealers_{}_miles'.format(gcd_cutoff)),
                      f.sum('active_dealer').alias('n_active_dealers_{}_miles'.format(gcd_cutoff))
                  )
                 )
    
    if save:
        if verbose:
            print('\nSaving result file here: {}'.format(filepath_save))
        density_sp.write.parquet(filepath_save,'overwrite')
        density_sp = sqlContext.read.parquet(filepath_save)
        t1 = time.time()
        print("Time to process: {0:.3g} minutes.".format((t1-t0)/60.))
    
    return density_sp
    
    
def get_cz_limited_by_radius(cz_table, save = True, filepath_save = None, verbose = True, 
                             orderby_varlist=['distance','name'], dist_varname='gcd', radius_varname = 'radius'):
    """
    Returns a new version of the CZ table.
    1. Limits to active dealerships
    2. Limits to eligible dealerships (based on each dealer's radius)
    3. Adds a field `rank_dist_active`:  ranking the dealerships based on how close they are to the customer zip
    
    :cz_table: Competition Zones table (spark df) with a row for each dealer for each customer zip. 
    :orderby_varlist: how to order the rows (within zip+make) to create the field `rank_dist_active`
    :dist_varname: var to use for distance (to limit the table to eligible dealer-zip combos)
    :radius_varname: var to use for dealer radius (to limit the table to eligible dealer-zip combos)
    :save: should we save the result?
    :filepath_save: where to save the result
    :return: cz_, an updated version of the CZ table
    """
    
    t0 = time.time()
    
    if filepath_save is None:
        filepath_save = 'get_cz_limited_by_radius-{}'.format(dt.datetime.now().strftime('%Y.%m.%d'))
        
    cz_ = (cz_table
           .where("active_dealer = 1")
           .where("{} < {}".format(dist_varname, radius_varname))
          )
    
    
    ## add rank (by distance)
    # we are ranking the dealerships based on how close they are to the customer zip
    windowrankSpec = Window.partitionBy('zip','make').orderBy(orderby_varlist)
    rank_of_dist = f.rank().over(windowrankSpec)
    cz_ = cz_.withColumn("rank_dist_active", rank_of_dist)
    
    
    ##build rank dist active
    def dist_cat(x):
        if x is None:
            return -1
        else:
            if x <= 3:
                return x
            elif x <= 6:
                return 4
            else:
                return 5
    
    dist_cat_sp = f.udf(dist_cat,IntegerType())
    cz_ = cz_.withColumn('rank_dist_active_cat',dist_cat_sp(cz_['rank_dist_active'])) 
    
    if save:
        if verbose:
            print('\nSaving result file here: {}'.format(filepath_save))
        cz_.write.parquet(filepath_save,'overwrite')
        cz_ = sqlContext.read.parquet(filepath_save)
        t1 = time.time()
        print("Time to process: {0:.3g} minutes.".format((t1-t0)/60.))
    
    return cz_
        
    
def get_sales_leads_sp(start_dt, end_dt, save = True, filepath_save = None, verbose = True):
    """
    Queries redshift bi_dw and returns a spark df:
    ['tc_sales','leads','prospects'], aggregated by ['dealership_id','search_zip','make']
                 
	:start_dt: datetime
	:end_dt: datetime
	:return: SL_sp, spark df with sales, leads, and prospects for each dealer, make, & search zip
                 
    :sample output:
    +-------------+----------+----------+--------+-----+---------+
    |dealership_id|search_zip|      make|tc_sales|leads|prospects|
    +-------------+----------+----------+--------+-----+---------+
    |        10554|     60564|volkswagen|       0|    1|        1|
    |        10554|     60638|volkswagen|       0|    1|        1|
    |        10554|     60655|volkswagen|       1|    1|        1|
    +-------------+----------+----------+--------+-----+---------+
    """

    t0 = time.time()
    if filepath_save is None:
        filepath_save = 'get_sales_leads_sp-{}'.format(dt.datetime.now().strftime('%Y.%m.%d'))

    ## define query I will use to get sales and leads
    qry_sales_leads = """
    SELECT 
        A.dealership_id
        ,lower(M.make_name)                  AS make
        ,A.postal_code                       as search_zip
        
        ,COUNT(DISTINCT A.email_hash)        AS prospects
        ,COUNT(DISTINCT A.leadgen_lead_id)   AS leads
        ,COUNT(DISTINCT CASE WHEN R.approved_date IS NOT NULL THEN A.email_hash END) as tc_sales

    FROM bi_dw.f_reported_lead A

    LEFT OUTER JOIN bi_dw.f_result R
        on R.reported_lead_id = A.reported_lead_id

    LEFT OUTER JOIN bi_dw.d_dealership D
        on A.dealership_id = D.dealership_id

    LEFT OUTER JOIN bi_dw.d_make M
        on A.make_id = M.make_id

    WHERE
        A.program_id = 1
        AND A.processing_status_id = 2
        AND A.is_reported = 1
        AND A.dealership_id > -1
        AND A.new_used = 'n'
        {where}

    GROUP BY
        A.dealership_id    
        ,lower(M.make_name) 
        ,A.postal_code                      

    ORDER BY
        A.dealership_id
        ,lower(M.make_name) 
        ,A.postal_code   
    """

    date_cond = "AND a.date_id BETWEEN '{}' AND '{}'".format(start_dt.strftime('%Y-%m-%d'),
                                                             end_dt.strftime('%Y-%m-%d'))
    my_qry_SL = qry_sales_leads.format(where=date_cond)
    if verbose:
        print(my_qry_SL)
    
    
    SL = run_query_redshift(my_qry_SL, verbose = verbose)

    ## aggregate TC sales, leads, and prospects 
    # by dealer, search zip, month
    
    SL_sp = (SL
                 .groupby(['dealership_id','search_zip','make'])
                 ['tc_sales','leads','prospects']
                 .agg(np.sum)
                 .reset_index()
                )
    SL_sp = sqlContext.createDataFrame(SL_sp)
    SL_sp = SL_sp.withColumn('make', f.lower(f.col('make')))
    
    if save:
        if verbose:
            print('\nSaving result file here: {}'.format(filepath_save))
        SL_sp.write.parquet(filepath_save,'overwrite')
        SL_sp = sqlContext.read.parquet(filepath_save)
        t1 = time.time()
        print("Time to process: {0:.3g} minutes.".format((t1-t0)/60.))
    
    return SL_sp
    
    
def add_sales_leads(cz_table, SL_table, save = True, filepath_save = None, verbose = True):
    
    """
    Takes the CZ table and adds sales, leads, and prospects information to it.
	:cz_table: Competition Zones table (spark df) with a row for each dealer for each customer zip. 
	:SL_table: spark df with sales, leads, & prospects for each dealer, make, & search zip
	:returns: cz_, CZ table with sales, leads, & prospects 
    """
    
    t0 = time.time()
    if filepath_save is None:
        filepath_save = 'add_sales_leads-{}'.format(dt.datetime.now().strftime('%Y.%m.%d'))
    
    cond  = [
        cz_table.make == SL_table.make
        ,cz_table.zip == SL_table.search_zip
        ,cz_table.dealership_id == SL_table.dealership_id
    ]

    cz_ = (cz_table
           .join(other = SL_table, on = cond, how = 'left_outer')
           .select([cz_table[col] for col in cz_table.columns]+['prospects','leads','tc_sales',])
           ).na.fill({'prospects':0,'leads':0,'sales':0,'tc_sales':0})
    
    if save:
        if verbose:
            print('\nSaving result file here: {}'.format(filepath_save))
        cz_.write.parquet(filepath_save,'overwrite')
        cz_ = sqlContext.read.parquet(filepath_save)
        t1 = time.time()
        print("Time to process: {0:.3g} minutes.".format((t1-t0)/60.))
    
    return cz_
    
	
def get_uvs_sp(start_dt, end_dt, save = True, filepath_save = None, verbose = True):
    """
    Queries redshift and returns a spark df with UV data (unique visitors).

	:start_dt: datetime
	:end_dt: datetime
	:return: uvs, spark df with uv count for each make + search zip.
                 
    :sample output:
    +----------+-------+---+
    |search_zip|   make| uv|
    +----------+-------+---+
    |     15120|bmw    |  5|
    |     92240|bmw    |  7|
    |     21237|bmw    |  6|
    +----------+-------+---+
    """

    t0 = time.time()
    if filepath_save is None:
        filepath_save = 'get_uvs_sp-{}'.format(dt.datetime.now().strftime('%Y.%m.%d'))


    ## define query I will use to get UVs
    uv_qry = """
    SELECT
        a.postal_code                                                       as search_zip
        ,lower(M.make_name)                                                 as make
        ,COUNT(DISTINCT CONCAT(a.fullvisitorid, a.date_id) )                as uv

    from bi_dw.agg_daily_ga_visitors a

    LEFT OUTER JOIN bi_dw.d_make M
        on A.make_id = M.make_id

    WHERE
        A.new_used = 'n'
        AND A.pagename LIKE 'New Car Price Report%'
        {where}

    GROUP BY
        a.postal_code
        ,lower(M.make_name)  
    """

    date_cond = "AND a.date_id BETWEEN '{}' AND '{}'".format(start_dt.strftime('%Y-%m-%d'),
                                                             end_dt.strftime('%Y-%m-%d'))
    my_qry_uv = uv_qry.format(where=date_cond)
    if verbose:
        print(my_qry_uv)
    
    
    uvs = run_query_redshift(my_qry_uv, verbose = verbose)
    uvs = uvs[uvs['search_zip'].notnull()]
    uvs['search_zip'] = uvs['search_zip'].str.zfill(5)
    assert uvs.notnull().all().all()

    uvs = sqlContext.createDataFrame(uvs)
        
    if save:
        if verbose:
            print('\nSaving result file here: {}'.format(filepath_save))
        uvs.write.parquet(filepath_save,'overwrite')
        uvs = sqlContext.read.parquet(filepath_save)
        t1 = time.time()
        print("Time to process: {0:.3g} minutes.".format((t1-t0)/60.))
    
    return uvs
    
    
def add_uvs(cz_table, uv_table, uv_col_list = ['uv'],
    save = True, filepath_save = None, verbose = True):
    """
    Joins UV information to CZ table.
    Limits to customer zips that have at least one UV.
    
    :uv_col_list: the fields from `uv_table` to add to `cz_table`
    	NOTE: if any of these fields already exist in `cz_table` they will be OVERWRITTEN
    :cz_table: Competition Zones table (spark df) with a row for each dealer for each customer zip. 
    :uv_table: spark df with uvs
	:returns: cz_, CZ table with UVs (limited to zips with at least 1 uv)
    """
    
    
    t0 = time.time()
    if filepath_save is None:
        filepath_save = 'add_uvs-{}'.format(dt.datetime.now().strftime('%Y.%m.%d'))
    
    cond = [
        cz_table.zip == uv_table.search_zip
        ,cz_table.make == uv_table.make
    ]
    
    cz_ = cz_table
    for x in uv_col_list:
    	if x in cz_.columns:
    		cz_ = cz_.drop(x)
 
    cz_2 = (cz_
           .join(other = uv_table, on = cond, how = 'inner')
           .select([cz_table[col] for col in cz_.columns]+uv_col_list)
           )
    
    for x in uv_col_list:
    	cz_2 = cz_2.na.fill({x:0})
    
    if save:
        if verbose:
            print('\nSaving result file here: {}'.format(filepath_save))
        cz_2.write.parquet(filepath_save,'overwrite')
        cz_2 = sqlContext.read.parquet(filepath_save)
        t1 = time.time()
        print("Time to process: {0:.3g} minutes.".format((t1-t0)/60.))
    
    return cz_2
    
    
def add_density(cz_table, density_table, save = True, filepath_save = None, verbose = True):
    """
    Joins desnity information to CZ table.
    
    :cz_table: Competition Zones table (spark df) with a row for each dealer for each customer zip. 
    :density_table: spark df with dealer density
    :returns: cz_, CZ table with density information
    """
    
    t0 = time.time()
    if filepath_save is None:
        filepath_save = 'add_dens-{}'.format(dt.datetime.now().strftime('%Y.%m.%d'))
    
    ## get dealer density
    cond = [
        cz_table.zip == density_table.zip
        ,cz_table.make == density_table.make
    ]
 
    dens_cols = [x for x in density_table.columns if bool(re.search(r'n_.*dealers.*miles', x))]
    active_var = [x for x in dens_cols if 'active' in x][0]
    
    cz_ = (cz_table
           .join(other = density_table, on = cond, how = 'left_outer')
           .select([cz_table[col] for col in cz_table.columns]+dens_cols)
           )
    
    for x in dens_cols:
        cz_ = cz_.na.fill({x:0})
    
    ## apply categories
    def cat(x):
        if x <= 3:
            return 0
        elif x < 8:
            return 1
        else:
            return 2
    cat_sp = f.udf(cat, IntegerType())  
    cz_ = cz_.withColumn('active_cat', cat_sp(cz_[active_var]))
    
    if save:
        if verbose:
            print('\nSaving result file here: {}'.format(filepath_save))
        cz_.write.parquet(filepath_save,'overwrite')
        cz_ = sqlContext.read.parquet(filepath_save)
        t1 = time.time()
        print("Time to process: {0:.3g} minutes.".format((t1-t0)/60.))
    
    return cz_
    
    
def add_size_cat(cz_table, size_cat_table, save = True, filepath_save = None, verbose = True):
    """
    Joins size cat information to CZ table.
    
    :cz_table: Competition Zones table (spark df) with a row for each dealer for each customer zip. 
        Must have industry sales info (from Polk) for each dealer.
    
    :size_cat_table: spark df with dealer size_cat
    :returns: cz_, CZ table with size_cat information
    """
    
    t0 = time.time()
    if filepath_save is None:
        filepath_save = 'add_size_cat-{}'.format(dt.datetime.now().strftime('%Y.%m.%d'))
    
    ## identify dealer size category based on zone 
    def assign_dealer_size_cat(x,x1,x2,x3):
        if (x == None) | (x <= x1):
            return 1
        elif x <= x2:
            return 2
        elif x <= x3:
            return 3
        else:
            return 4
    
    assign_dealer_size_cat_sp = f.udf(assign_dealer_size_cat,IntegerType())
    cz_  =  cz_table.withColumn('zone_dealer_industry_sales',
                            f.sum(cz_table['sales']/24.).over(Window.partitionBy('unique_id','DCZ_Zone')))
    
    ## merge info from size cat table
    cond = [cz_.make == size_cat_table.make,
            cz_.DCZ_Zone == size_cat_table.DCZ_Zone]
    
    cz_ = (cz_
            .join(other = size_cat_table, on = cond, how = 'left_outer')
            .select([cz_table[col] for col in cz_table.columns]+['zone_dealer_industry_sales', 'q1','q2','q3'])
          )
    
    cz_ = cz_.withColumn('dealer_size_cat',
                           assign_dealer_size_cat_sp(cz_['zone_dealer_industry_sales'],
                                                     cz_['q1'],cz_['q2'],cz_['q3'])
                          )
    
    if save:
        if verbose:
            print('\nSaving result file here: {}'.format(filepath_save))
        cz_.write.parquet(filepath_save,'overwrite')
        cz_ = sqlContext.read.parquet(filepath_save)
        t1 = time.time()
        print("Time to process: {0:.3g} minutes.".format((t1-t0)/60.))
    
    return cz_
    
    
def get_lead_conv_rate_table(cz_table,  zone_var = 'DCZ_Zone', filepath_save = None, verbose = True, save=True):
    """
    Creates a spark df with predicted LEAD conversion rate
   
    :cz_table: Competition Zones table (spark df) with a row for each dealer for each customer zip. 
    	Must have UVs, leads, tc sales, & prospects
    :save: should we save the result?
    :filepath_save: where to save the result
    :score_var: which Competition Zone score to use (e.g. DCZ or CCZ)
    :zone_var: which CZ zone to use (e.g. DCZ Zone, DCZ Zone Exclusize, CCZ Zone, etc.)
    
    :returns: conv_rate_sp, spark df with predicted LEAD conversion rate 

	:sample of output:

    """
  
    t0 = time.time()
    if filepath_save is None:
        filepath_save = 'get_lead_conv_rate_table-{}'.format(dt.datetime.now().strftime('%Y.%m.%d'))
    
    conv_rate_sp  = (cz_table
                   .groupby(['active_start_dt','active_end_dt','make','dealer_size_cat',zone_var,'rank_dist_active_cat'])
                   .agg(f.sum('leads').alias('leads'),f.sum('uv').alias('uvs'))
#                    .toPandas()
                  )
    
    conv_rate_sp = conv_rate_sp.withColumn('conv_rate', conv_rate_sp['leads'] / conv_rate_sp['uvs']).na.fill({'conv_rate':0})
    
    if save:
        if verbose:
            print('\nSaving result file here: {}'.format(filepath_save))
        conv_rate_sp.write.parquet(filepath_save,'overwrite')
        conv_rate_sp = sqlContext.read.parquet(filepath_save)
        
    t1 = time.time()
    if verbose:
        print("Time to process: {0:.3g} minutes.".format((t1-t0)/60.))
    
    return conv_rate_sp
    

def conv_rate_table_master(cz_table, start_dt, end_dt, conv_rate_path, temp_folder, 
						   zone_var = 'DCZ_Zone', save_intermediate = True, 
                           training_set_path = None, states_modifiers_path = None):
    """
    Master function for building Conversion Rate table.
    Saves the conversion rate table to `conv_rate_path`.
    
    Optionally saves training_set & states_modifiers to their respective paths (if not None).
    
    if `save_intermediate` = True, then saves intermediate files to `temp_folder`. 
    
    :start_dt: datetime
    :end_dt: datetime
    :cz_table: Competition Zones table (spark df) with a row for each dealer for each customer zip. 
    :returns: nothing
    """
    
    
    ### 1. identify dealers that are currently active
    print("\n### 1. identify dealers that are currently active")
    active_dlrs = get_active_dlrs(start_dt = start_dt,
                                  end_dt = end_dt)
    active_dlrs = get_dlr_info(df = active_dlrs)

    # missing dealer radius: fill in 150
    active_dlrs['radius'] = active_dlrs['radius'].fillna(150)
    assert active_dlrs.notnull().all().all()

    # create Spark df
    active_sp = sqlContext.createDataFrame(active_dlrs)
    active_sp = active_sp.withColumn('active_dealer',f.lit(1))
    active_sp = active_sp.withColumn('active_start_dt',f.lit(start_dt.strftime('%Y-%m-%d')))
    active_sp = active_sp.withColumn('active_end_dt',f.lit(end_dt.strftime('%Y-%m-%d')))



    ### 1.5 - DCZ table + flag for active dealers + active dealer radius
    print("\n### 1.5 - DCZ table + flag for active dealers + active dealer radius")
    cond = [
        cz_table.unique_id == active_sp.unique_id
        ,cz_table.dealership_id == active_sp.dealership_id
    ]
    cz_active = (cz_table
                  .join(other = active_sp, on = cond, how = 'left_outer')
                  .select([cz_table[col] for col in cz_table.columns]+
                  	 ['active_dealer','radius','active_start_dt','active_end_dt'])
                 ).na.fill({'active_dealer':0})

    # save temp file
    if save_intermediate:
        tempfile_dcz_active = temp_folder + 'cz_active'
        print (tempfile_dcz_active)
        t0 = time.time()
        cz_active.write.parquet(tempfile_dcz_active,'overwrite')
        cz_active = sqlContext.read.parquet(tempfile_dcz_active)
        t1 = time.time()
        print("Time to process: {0:.3g} minutes.".format((t1-t0)/60.))
#    tempfile_dcz_active = temp_folder + 'cz_active'
#    cz_active = sqlContext.read.parquet(tempfile_dcz_active)

    
    ### 2. dealer size cat (based on sales)
    print("\n### 2. dealer size cat (based on sales)")
    dealer_size_cat = get_dlr_size_cat(cz_table = cz_active, 
                                       save = save_intermediate,
                                       filepath_save = temp_folder + '02_dealer_size_cat')


    ### 3. dealer density (nearby dealers: overall & active )
    print("\n### 3. dealer density (nearby dealers: overall & active )")
    dealer_density_sp = get_dealer_density(cz_table = cz_active,
                                           save = save_intermediate,
                                           filepath_save = temp_folder + '03_dealer_density_sp')


    ### 4. limit to active dlrs, and limit to customer zips within each dealer's radius
    print("\n### 4. limit to active dlrs, and limit to customer zips within each dealer's radius")
    dcz2 = get_cz_limited_by_radius(cz_table = cz_active, 
                                    save = save_intermediate,
                                    filepath_save = temp_folder + '04_dcz_active_radius')

    
    ### 5. add leads, sales, & prospects
    # * lead by lead date
    # * sale by lead date
    print("\n### 5. add leads, sales, & prospects")
    SL_sp = get_sales_leads_sp(start_dt = start_dt,
                               end_dt = end_dt,
                               save = save_intermediate,
                               filepath_save = temp_folder + '05_get_sales_leads_sp')
    
    dcz3 = add_sales_leads(cz_table = dcz2, 
                           SL_table = SL_sp,
                           save = save_intermediate,
                           filepath_save = temp_folder + '05b_add_sales_leads')



    ## 6. UVs
    print("\n### 6. UVs")
    uv_sp = get_uvs_sp(start_dt = start_dt, 
                       end_dt = end_dt,
                       save = save_intermediate,
                       filepath_save = temp_folder + '06_get_uvs_sp')

    dcz4 = add_uvs(cz_table = dcz3, 
                   uv_table = uv_sp,
                   save = save_intermediate,
                   filepath_save = temp_folder + '06b_add_uvs')


    #### 7. add density 
    print("\n### 7. add density ")
    dcz5 = add_density(cz_table = dcz4, 
                       density_table = dealer_density_sp,
                       save = (save_intermediate|(training_set_path is not None)),
                       filepath_save = training_set_path)


    ### 8. add dealer size category
    print("\n### 8. add dealer size category")
    dcz6 = add_size_cat(cz_table = dcz5, 
                        size_cat_table = dealer_size_cat,
                        save = save_intermediate,
                        filepath_save = temp_folder + '08_add_size_cat')

    
    ### 9. build conv rate table
    print("\n### 9. build conv rate table")
    conv_rate = get_lead_conv_rate_table(cz_table = dcz6, 
                                         zone_var = 'DCZ_Zone',
                                         filepath_save = conv_rate_path)
    

    ### 10. Build state modifiers
    print("\n ### 10. Build state modifiers")
    if states_modifiers_path is not None:
        state_mod = get_state_modifiers(cz_table = dcz6, 
                                        conv_rate_table = conv_rate, 
                                        zone_var = 'DCZ_Zone', 
                                        filepath_save = states_modifiers_path)


    