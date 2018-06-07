import pandas
import psycopg2
import time
import re
import datetime as dt
from sklearn.isotonic import IsotonicRegression
from pyspark.sql import Row
from pyspark.sql.types import *
from pyspark.sql.window import Window
import pyspark.sql.functions as f
from pyspark.sql import SQLContext, Row, HiveContext
from pyspark import SparkContext, SparkConf


def get_sales_leads_pag_sp(start_dt, end_dt, plus_days = 31, save = True, filepath_save = None, verbose = True):
	"""
	Queries redshift bi_dw and returns a spark df:
	['tc_sales','leads','prospects'], aggregated by ['dealership_id','search_zip','make','pag']
			 
	Note: pag refers to pag-group: usaa, tcdc, extpar (extended partner), and total
			 
	:start_dt: datetime
	:end_dt: datetime
	:plus_days: sales must be approved within this many days after end_dt
	:return: SL_sp, spark df with sales, leads, and prospects for each dealer, make, & search zip
			 
	:sample output:
	+-------------+----------+-----+-----+------------+----------+----------+---------+
	|dealership_id|search_zip| make|leads|leads_extpar|leads_tcdc|leads_usaa|prospects|
	+-------------+----------+-----+-----+------------+----------+----------+---------+
	|         5281|     07726|mazda| 22.0|        10.0|      12.0|       0.0|     15.0|
	|         5281|     07727|mazda|  3.0|         2.0|       1.0|       0.0|      3.0|
	|         5281|     07728|mazda| 25.0|        10.0|      14.0|       1.0|     23.0|
	|         5281|     07730|mazda|  3.0|         2.0|       1.0|       0.0|      2.0|
	|         5281|     07731|mazda| 10.0|         5.0|       3.0|       2.0|      9.0|
	+-------------+----------+-----+-----+------------+----------+----------+---------+
	"""

	t0 = time.time()
	if filepath_save is None:
		filepath_save = 'get_sales_leads_pag_sp-{}'.format(dt.datetime.now().strftime('%Y.%m.%d'))

	## define query I will use to get sales and leads
	my_qry_SL = """
	SELECT 
		A.dealership_id
		,lower(M.make_name)                  AS make
		,A.postal_code                       as search_zip
		,CASE WHEN a.affinity_group_id in (2, 62, 75, 81, 116) THEN 'usaa' 
			  WHEN a.affinity_group_id in (77)                 THEN 'tcdc' 
			  ELSE 'extpar'                             
			  END                            as pag
	
		,COUNT(DISTINCT A.email_hash)        AS prospects
		,COUNT(DISTINCT A.leadgen_lead_id)   AS leads
		,COUNT(DISTINCT CASE WHEN( (R.approved_date IS NOT NULL)
								   AND (R.approved_date < '{approved_date_cutoff}') )
						THEN A.email_hash END) as tc_sales

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
		AND a.date_id BETWEEN '{start_dt}' AND '{end_dt}'

	GROUP BY
		A.dealership_id    
		,lower(M.make_name) 
		,A.postal_code   
		,CASE WHEN a.affinity_group_id in (2, 62, 75, 81, 116) THEN 'usaa' 
			  WHEN a.affinity_group_id in (77)                 THEN 'tcdc' 
			  ELSE 'extpar'                             
			  END                            
			   
	ORDER BY
		A.dealership_id
		,lower(M.make_name) 
		,A.postal_code   
		,CASE WHEN a.affinity_group_id in (2, 62, 75, 81, 116) THEN 'usaa' 
			  WHEN a.affinity_group_id in (77)                 THEN 'tcdc' 
			  ELSE 'extpar'                             
			  END                            
	""".format(start_dt = start_dt.strftime('%Y-%m-%d'),
	           end_dt = end_dt.strftime('%Y-%m-%d'),
	           approved_date_cutoff = (end_dt + pd.DateOffset(days=plus_days)).strftime('%Y-%m-%d')
	           )

	if verbose:
		print(my_qry_SL)

	idx_vars = ['dealership_id','search_zip','make']

	SL = run_query_redshift(my_qry_SL, verbose = verbose)

	## aggregate TC sales, leads, and prospects 
	# by dealer, search zip, pag
	SL = (SL
				 .groupby(['dealership_id','search_zip','make','pag'])
				 ['tc_sales','leads','prospects']
				 .agg(np.sum)
				 .reset_index()
				)
			
	## Add 'total' pag-group
	SL_total = SL.copy()
	SL_total = (SL_total
				.groupby(idx_vars)
				['tc_sales','leads','prospects']
				.sum()
				.reset_index()
			   )
	SL_total['pag'] = 'total'
	SL_total = SL_total[SL.columns]
	SL = SL.append(SL_total)
	SL2 = reshape_wide(df = SL,
					   idx_vars = idx_vars,
					   unstack_var = 'pag'
					   )
				   
	SL2 = SL2.fillna(0)
	
	## rename 'total' cols, e.g. leads_total -> leads
	dict_rename={}
	for x in SL2.columns:
		if '_total' in x:
			dict_rename[x] = x.replace('_total', '')
	SL2.rename(columns=dict_rename,inplace=True)

	## re-arrange order of columns
	SL2 = SL2[
		idx_vars
		+ sorted(set(SL2.columns).difference(['dealership_id', 'new_used', 'make', 'search_zip', ]))
	]
