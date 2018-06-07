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


def rounded_trunc(x):
    return int(round(max(min(x, 4.9), -2.), 1) * 10)
    
rounded_sp = f.udf(rounded_trunc,  IntegerType())

def add_leads_prediction(cz_table, conv_table, zone_var='DCZ_Zone', save = True, filepath_save = None, verbose = True):
	"""
	Joins predicted conversion to CZ table; Calculates predicted leads.
	fall back logic at the make + cz_zone level

	:cz_table: Competition Zones table (spark df) with a row for each dealer for each customer zip. 
	:zone_var: which CZ zone to use (e.g. DCZ Zone, DCZ Zone Exclusize, CCZ Zone, etc.)
	:conv_table: spark df with predicted conversion rate
	:returns: cz_2, CZ table with conv rate + predicted leads information
	"""

	t0 = time.time()
	if filepath_save is None:
		filepath_save = 'add_leads_prediction-{}'.format(dt.datetime.now().strftime('%Y.%m.%d'))

	cz_table_ = cz_table

	## add dealer size cat - if it does not exist
	if 'dealer_size_cat' not in cz_table_.columns:
		print('get dealer_size_cat')
		dealer_size_cat = get_dlr_size_cat(cz_table = cz_table_.where('active_dealer = 1'), 
										   save = False)
		cz_table_ = add_size_cat(cz_table = cz_table_, 
                        size_cat_table = dealer_size_cat,
                        save = False)

	## get conversion rate
	cond = [
		cz_table_[zone_var] == conv_table[zone_var],
		cz_table_.rank_dist_active_cat == conv_table.rank_dist_active_cat,
		cz_table_.dealer_size_cat == conv_table.dealer_size_cat,
		cz_table_.make == conv_table.make]

	cz_ = (cz_table_
		   .join(other = conv_table, on = cond, how = 'left_outer')
		   .select([cz_table_[col] for col in cz_table_.columns]+['conv_rate'])
		   )

	## fall-back logic if conv rate is Null
	conv_table_agg = conv_table.groupby(['make', zone_var]).agg(
		f.sum('uvs').alias('uvs'), f.sum('leads').alias('leads')
	)
	conv_table_agg = conv_table_agg.withColumn(
		'conv_rate_agg', conv_table_agg.leads * 1. / conv_table_agg.uvs)

	## get conversion rate
	cond = [
		cz_table_[zone_var] == conv_table[zone_var]
		,cz_table_.make == conv_table.make]
	
	cz_2 = (cz_
			   .join(other = conv_table_agg, on = cond, how = 'left_outer')
			   .select([cz_[col] for col in cz_.columns]+['conv_rate_agg'])
		   )

	## get predicted leads
	cz_2 = cz_2.withColumn('pred_leads', 
		f.when(cz_2['conv_rate'].isNotNull(), cz_2['conv_rate'] * cz_2['uv'])
		.otherwise(cz_2['conv_rate_agg'] * cz_2['uv'])
		)

	if save:
		if verbose:
			print('\nSaving result file here: {}'.format(filepath_save))
		cz_2.write.parquet(filepath_save,'overwrite')
		cz_2 = sqlContext.read.parquet(filepath_save)
		t1 = time.time()
		print("Time to process: {0:.3g} minutes.".format((t1-t0)/60.))

	return cz_2
	
	
	