# 	SL2.sort_values(idx_vars,inplace=True)

	## make spark df            
	SL_sp = sqlContext.createDataFrame(SL2)
	SL_sp = SL_sp.withColumn('make', f.lower(f.col('make')))
	SL_sp = SL_sp.orderBy(idx_vars)

	if save:
		if verbose:
			print('\nSaving result file here: {}'.format(filepath_save))
		SL_sp.write.parquet(filepath_save,'overwrite')
		SL_sp = sqlContext.read.parquet(filepath_save)
		t1 = time.time()
		print("Time to process: {0:.3g} minutes.".format((t1-t0)/60.))

	return SL_sp
	
	
def add_sales_leads_pag(cz_table, SL_table, to_pandas = True, replace_SL = True, save = True, 
	filepath_save = None, verbose = True, where_str='leads > 0'):  
	"""
	Takes the CZ table and adds sales, leads, and prospects (by pag) to it.
	:cz_table: Competition Zones table (spark df) with a row for each dealer for each customer zip. 
	:SL_table: spark df with sales, leads, & prospects for each dealer, make, & search zip
	:replace_SL: if True drop the existing sales/leads/prospects fields from cz_table
	:returns: cz_, CZ table with sales, leads, & prospects 
	"""

	t0 = time.time()
	if filepath_save is None:
		filepath_save = 'add_sales_leads_pag-{}'.format(dt.datetime.now().strftime('%Y.%m.%d'))
	
	cond  = [
		cz_table.make == SL_table.make
		,cz_table.zip == SL_table.search_zip
		,cz_table.dealership_id == SL_table.dealership_id
	]

	## if replace_SL, get rid of certain pre-existing columns
	cz_table_ = cz_table
	if replace_SL:
		drop_cols = []
		for x in ['tc_sales','leads','prospects']:
			drop_cols+=[y for y in cz_table_.columns if x in y]
		if verbose:
			print("Dropping these columns: {}".format(", ".join(drop_cols)))
		for x in drop_cols:
			cz_table_ = cz_table_.drop(x)

	sl_cols = []
	for x in ['tc_sales','leads','prospects']:
		sl_cols+=[y for y in SL_table.columns if x in y]
	if verbose:
		print("Adding these columns: {}".format(", ".join(sl_cols)))
	
	cz_ = (cz_table_
		   .join(other = SL_table, on = cond, how = 'left_outer')
		   .select([cz_table_[col] for col in cz_table_.columns]+sl_cols)
		   ).na.fill({'prospects':0,'leads':0,'sales':0,'tc_sales':0})

	cz_ = cz_.where(where_str)

	if save:
		if verbose:
			print('Saving result file here: {}'.format(filepath_save))
		cz_.write.parquet(filepath_save,'overwrite')
		cz_ = sqlContext.read.parquet(filepath_save)
		t1 = time.time()
		print("Time to process: {0:.3g} minutes.".format((t1-t0)/60.))

	if to_pandas:
		cz_ = cz_.toPandas()

	return cz_	
	
	
def ludovica_smoothing(df_, leads_column, sales_column, make, cz_score_var='DCZ',  q=1.):
	"""
	Aggregates observations by CZ score (e.g. DCZ) and calculates close rate within each group.

	:df_: data frame with CZ score, leads, and sales (by dealer & customer zip)
	:cz_score_var: Competition Zones score variable (e.g. DCZ, CCZ)	
	:returns: cz_agg, pandas df_2 with CZ score and close rate for the group of observations with that (approx) score
	"""

	if make:
		make = make if isinstance(make,list) else [make]
		df_2 = df_[df_.make.isin(make)].sort_values(by=[cz_score_var]).reset_index(drop=True)
	else:
		df_2 = df_.sort_values(by=[cz_score_var]).reset_index(drop=True)
	n = df_2[leads_column].sum()
	df_2['cum_leads'] = df_2[leads_column].cumsum()
	df_2['cum_leads_cat'] = 100*df_2.cum_leads // (n*q)
	cz_agg = df_2.groupby('cum_leads_cat').agg({cz_score_var:max,sales_column:sum,leads_column:sum})
	cz_agg['close_rate'] = cz_agg[sales_column] * 1. / cz_agg[leads_column]
	return cz_agg[[cz_score_var,'close_rate']]


def right_predict_function(x,irs,Make,_Min,_Max,mins,maxs,make_list_):
	"""
	Makes prediction using Isotonic Regression
	"""
	idx = make_list_.index(Make)
	ir = irs[idx]
	Min = max(mins[idx],_Min)
	Max = min(maxs[idx],_Max)
	if (x <= Max) and (x >= Min):
		return ir.predict([x])[0]
	elif (x > Max):
		return ir.predict([Max])[0]
	else:
		return ir.predict([Min])[0]
        
        
def get_pred_close_rate_by_make_pag(df_, make_list_, cz_score_var='DCZ', pags_=['tcdc','usaa','extpar','']):
	"""
	Creates lists with predicted close rates for each make in `make_list_`.
	
	:df_: data frame with CZ score, leads, and sales (by dealer & customer zip)
	:make_list_: list of makes (Honda, BMW, etc.)
	:pags_: list of pag-groups. Note that '' refers to the overall (not pag-specific) analysis
	:cz_score_var: Competition Zones score variable (e.g. DCZ, CCZ)	
	:returns: cr_dict, a dictionary with a list for each pag: IR (isotonic regression), min, and max.
	"""
	
	cr_dict = {}
	for pag in pags_:
	
		pag2 = pag
		if pag2 != '': pag2 = '_'+pag2
	
		## initialize list objects
		current_mins = []
		current_maxs = []
		current_irs = []
	
		lead_var = 'leads'+pag2
		sales_var = 'tc_sales'+pag2

		## calculate IR for each make
		for make in make_list_:
	
			alias = df_[(df_.make==make) & (df_[cz_score_var].notnull())].copy()
			q = 2.0
			if make in ['volvo','cadillac','land rover','audi']:
				q = 10.
	
			dfl = ludovica_smoothing(alias,lead_var,sales_var,make=[],q=q)
			current_mins.append(dfl[cz_score_var].min())
			current_maxs.append(dfl[cz_score_var].max())
			ir = IsotonicRegression(increasing=False)
			current_irs.append(ir)
			ir.fit(dfl[cz_score_var].values,dfl.close_rate.values)
			xnew = np.linspace(-10, 20, num=301, endpoint=True)
			y_ir = ir.predict(xnew)
		
		## add results for this pag to dict
		cr_dict[pag] = {'mins':current_mins,
						 'maxs':current_maxs,
						 'irs':current_irs}
	return cr_dict
		
	
	