def get_uvs_pag_sp(start_dt, end_dt, save = True, filepath_save = None, verbose = True):
	"""
	Queries redshift and returns a spark df with UV data (unique visitors).

	:start_dt: datetime
	:end_dt: datetime
	:return: uvs, spark df with uv count for each make + search zip + pag-group.
			 
	:sample output:
	+----------+-------------+-----+---------+-------+-------+
	|search_zip|         make|   uv|uv_extpar|uv_tcdc|uv_usaa|
	+----------+-------------+-----+---------+-------+-------+
	|     92562|          gmc| 82.0|     21.0|   52.0|    9.0|
	|     92562|        honda|436.0|    107.0|  280.0|   49.0|
	|     92562|      hyundai|158.0|     30.0|  120.0|    8.0|
	|     92562|     infiniti| 48.0|      6.0|   41.0|    1.0|
	+----------+-------------+-----+---------+-------+-------+
	"""

	t0 = time.time()
	if filepath_save is None:
		filepath_save = 'get_uvs_pag_sp-{}'.format(dt.datetime.now().strftime('%Y.%m.%d'))


	## define query I will use to get UVs
	uv_qry = """
	SELECT
		a.postal_code                                                       as search_zip
		,lower(M.make_name)                                                 as make
		,CASE WHEN a.affinity_group_id in (2, 62, 75, 81, 116)          THEN 'usaa' 
				  WHEN a.affinity_group_id in (77)                      THEN 'tcdc' 
				  ELSE 'extpar'                             
				  END                                                       as pag 
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
		,CASE WHEN a.affinity_group_id in (2, 62, 75, 81, 116)          THEN 'usaa' 
				  WHEN a.affinity_group_id in (77)                      THEN 'tcdc' 
				  ELSE 'extpar'                             
				  END 
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

	## aggregate  by dealer, search zip, pag

	idx_vars = ['search_zip','make']
	uvs = (uvs
				 .groupby(idx_vars+['pag'])
				 ['uv']
				 .sum()
				 .reset_index()
				)
		
	## Add 'total' pag-group
	uvs_total = uvs.copy()
	uvs_total = (uvs_total
				.groupby(idx_vars)
				['uv']
				.sum()
				.reset_index()
			   )
	uvs_total['pag'] = 'total'
	uvs_total = uvs_total[uvs.columns]
	uvs = uvs.append(uvs_total)
	uvs2 = reshape_wide(df = uvs,
					   idx_vars = idx_vars,
					   unstack_var = 'pag'
					   )			   
	uvs2 = uvs2.fillna(0)

	## rename 'total' cols, e.g. leads_total -> leads
	dict_rename={}
	for x in uvs2.columns:
		if '_total' in x:
			dict_rename[x] = x.replace('_total', '')
	uvs2.rename(columns=dict_rename,inplace=True)

	## re-arrange order of columns
	uvs2 = uvs2[
		idx_vars
		+ sorted(set(uvs2.columns).difference(idx_vars))
	]

	uvs_sp = sqlContext.createDataFrame(uvs2)
	
	if save:
		if verbose:
			print('\nSaving result file here: {}'.format(filepath_save))
		uvs_sp.write.parquet(filepath_save,'overwrite')
		uvs_sp = sqlContext.read.parquet(filepath_save)
		t1 = time.time()
		print("Time to process: {0:.3g} minutes.".format((t1-t0)/60.))

	return uvs_sp
	
	
	
def add_sales_prediction(cz_table, close_table, score_var='DCZ', pags_=['tcdc','usaa','extpar',''],
    save = True, filepath_save = None, verbose = True):
	"""
	Joins predicted close rate to CZ table; Calculates predicted sales.

	:cz_table: Competition Zones table (spark df) with a row for each dealer for each customer zip. 
    :score_var: which Competition Zone score to use (e.g. DCZ or CCZ)
	:close_table: spark df with predicted close rate
	:returns: cz_2, CZ table with close rate + predicted sales information
	"""
	
	t0 = time.time()
	if filepath_save is None:
		filepath_save = 'add_sales_prediction-{}'.format(dt.datetime.now().strftime('%Y.%m.%d'))

	cz_table_ = cz_table
	
	rounded_score = 'rounded_{}'.format(score_var)
	close_table = close_table.withColumn(rounded_score, rounded_sp(close_table[score_var]))
	cz_table_ = cz_table_.withColumn(rounded_score, rounded_sp(cz_table_[score_var]))
	
	
	## merge conv rate
	cond = [
		cz_table_.make == close_table.make,
		cz_table_[rounded_score] == close_table[rounded_score],
	]

	cz_table_2 = (cz_table_
			   .join(other=close_table, on=cond, how='left_outer')
			   .select([cz_table_[col] for col in cz_table_.columns] +
					   ['pred_CR_tcdc', 'pred_CR_usaa', 'pred_CR_extpar', 'pred_CR',])
			   )

	#### calc pred leads
	cz_table_2 = cz_table_2.withColumn('pred_sales', cz_table_2['pred_leads'] * cz_table_2['pred_CR'])
	
	if save:
		if verbose:
			print('\nSaving result file here: {}'.format(filepath_save))
		cz_table_2.write.parquet(filepath_save,'overwrite')
		cz_table_2 = sqlContext.read.parquet(filepath_save)
		t1 = time.time()
		print("Time to process: {0:.3g} minutes.".format((t1-t0)/60.))
		
	return cz_table_2




def simple_pred_master(cz_table, conv_table, close_table, simple_pred_path_parquet, temp_folder, 
	start_dt, end_dt,
						score_var='DCZ', zone_var='DCZ_Zone',
						   pags_=['tcdc','usaa','extpar',''],
						   cz_score_var = 'DCZ', save = True, save_intermediate = True, verbose = True):
	"""
	Master function for Simple Prediction: Sales = UVs * Pred Conv Rate * Pred Close Rate

	:start_dt: datetime
	:end_dt: datetime
	:cz_table: Competition Zones table (spark df) with a row for each dealer for each customer zip. 
	:cz_score_var: Competition Zones score variable (e.g. DCZ, CCZ)	
	:zone_var: which CZ zone to use (e.g. DCZ Zone, DCZ Zone Exclusize, CCZ Zone, etc.)
	"""
	t0 = time.time()

	### 1. Add UVs by PAG
	print("\n### 1. Add UVs by PAG")
	uvs_pag_sp = get_uvs_pag_sp(start_dt = start_dt, 
							end_dt = end_dt,
							save = save_intermediate,
							verbose = verbose,
							filepath_save = temp_folder + 'uvs_pag_sp')
						
	cz1 = add_uvs(cz_table = cz_table, 
			  uv_table = uvs_pag_sp, 
			  uv_col_list = ['uv','uv_tcdc','uv_usaa','uv_extpar'],
			  save = save_intermediate,
			  verbose = verbose,
			  filepath_save = temp_folder + '01_add_uvs_by_pag')


	### 2. Add Conv Rate to data; get Predicted Leads
	print("\n### 2. Add Conv Rate to data; get Predicted Leads")
	cz2 = add_leads_prediction(cz_table = cz1,
						   conv_table = conv_table,
						   zone_var=zone_var,
						   save = save_intermediate,
						   verbose = verbose,
						   filepath_save = temp_folder + '02_add_leads_prediction')
					   

	### 3. Add Close Rate to data; get Predicted Sales
	print("\n### 2. Add Close Rate to data; get Predicted Sales")  
	cz3 = add_sales_prediction(cz_table = cz2, 
							   close_table = close_table,
							   score_var=score_var,
							   pags_=pags_,
							   save = save_intermediate, 
							   verbose = verbose,
							   filepath_save = temp_folder + '03_add_sales_prediction')
						   
	if save:
		if verbose:
			print('\nSaving result file here: {}'.format(simple_pred_path_parquet))
		cz3.write.parquet(simple_pred_path_parquet,'overwrite')
		cz3 = sqlContext.read.parquet(simple_pred_path_parquet)
	
	t1 = time.time()
	if verbose:
		print("Time to process: {0:.3g} minutes.".format((t1-t0)/60.))
	
	return cz3