def close_rate_table_master(cz_table, start_dt, end_dt, plus_days,
                           cr_path_csv, cr_path_parquet, temp_folder, 
                           pags_=['tcdc','usaa','extpar',''],
                           cz_score_var = 'DCZ', save_intermediate = True):
    """
    Master function for building Close Rate table.
    Saves the conversion rate table to `cr_path_csv` and/or `cr_path_parquet`
    
    Optionally saves training_set & states_modifiers to their respective paths (if not None).
    
    :start_dt: datetime
    :end_dt: datetime
    :cz_table: Competition Zones table (spark df) with a row for each dealer for each customer zip. 
    :cz_score_var: Competition Zones score variable (e.g. DCZ, CCZ)	
    :returns: cr_df, a data frame with predicted close rate by pag & incr. value of CZ score
    
    :sample output:
    +----+-----+-----+------------+------------+--------------+-------+
    | DCZ| make|make_|pred_CR_tcdc|pred_CR_usaa|pred_CR_extpar|pred_CR|
    +----+-----+-----+------------+------------+--------------+-------+
    |-0.9|acura|acura|       0.129|       0.178|         0.105|  0.126|
    |-0.8|acura|acura|       0.125|       0.178|         0.096|  0.124|
    |-0.7|acura|acura|       0.119|       0.168|         0.089|  0.116|
    +----+-----+-----+------------+------------+--------------+-------+
    """
    
    
    ### 1. get sales and leads, by PAG
    print("\n### 1. get sales and leads, by PAG")
    SL_sp = get_sales_leads_pag_sp(start_dt = start_dt, 
                                   end_dt = end_dt,
                                   plus_days = plus_days,
                                   save = save_intermediate,
                                   filepath_save = temp_folder + 'get_sales_leads_pag_sp')
    
    cz_table2 = add_sales_leads_pag(cz_table = cz_table,
                                    SL_table = SL_sp,
                                    save = save_intermediate,
                                    replace_SL = True,
                                    filepath_save = temp_folder + 'add_sales_leads_pag')
    
    ### 2. Build close rate predictor
    print("\n### 2. Build close rate predictor")
    
    # identify makes
    cz_table2['make_'] = cz_table2.make
    make_list = cz_table2.make_.unique()
    low_volume = ['alfa romeo', 'aston martin', 'bentley', 'ferrari', 'fiat', 'genesis', 'jaguar', 'lamborghini', 
                  'lincoln', 'lotus', 'maserati', 'mini', 'mitsubishi', 'porsche', 'rolls', 'rolls-royce', 'scion', 'smart']
    make_list = [x for x in make_list if x not in low_volume]+['low_volume']
    print (make_list)
    cz_table2.make = cz_table2.make_.apply(lambda x: 'low_volume' if x in low_volume else x)
    
    cr_dict = get_pred_close_rate_by_make_pag(df_ = cz_table2,
                                              make_list_ = make_list,
                                              cz_score_var=cz_score_var,
                                              pags_=pags_)
    
    ### 3. Store the output
    print("\n### 3. Store the output")
    x = [x / 10.0 for x in range(-20, 50,1)]
    first = pd.DataFrame({cz_score_var:x})
    first['key'] = 1
    second = cz_table2[['make','make_']].drop_duplicates()
    second['key'] = 1
    cr_df = pd.merge(first,second,on='key')
    cr_df.drop('key',inplace=True,axis=1)
    cr_df.sort_values(['make','make_'],inplace=True)
    
    for pag in pags_:
        pag2 = pag
        if pag2 != '': pag2 = '_'+pag2
        CR_var = "pred_CR{x}".format(x=pag2)
        cr_df[CR_var] = cr_df.apply(lambda x:right_predict_function(x = x[cz_score_var],
                                                                    irs = cr_dict[pag]['irs'],
                                                                    Make = x.make,
                                                                    _Min = -1,
                                                                    _Max = 6,
                                                                    mins = cr_dict[pag]['mins'],
                                                                    maxs = cr_dict[pag]['maxs'],
                                                                    make_list_ = make_list
                                                                     )
                                      ,axis=1 )
        
    ### 4. Save
    print("\n### 4. Save")
    
    ## csv
    if cr_path_csv is not None:
        current_file = cr_path_csv
        current_data = cr_df

        print(current_file)
        to_write = current_data.to_csv(None, index=False).encode()
        with fs.open(current_file, 'wb') as f:
            f.write(to_write)
        print(subprocess.check_output(['aws','s3','ls',current_file,]).decode('utf-8'))
    
    ## parquet
    if cr_path_parquet is not None:
        sqlContext.createDataFrame(cr_df).write.parquet(cr_path_parquet,'overwrite')
        print(fs.ls(cr_path_parquet.replace('s3a://','s3://'),detail=True)[0])
        
    return cr_df
	
