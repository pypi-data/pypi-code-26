from __future__ import (absolute_import,
                        division,
                        print_function,
                        unicode_literals)

# TODO: NEED TESTS!!!
# class Testoghfunctions(object):

#     def setup(self):
#         pass

#     def test_saveDictOfDf(self):
#         pass
    
#     def test_saveDictOfDf(self):
#         pass


# loading and saving dataframes and dictionaries
import ogh, os, pandas as pd
import pytest

class Test_ogh_load_functions(object):

    def test_ogh_meta():
        keys = dict(ogh.ogh_meta())
        if len(keys)>0:
            pass


    def test_DictOfDf():
        path ='tests/data/test.json'
        obj1 = pd.DataFrame({'foo':['a','b'],'bar':[1,2]})
        obj2 = ['foo','bar']

        # savedictofdf success
        ogh.saveDictOfDf(path, obj1)
        assert os.path.exists(path)

        # readdictofdf success
        test = ogh.readDictOfDf(path)
        assert True

        # savedictofdf fail
        try:
            ogh.saveDictOfDf(path, obj2)
        except:
            os.remove(path)
            assert True

    def test_ensuredir():
        path0 = os.getcwd()
        path1 = 'tests/data/test_subfolder'
        ogh.ensuredir(path1)
        ogh.ensuredir(path0)
        assert os.path.exists(path1)
        
        
class Test_mappingfile_ops(object):
    def test_readmappingfile():
        test_map = ogh.mappingfileToDF(mappingfile='tests/data/test_mapping.csv', colvar='all', summary=True)
        assert True

        test_compare = ogh.compareonvar(map_df=test_map, colvar=None)
        assert True

    
# loading and saving shapefiles
import ogh, os, pandas as pd, numpy as np, geopandas as gpd
import pytest

class Test_ogh_shape_functions(object):

    def test_shapefile_reading():
        path='tests/data/shape.shp'

        # getFullShape success
        test = ogh.getFullShape(path)
        assert True

        # readShapefileTable success
        test = ogh.readShapefileTable(shapefile='tests/data/shape.shp')
        assert True

        # getShapeBbox
        test = ogh.getShapeBbox(fiona.open(path))
        assert True


    def test_reprojShapefile():
        ogh.reprojShapefile(sourcepath='tests/data/shape.shp', 
                            newprojdictionary={'proj':'longlat', 'ellps':'WGS84', 'datum':'WGS84'})
        assert True


    def test_treatgeoself_parts():
        inpath='tests/data/shape.shp'
        outpath='tests/data/test_mappingfile.csv'

        # reading in the shapefile
        test_poly=gpd.read_file(inpath)
        assert True

        # generate lat-lon
        test_lon, test_lat= np.array(test_poly.centroid[0])

        # filterPointsinShape
        test_maptable = ogh.filterPointsinShape(shape=test_poly.geometry[0], 
                                                points_lat=test_lat, points_lon=test_lon, points_elev=None, 
                                                buffer_distance=0.06, buffer_resolution=16, labels=['LAT', 'LONG_', 'ELEV'])
        test_maptable = test_maptable.reset_index(inplace=True).rename(columns={"index":"FID"})
        assert len(test_maptable)>0

        # print the mappingfile
        test_maptable.to_csv(outpath, sep=',', header=True, index=False)
        assert os.path.exists(outpath)

    
# spatial mapping
import ogh, os, pandas as pd
import pytest

class Test_ogh_spatial_mapping(object):

    def test_canadabox_bc():
        test = ogh.canadabox_bc()
        assert True


    def test_mapContentFolder():
        test = ogh.mapContentFolder('test')
        assert True


    def test_mapfilelocations():
        test_maptable = pd.read_csv('tests/data/test_mappingfile.csv')

        # livneh 2013
        assert ogh.compile_dailyMET_Livneh2013_locations(test_maptable) is not None
        assert ogh.compile_VICASCII_Livneh2013_locations(test_maptable) is not None
        
        # livneh 2013 (CIG)
        assert ogh.compile_Livneh2013_locations(test_maptable) is not None
        assert ogh.compile_bc_Livneh2013_locations(test_maptable) is not None

        # livneh 2015
        assert ogh.compile_dailyMET_Livneh2015_locations(test_maptable) is not None
        assert ogh.compile_VICASCII_Livneh2015_locations(test_maptable) is not None

        # Salathe 2014
        assert ogh.compile_wrfnnrp_raw_Salathe2014_locations(test_maptable) is not None
        assert ogh.compile_wrfnnrp_bc_Salathe2014_locations(test_maptable) is not None



# web scraping
import ogh
import pytest

class Test_ogh_webscraping(object):

    def test_scrapeurl():
        path = 'test'
        filenames=ogh.scrapeurl(path, startswith='data')
        assert len(filenames)>0


    def test_scrapedomain():
        # gridded data product metadata
        domain='livnehpublicstorage.colorado.edu'
        subdomain='/public/Livneh.2013.CONUS.Dataset/Fluxes.asc.v.1.2.1915.2011.bz2'

        # identify the subfolder blocks
        blocks = ogh.scrape_domain(domain=domain, subdomain=subdomain, startswith='fluxes')
        assert len(blocks)>0

    

# web download
import ftplib, ogh, os
import pytest

class Test_ogh_webdownload(object):

    def test_ftp_download():
        protocol = 'ftp://'
        ipaddress = 'livnehpublicstorage.colorado.edu/'
        subdomain = 'public/Livneh.2013.CONUS.Dataset/Fluxes.asc.v.1.2.1915.2011.bz2/fluxes.100.95.25.36/'
        filename1 = 'VIC_fluxes_Livneh_CONUSExt_v.1.2_2013_25.90625_-97.40625.bz2' # real
        filename2 = 'VIC_fluxes_Livneh_CONUSExt_v.1.2_2013_25.90625_-97.40626.bz2' # fake

        # connect to ipaddress and subfolder
        try:
            ftp=ftplib.FTP(ipaddress)
            ftp.login()
            ftp.cwd(subdomain)

            # connection success
            if len(ftp.nlst(filename1))==1:
                assert True

            # connection fail
            if len(ftp.nlst(filename2))==0:
                assert True

            ftp.close()
        except:
            pass


    def test_ftp_download_one():
        protocol = 'ftp://'
        ipaddress = 'livnehpublicstorage.colorado.edu/'
        subdomain = 'public/Livneh.2013.CONUS.Dataset/Fluxes.asc.v.1.2.1915.2011.bz2/fluxes.100.95.25.36/'
        filename1 = 'VIC_fluxes_Livneh_CONUSExt_v.1.2_2013_25.90625_-97.40626.bz2' # fake

        urlofinterest=os.path.join(protocol, ipaddress, subdomain, filename1)
        ogh.ftp_download_one(urlofinterest)
        assert True


    def test_ftp_download_p():
        protocol = 'ftp://'
        ipaddress = 'livnehpublicstorage.colorado.edu/'
        subdomain = 'public/Livneh.2013.CONUS.Dataset/Fluxes.asc.v.1.2.1915.2011.bz2/fluxes.100.95.25.36/'
        filename1 = 'VIC_fluxes_Livneh_CONUSExt_v.1.2_2013_25.90625_-97.40625.bz2' # real
        filename2 = 'VIC_fluxes_Livneh_CONUSExt_v.1.2_2013_25.90625_-97.40626.bz2' # fake

        listofinterest=[os.path.join(protocol, ipaddress, subdomain, filename1), 
                        os.path.join(protocol, ipaddress, subdomain, filename2)]
        ogh.ftp_download_p(listofinterest)
        assert True


    def test_wget_download():
        listofinterest=['test1', 'test2']
        ogh.wget_download(listofinterest)
        assert True


    def test_wget_download_one():
        urlofinterest='test1'
        ogh.wget_download_one(urlofinterest)
        assert True


    def test_wget_download_p():
        listofinterest=['test1', 'test2']
        ogh.wget_download_p(listofinterest)
        assert True


# Download the files to the subdirectory
import ogh
import pytest

class Test_ogh_cataloging(object):

    folderpath='tests/data/test_files/' # has sample file
    
    def test_catalogfiles():
        test = ogh.catalogfiles(folderpath)
        assert True

    def test_addCatalogToMap():
        # read in a sample mappingfile as test_map
        test_map = ogh.mappingfileToDf('tests/data/test_mappingfile.csv', colvar=None)
        ogh.addCatalogToMap(outfilepath='tests/data/test_catalog.csv', 
                            maptable=test_map, 
                            folderpath=folderpath,
                            catalog_label='test')
        assert True

    
# Wrapper scripts
import ogh, os
import pytest

class Test_ogh_wrappedget(object):

    def test_getDailyMET_livneh2013():
        ogh.getDailyMET_livneh2013(homedir=os.getcwd(), mappingfile='tests/data/test_mappingfile.csv', 
                                   subdir='tests/data/test_files', catalog_label='dailymet_livneh2013')
        assert True
    
    def test_getDailyMET_livneh2015():
        ogh.getDailyMET_livneh2015(homedir=os.getcwd(), mappingfile='tests/data/test_mappingfile.csv',
                                   subdir='tests/data/test_files', catalog_label='dailymet_livneh2015')
        assert True
        

    def test_getDailyMET_bcLivneh2013():
        ogh.getDailyMET_bcLivneh2013(homedir=os.getcwd(), mappingfile='tests/data/test_mappingfile.csv',
                                     subdir='tests/data/test_files',catalog_label='dailymet_bclivneh2013')
        assert True


    def test_getDailyVIC_livneh2013():
        ogh.getDailyVIC_livneh2013(homedir=os.getcwd(), mappingfile='tests/data/test_mappingfile.csv',
                                   subdir='tests/data/test_files', catalog_label='dailyvic_livneh2013')
        assert True
        
    def test_getDailyVIC_livneh2015():
        ogh.getDailyVIC_livneh2015(homedir=os.getcwd(), mappingfile='tests/data/test_mappingfile.csv',
                                   subdir='tests/data/test_files', catalog_label='dailyvic_livneh2015')
        assert True
    

    def test_getDailyWRF_salathe2014():
        ogh.getDailyWRF_salathe2014(homedir=os.getcwd(), mappingfile='tests/data/test_mappingfile.csv',
                                    subdir='tests/data/test_files', catalog_label='dailywrf_salathe2014')
        assert True
        

    def test_getDailyWRF_bcsalathe2014():
        ogh.getDailyWRF_bcsalathe2014(homedir=os.getcwd(), mappingfile='tests/data/test_mappingfile.csv', 
                                      subdir='tests/data/test_files', catalog_label='dailywrf_bcsalathe2014')
        assert True

        
# # Data Processing libraries

        
# data reading and processing
        
# def read_in_all_files(map_df, dataset, metadata, file_start_date, file_end_date, file_time_step, file_colnames, file_delimiter, subset_start_date, subset_end_date):
#     """
#     Read in files based on dataset label
    
#     map_df: (dataframe) the mappingfile clipped to the subset that will be read-in
#     dataset: (str) the name of the dataset catalogged into map_df
#     metadata (str) the dictionary that contains the metadata explanations; default is None
#     file_colnames: (list) the list of shorthand variables; default is None
#     file_start_date: (date) the start date of the files that will be read-in; default is None
#     file_end_date: (date) the end date for the files that will be read in; default is None
#     file_time_step: (str) the timedelta code that represents the difference between time points; default is 'D' (daily)    
#     subset_start_date: (date) the start date of a date range of interest
#     subset_end_date: (date) the end date of a date range of interest
#     """
#     # extract metadata if the information are not provided
#     if pd.notnull(metadata):
        
#         if isinstance(file_start_date, type(None)):
#             file_start_date = metadata[dataset]['start_date']
        
#         if isinstance(file_end_date, type(None)):
#             file_end_date = metadata[dataset]['end_date']

#         if isinstance(file_time_step, type(None)):
#             file_time_step = metadata[dataset]['temporal_resolution']

#         if isinstance(file_colnames, type(None)):
#             file_colnames = metadata[dataset]['variable_list']
        
#         if isinstance(file_delimiter, type(None)):
#             file_delimiter = metadata[dataset]['delimiter']
   
#     #initialize dictionary and time sequence
#     df_dict=dict()
#     met_daily_dates=pd.date_range(file_start_date, file_end_date, freq=file_time_step) # daily
        
#     # import data for all climate stations
#     for ind, row in map_df.iterrows():
#         tmp = pd.read_table(row[dataset], header=None, delimiter=file_delimiter, names=file_colnames)
#         tmp.set_index(met_daily_dates, inplace=True)
        
#         # subset to the date range of interest (default is file date range)
#         tmp = tmp.iloc[(met_daily_dates>=subset_start_date) & (met_daily_dates<=subset_end_date),:]
        
#         # set row indices
#         df_dict[tuple(row[['FID','LAT','LONG_']].tolist())] = tmp
        
#     return(df_dict)


# def read_files_to_vardf(map_df, df_dict, gridclimname, dataset, metadata, 
#                         file_start_date, file_end_date, file_delimiter, file_time_step, file_colnames, 
#                         subset_start_date, subset_end_date, min_elev, max_elev):
#     """
#     # reads in the files to generate variables dataframes
    
#     map_df: (dataframe) the mappingfile clipped to the subset that will be read-in
#     df_dict: (dict) an existing dictionary where new computations will be stored
#     gridclimname: (str) the suffix for the dataset to be named; if None is provided, default to the dataset name
#     dataset: (str) the name of the dataset catalogged into map_df
#     metadata: (str) the dictionary that contains the metadata explanations; default is None
#     file_start_date: (date) the start date of the files that will be read-in; default is None
#     file_end_date: (date) the end date for the files that will be read in; default is None
#     file_delimiter: (str) a file parsing character to be used for file reading
#     file_time_step: (str) the timedelta code that represents the difference between time points; default is 'D' (daily)    
#     file_colnames: (list) the list of shorthand variables; default is None
#     subset_start_date: (date) the start date of a date range of interest
#     subset_end_date: (date) the end date of a date range of interest
#     """
#     # start time
#     starttime = pd.datetime.now()
    
#     # date range from ogh_meta file
#     met_daily_dates=pd.date_range(file_start_date, file_end_date, freq=file_time_step)
#     met_daily_subdates=pd.date_range(subset_start_date, subset_end_date, freq=file_time_step)
    
#     # omit null entries or missing data file
#     map_df = map_df.loc[pd.notnull(map_df[dataset]),:]
#     print('Number of data files within elevation range ('+str(min_elev)+':'+str(max_elev)+'): '+str(len(map_df)))
    
#     # iterate through each data file
#     for eachvar in metadata[dataset]['variable_list']:
        
#         # exclude YEAR, MONTH, and DAY
#         if eachvar not in ['YEAR','MONTH','DAY']:

#             # identify the variable column index
#             usecols = [metadata[dataset]['variable_list'].index(eachvar)]

#             # initiate df as a list
#             df_list=[]

#             # loop through each file
#             for ind, row in map_df.iterrows():

#                 # consider rewriting the params to just select one column by index at a time
#                 var_series = dask.delayed(pd.read_table)(filepath_or_buffer=row[dataset],
#                                                          delimiter=file_delimiter,header=None,usecols=usecols,
#                                                          names=[tuple(row[['FID','LAT','LONG_']])])

#                 # append the series into the list of series
#                 df_list.append(var_series)

#             # concatenate list of series (axis=1 is column-wise) into a dataframe
#             df1 = dask.delayed(pd.concat)(df_list, axis=1)

#             # set and subset date_range index
#             df2 = df1.set_index(met_daily_dates, inplace=False).loc[met_daily_subdates]

#             # end of variable table
#             print(eachvar+ ' dataframe reading to start: ' + str(pd.datetime.now()-starttime))

#             # assign dataframe to dictionary object
#             df_dict['_'.join([eachvar, gridclimname])] = dask.compute(df2)[0]
#             print(eachvar+ ' dataframe reading complete:' + str(pd.datetime.now()-starttime))

#     return(df_dict)


# def read_daily_streamflow(file_name, drainage_area_m2, file_colnames=None, delimiter='\t', header='infer'):
#     # read in a daily streamflow data set    
    
#     # if file_colnames are supplied, use header=None
#     if file_colnames is not None:
#         header=None
    
#     # read in the data
#     daily_data=pd.read_table(file_name, delimiter=delimiter, header=header) 
    
#     # set columns, if header=None
#     if file_colnames is not None:
#         daily_data.columns=file_colnames
#     else:
#         file_colnames=list(daily_data.columns)
        
#     # calculate cfs to cms conversion, or vice versa
#     if 'flow_cfs' in daily_data.columns:
#         flow_cfs=daily_data['flow_cfs']
#         flow_cms=flow_cfs/(3.28084**3)
#         flow_mmday=flow_cms*1000*3600*24/drainage_area_m2 
#     elif 'flow_cms' in daily_data.columns:
#         flow_cms=daily_data['flow_cms']
#         flow_cfs=flow_cms*(3.28084**3)
#         flow_mmday=flow_cms*1000*3600*24/drainage_area_m2
            
#     # determine the datetime
#     date_index=[file_colnames.index(each) for each in ['year','month','day']]
#     row_dates=pd.to_datetime(daily_data[date_index])
    
#     # generate the daily_flow and set the datetime as row indices
#     daily_flow=pd.concat([flow_cfs, flow_cms, flow_mmday],axis=1)
#     daily_flow.set_index(row_dates, inplace=True)
#     daily_flow.columns=['flow_cfs', 'flow_cms', 'flow_mmday']
#     return(daily_flow)


# def read_daily_precip(file_name, file_colnames=None, header='infer', delimiter='\s+'):
#     # read in a daily precipitation data set
    
#     # if file_colnames are supplied, use header=None
#     if ps.notnull(file_colnames):
#         header=None
    
#     # read in the data
#     daily_data=pd.read_table(file_name, delimiter=delimiter, header=header) 
    
#     # set columns, if header=None
#     if pd.notnull(file_colnames):
#         daily_data.columns=file_colnames
#     else:
#         file_colnames=list(daily_data.columns)
    
#     # calculate cfs to cms conversion, or vice versa
#     if 'precip_m' in daily_data.columns:
#         precip_m=daily_data['precip_m']
#         precip_mm=precip_m*1000
    
#     # determine the datetime
#     date_index=[file_colnames.index(each) for each in ['year','month','day']]
#     row_dates=pd.to_datetime(daily_data[date_index])
    
#     # generate the daily_flow and set the datetime as row indices
#     daily_precip=pd.concat([precip_m, precip_mm],axis=1)
#     daily_precip.set_index(row_dates, inplace=True)
#     daily_precip.columns=['precip_m', 'precip_mm']
#     return(daily_precip)


# def read_daily_snotel(file_name, file_colnames=None, usecols=None, delimiter=',', header='infer'):
#     # read in a daily SNOTEL observation data set
    
#     # if file_colnames are supplied, use header=None
#     if file_colnames is not None:
#         header=None
    
#     # read in the data
#     daily_data=pd.read_table(file_name, usecols=usecols, header=header, delimiter=delimiter)
    
#     # reset the colnames
#     daily_data.columns=['Date', 'Tmax_C', 'Tmin_C', 'Tavg_C', 'Precip_mm']
    
#     # transform the data
#     daily_data['Tmax_C']=(daily_data['Tmax_C'] -32)/1.8
#     daily_data['Tmin_C']=(daily_data['Tmin_C'] -32)/1.8
#     daily_data['Tavg_C']=(daily_data['Tavg_C'] -32)/1.8
#     daily_data['Precip_mm']=daily_data['Precip_mm'] *25.4
    
#     # determine the datetime
#     row_dates=pd.to_datetime(daily_data.Date)
    
#     # generate the daily_flow and set the datetime as row indices
#     daily_snotel=daily_data[['Tmax_C', 'Tmin_C', 'Tavg_C', 'Precip_mm']]
#     daily_snotel.set_index(row_dates, inplace=True)
#     return(daily_snotel)


# def read_daily_coop(file_name, file_colnames=None, usecols=None, delimiter=',', header='infer'):
#     # read in a daily COOP observation data set
    
#     # if file_colnames are supplied, use header=None
#     if file_colnames is not None:
#         header=None
    
#     # read in the data
#     daily_data=pd.read_table(file_name, usecols=usecols, header=header, delimiter=delimiter, 
#                              date_parser=lambda x: pd.datetime.strptime(x, '%Y%m%d'), 
#                              parse_dates=[0], 
#                              na_values=-9999)
    
#     # reset the colnames
#     daily_data.columns=['Date', 'Precip_mm','Tmax_C', 'Tmin_C', 'Tavg_C']
    
#     # transform the data
#     daily_data['Tmax_C']=(daily_data['Tmax_C'] -32)/1.8
#     daily_data['Tmin_C']=(daily_data['Tmin_C'] -32)/1.8
#     daily_data['Tavg_C']=(daily_data['Tavg_C'] -32)/1.8
#     daily_data['Precip_mm']=daily_data['Precip_mm'] *25.4
    
#     # determine the datetime
#     row_dates=pd.to_datetime(daily_data.Date)
    
#     # generate the daily_flow and set the datetime as row indices
#     daily_coop=daily_data[['Precip_mm','Tmax_C', 'Tmin_C', 'Tavg_C']]
#     daily_coop.set_index(row_dates, inplace=True)
#     return(daily_coop)

# # ### Data Processing functions

# def generateVarTables(file_dict, gridclimname, dataset, metadata, df_dict=None):
#     """
#     Slice the files by their common variable
    
#     all_files: (dict) a dictionary of dataframes for each tabular datafile
#     dataset: (str) the name of the dataset
#     metadata (dict) the dictionary that contains the metadata explanations; default is None
#     """
#     # combine the files into a pandas panel
#     panel = pd.Panel.from_dict(file_dict)

#     # initiate output dictionary
#     if pd.isnull(df_dict):
#         df_dict = dict()
    
#     # slice the panel for each variable in list
#     for eachvar in metadata[dataset]['variable_list']:
#         df_dict['_'.join([eachvar, gridclimname])] = panel.xs(key=eachvar, axis=2)
        
#     return(df_dict)


# # compare two date sets for the start and end of the overlapping dates
# def overlappingDates(date_set1, date_set2):
#     # find recent date
#     if date_set1[0] > date_set2[0]:
#         start_date = date_set1[0]
#     else:
#         start_date = date_set2[0]
    
#     # find older date
#     if date_set1[-1] < date_set2[-1]:
#         end_date = date_set1[-1]
#     else:
#         end_date = date_set2[-1]
#     return(start_date, end_date)


# # Calculate means by 8 different methods
# def multigroupMeans(VarTable, n_stations, start_date, end_date):
#     Var_daily = VarTable.loc[start_date:end_date, range(0,n_stations)]
    
#     # e.g., Mean monthly temperature at each station
#     month_daily=Var_daily.groupby(Var_daily.index.month).mean() # average monthly minimum temperature at each station
    
#     # e.g., Mean monthly temperature averaged for all stations in analysis
#     meanmonth_daily=month_daily.mean(axis=1)
    
#     # e.g., Mean monthly temperature for minimum and maximum elevation stations
#     meanmonth_min_maxelev_daily=Var_daily.loc[:,analysis_elev_max_station].groupby(Var_daily.index.month).mean()
#     meanmonth_min_minelev_daily=Var_daily.loc[:,analysis_elev_min_station].groupby(Var_daily.index.month).mean()
    
#     # e.g., Mean annual temperature
#     year_daily=Var_daily.groupby(Var_daily.index.year).mean()
    
#     # e.g., mean annual temperature each year for all stations
#     meanyear_daily=year_daily.mean(axis=1)
    
#     # e.g., mean annual min temperature for all years, for all stations
#     meanallyear_daily=np.nanmean(meanyear_daily)
    
#     # e.g., anomoly per year compared to average
#     anom_year_daily=meanyear_daily-meanallyear_daily
    
#     return(month_daily, 
#            meanmonth_daily, 
#            meanmonth_min_maxelev_daily, 
#            meanmonth_min_minelev_daily, 
#            year_daily, 
#            meanyear_daily, 
#            meanallyear_daily,
#            anom_year_daily)


# def specialTavgMeans(VarTable):
#     Var_daily = VarTable.loc[start_date:end_date, range(0,n_stations)]
    
#     # Average temperature for each month at each station
#     permonth_daily=Var_daily.groupby(pd.TimeGrouper("M")).mean()
    
#     # Average temperature each month averaged at all stations
#     meanpermonth_daily=permonth_daily.mean(axis=1)
    
#     # Average monthly temperature for all stations
#     meanallpermonth_daily=meanpermonth_daily.mean(axis=0)
    
#     # anomoly per year compared to average
#     anom_month_daily=(meanpermonth_daily-meanallpermonth_daily)/1000
    
#     return(permonth_daily,
#           meanpermonth_daily,
#           meanallpermonth_daily,
#           anom_month_daily)


# def aggregate_space_time_average(df_dict, suffix, start_date, end_date):
#     """
#     VarTable: (dataframe) a dataframe with date ranges as the index
#     df_dict: (dict) a dictionary to which computed outputs will be stored
#     suffix: (str) a string representing the name of the original table
#     start_date: (date) the start of the date range within the original table
#     end_date: (date) the end of the date range within the original table
#     """
#     starttime = pd.datetime.now()
    
#     # subset dataframe to the date range of interest
#     Var_daily=df_dict[suffix].loc[start_date:end_date,:]
    
#     # Mean daily value averaged for all stations in analysis
#     df_dict['meandaily_'+suffix]=Var_daily.mean(axis=1) 
    
#     # Mean monthly value at each station
#     df_dict['month_'+suffix]=Var_daily.groupby(Var_daily.index.month).mean() 
    
#     # Mean monthly value averaged for all stations in analysis
#     df_dict['meanmonth_'+suffix]=Var_daily.groupby(Var_daily.index.month).mean().mean(axis=1)

#     # Mean annual value
#     df_dict['year_'+suffix]=Var_daily.groupby(Var_daily.index.year).mean()
    
#     # mean annual value for each year for all stations in analysis
#     df_dict['meanyear_'+suffix]=Var_daily.groupby(Var_daily.index.year).mean().mean(axis=1)
    
#     # global mean value for all daily values and for all stations in analysis
#     df_dict['meanallyear_'+suffix]=Var_daily.mean(axis=1).mean(axis=0)
    
#     # annual anomaly compared to the global mean value
#     df_dict['anom_year_'+suffix]=df_dict['meanyear_'+suffix]-df_dict['meanallyear_'+suffix]
    
#     print(suffix+ ' calculations completed in ' + str(pd.datetime.now()-starttime))
#     return(df_dict)


# def aggregate_space_time_sum(df_dict, suffix, start_date, end_date):
#     # subset dataframe to the date range of interest
#     Var_daily = df_dict[suffix].loc[start_date:end_date,:]

#     # mean daily sum across all stations then averaged across all days in analysis
#     df_dict['meandailysum_'+suffix]=Var_daily.groupby(pd.TimeGrouper('D')).sum().mean(axis=1)
    
#     # monthly sums for each station and for each month in analysis
#     monthsum_df=Var_daily.groupby(pd.TimeGrouper('M')).sum()
#     df_dict['monthsum_'+suffix]=monthsum_df
    
#     # mean monthly sum averaged for each stations for each month in analysis
#     df_dict['meanbymonthsum_'+suffix]=monthsum_df.groupby(monthsum_df.index.month).mean()
    
#     # mean monthly sum averaged across all stations for each month in analysis
#     df_dict['meanmonthsum_'+suffix]=monthsum_df.mean(axis=1)
    
#     # mean monthly sum averaged across all stations and all months in analysis
#     df_dict['meanallmonthsum_'+suffix]=monthsum_df.mean(axis=1).mean()
    
#     # annual sum for each station and for each year in analysis
#     yearsum_df=Var_daily.groupby(Var_daily.index.year).sum()
#     df_dict['yearsum_'+suffix]=yearsum_df
    
#     # mean annual sum averaged for each stations across year in analysis
#     df_dict['meanbyyearsum_'+suffix]=pd.DataFrame(yearsum_df.mean()).T
    
#     # mean annual sum averaged across all stations for each year in analysis
#     df_dict['meanyearsum_'+suffix]=yearsum_df.mean(axis=1)
    
#     # mean annual sum averaged across all stations and all years in analysis
#     df_dict['meanallyearsum_'+suffix]=yearsum_df.mean(axis=1).mean()
    
#     return(df_dict)


# def gridclim_dict(mappingfile,dataset,gridclimname=None,metadata=None,min_elev=None,max_elev=None,
#                   file_start_date=None,file_end_date=None,file_time_step=None,file_colnames=None,file_delimiter=None,
#                   subset_start_date=None,subset_end_date=None,df_dict=None,colvar=None):
#     """
#     # pipelined operation for assimilating data, processing it, and standardizing the plotting
    
#     mappingfile: (dir) the path directory to the mappingfile
#     dataset: (str) the name of the dataset within mappingfile to use
#     gridclimname: (str) the suffix for the dataset to be named; if None is provided, default to the dataset name
#     metadata: (str) the dictionary that contains the metadata explanations; default is None
#     min_elev: (float) the minimum elevation criteria; default is None
#     max_elev: (float) the maximum elevation criteria; default is None
#     file_start_date: (date) the start date of the files that will be read-in; default is None
#     file_end_date: (date) the end date for the files that will be read in; default is None
#     file_time_step: (str) the timedelta code that represents the difference between time points; default is 'D' (daily)    
#     file_colnames: (list) the list of shorthand variables; default is None
#     file_delimiter: (str) a file parsing character to be used for file reading
#     subset_start_date: (date) the start date of a date range of interest
#     subset_end_date: (date) the end date of a date range of interest
#     df_dict: (dict) an existing dictionary where new computations will be stored
#     """
    
#     # generate the climate locations and n_stations
#     locations_df, n_stations = mappingfileToDF(mappingfile, colvar=colvar, summary=False)
    
#     # generate the climate station info
#     if pd.isnull(min_elev):
#         min_elev = locations_df.ELEV.min()
    
#     if pd.isnull(max_elev):
#         max_elev = locations_df.ELEV.max()
    
#     # extract metadata if the information are not provided
#     if not isinstance(metadata, type(None)):
        
#         if isinstance(file_start_date, type(None)):
#             file_start_date = metadata[dataset]['start_date']
        
#         if isinstance(file_end_date, type(None)):
#             file_end_date = metadata[dataset]['end_date']

#         if isinstance(file_time_step, type(None)):
#             file_time_step = metadata[dataset]['temporal_resolution']

#         if isinstance(file_colnames, type(None)):
#             file_colnames = metadata[dataset]['variable_list']
        
#         if isinstance(file_delimiter, type(None)):
#             file_delimiter = metadata[dataset]['delimiter']
        
#     # take all defaults if subset references are null
#     if pd.isnull(subset_start_date):
#         subset_start_date = file_start_date
    
#     if pd.isnull(subset_end_date):
#         subset_end_date = file_end_date
        
#     # initiate output dictionary df_dict was null
#     if pd.isnull(df_dict):
#         df_dict = dict()
        
#     if pd.isnull(gridclimname):
#         if pd.notnull(dataset):
#             gridclimname=dataset
#         else:
#             print('no suffix name provided. Provide a gridclimname or dataset label.')
#             return
    
#     # assemble the stations within min and max elevantion ranges
#     locations_df = locations_df[(locations_df.ELEV >= min_elev) & (locations_df.ELEV <= max_elev)]
    
#     # create dictionary of dataframe
#     df_dict = read_files_to_vardf(map_df=locations_df,
#                                   dataset=dataset, 
#                                   metadata=metadata, 
#                                   gridclimname=gridclimname,
#                                   file_start_date=file_start_date, 
#                                   file_end_date=file_end_date, 
#                                   file_delimiter=file_delimiter, 
#                                   file_time_step=file_time_step, 
#                                   file_colnames=file_colnames, 
#                                   subset_start_date=subset_start_date, 
#                                   subset_end_date=subset_end_date,
#                                   min_elev=min_elev, 
#                                   max_elev=max_elev,
#                                   df_dict=df_dict)

#     vardf_list = [eachvardf for eachvardf in df_dict.keys() if eachvardf.endswith(gridclimname)]
#     # loop through the dictionary to compute each aggregate_space_time_average object
#     for eachvardf in vardf_list:

#         # update the dictionary with spatial and temporal average computations
#         df_dict.update(aggregate_space_time_average(df_dict=df_dict,suffix=eachvardf,
#                                                     start_date=subset_start_date,end_date=subset_end_date))

#         # if the number of stations exceeds 500, remove daily time-series dataframe
#         if len(locations_df)>300:
#            del df_dict[eachvardf]
                
#     return(df_dict)


# def compute_diffs(df_dict, df_str, gridclimname1, gridclimname2, prefix1, prefix2='meanmonth', comp_dict=None):
#     #Compute difference between monthly means for some data (e.g,. Temp) for two different gridded datasets (e.g., Liv, WRF)
    
#     if isinstance(comp_dict, type(None)):
#         comp_dict=dict()
        
#     for each1 in prefix1:
#         for each2 in prefix2:
#             diffs = df_dict['_'.join([each2,each1,gridclimname1])]-df_dict['_'.join([each2,each1,gridclimname2])]
#             comp_dict['_'.join([str(each1),df_str])] = diffs
#     return(comp_dict)


# def compute_ratios(df_dict, df_str, gridclimname1, gridclimname2, prefix1, prefix2='meanmonth', comp_dict=None):
#     #Compute difference between monthly means for some data (e.g,. Temp) for two different gridded datasets (e.g., Liv, WRF)
    
#     if isinstance(comp_dict, type(None)):
#         comp_dict=dict()
    
#     for each1 in prefix1:
#         for each2 in prefix2:
#             ratios = df_dict['_'.join([each2,each1,gridclimname1])]/df_dict['_'.join([each2,each1,gridclimname2])]
#             comp_dict['_'.join([str(each1),df_str])] = ratios
#     return(comp_dict)


# def compute_elev_diffs(df_dict, df_str, gridclimname1, prefix1, prefix2a='meanmonth_minelev_', prefix2b='meanmonth_maxelev_'):
#     comp_dict=dict()
#     for each1 in prefix1:
#         comp_dict[str(each1)+df_str] = df_dict[prefix2a+each1+gridclimname1]-df_dict[prefix2b+each1+gridclimname1]
#     return(comp_dict)


# def monthlyBiasCorrection_deltaTratioP_Livneh_METinput(homedir, mappingfile, BiasCorr,
#                                                  lowrange='0to1000m', LowElev=range(0,1000),
#                                                  midrange='1000to1500m', MidElev=range(1001,1501),
#                                                  highrange='1500to3000m', HighElev=range(1501,3000),
#                                                  data_dir=None, file_start_date=None, file_end_date=None):

#     np.set_printoptions(precision=3)
    
#     # take liv2013 date set date range as default if file reference dates are not given
#     if isinstance(file_start_date, type(None)):
#         file_start_date = pd.datetime(1915,1,1)
        
#     if isinstance(file_end_date, type(None)):
#         file_end_date = pd.datetime(2011,12,31)
    
#     # generate the month vector
#     month = pd.date_range(start=file_start_date, end=file_end_date).month
#     month = pd.DataFrame({'month':month})
    
#     # create NEW directory
#     dest_dir = os.path.join(homedir, 'biascorrWRF_liv')
#     if not os.path.exists(dest_dir):
#         os.mkdir(dest_dir)
#         print('destdir created')
    
#     # read in the Elevation table
#     zdiff = pd.read_table(mappingfile, sep=',', header='infer')
#     zdiff = zdiff.rename(columns={'RASTERVALU':'Elev','ELEV':'Elev'})
#     zdiff = zdiff[['LAT','LONG_', 'Elev']]
#     zdiff['filename'] = zdiff[['LAT','LONG_']].apply(lambda x: '_'.join(['Meteorology_Livneh_CONUSExt_v.1.2_2013',str(x[0]), str(x[1])]), axis=1)
#     #print(zdiff[0:10])

#     # lapse rate vector by month
#     # temperature adjustment vector by month

#     # identify the files to read
#     print('reading in data_long_lat files')
#     data_files = [os.path.join(data_dir,dat) for dat in os.listdir(data_dir) 
#                   if os.path.basename(dat).startswith('Meteorology_Livneh_CONUSExt_v.1.2_2013')]
#     print('done reading data_long_lat files')
    
#     # loop through each file
#     for eachfile in data_files:
        
#         # subset the zdiff table using the eachfile's filename, then assign Elevation to equal the Elev value
#         Elevation = zdiff[zdiff['filename']==os.path.basename(eachfile)]['Elev'].reset_index(drop=True)
#         print(Elevation)
                
#         # decide on the elevation-based Tcorr
#         #print('Convert BiasCorr to a df')
#         if Elevation.iloc[0] in LowElev:
#             BiasCorr_sub = {k: v for k, v in BiasCorr.items() if k.endswith('_'+lowrange)}
#             #BiasCorr_sub_df = pd.DataFrame.from_dict(BiasCorr_sub, orient='columns').reset_index()
#             #BiasCorr_sub_df.columns = ['month', 'precip', 'Tmax', 'Tmin']
            
#         elif Elevation.iloc[0] in MidElev:
#             BiasCorr_sub = {k: v for k, v in BiasCorr.items() if k.endswith('_'+midrange)}
#             #BiasCorr_sub_df = pd.DataFrame.from_dict(BiasCorr_sub, orient='columns').reset_index()
#             #BiasCorr_sub_df.columns = ['month', 'precip', 'Tmax', 'Tmin']
        
#         elif Elevation.iloc[0] in HighElev:
#             BiasCorr_sub = {k: v for k, v in BiasCorr.items() if k.endswith('_'+highrange)}
#             #BiasCorr_sub_df = pd.DataFrame.from_dict(BiasCorr_sub, orient='columns').reset_index()
#             #BiasCorr_sub_df.columns = ['month', 'precip', 'Tmax', 'Tmin']
       
#         #print('reading in eachfile')
#         read_dat = pd.read_table(eachfile, delimiter='\s+', header=None)
#         read_dat.columns = ['precip', 'temp_max','temp_min','wind']
#         # print('done reading eachfile')

#         # extrapolate monthly values for each variable
#         for eachvar in ['precip', 'temp_max', 'temp_min']:
#             BiasCorr_sub_df = [BiasCorr_sub[eachkey] for eachkey in BiasCorr_sub.keys() if eachkey.startswith(eachvar)]
            
#             # subset the column for the eachfile station number
#             BiasCorr_sub_df = BiasCorr_sub_df.loc[:,zdiff[zdiff['filename']==eachfile].index]
#             BiasCorr_sub_df.columns = ['var']
            
#             # regenerate the month
#             BiasCorr_sub_df = BiasCorr_sub_df.reset_index().rename(columns={'index':'month'})
            
#             # generate s-vectors
#             month_obj = month.merge(BiasCorr_sub_df, how='left', on='month')
            
#             # generate the s-vector
#             s = pd.Series(month_obj.var)
            
#             #
#             if eachvar=='precip':
#                 read_dat[eachvar] = np.array(read_dat[eachvar])*np.array(s)
#             else:
#                 read_dat[eachvar] = np.array(read_dat[eachvar])+np.array(s)    
        
#         #print('grabbing the S vector of monthlapse after the merge between month and Tcorr_df')
#         #print('number of corrections to apply: '+str(len(month)))
        
#         # write it out to the new destination location
#         read_dat.to_csv(os.path.join(dest_dir, os.path.basename(eachfile)), sep='\t', header=None, index=False)
#         print(os.path.join(dest_dir, os.path.basename(eachfile)))
    
#     print('mission complete.')
#     print('this device will now self-destruct.')
#     print('just kidding.')


# def monthlyBiasCorrection_WRFlongtermmean_elevationbins_METinput(homedir, mappingfile, BiasCorr,
#                                                  lowrange='0to1000m', LowElev=range(0,1000),
#                                                  midrange='1000to1500m', MidElev=range(1001,1501),
#                                                  highrange='1500to3000m', HighElev=range(1501,3000),
#                                                  data_dir=None,
#                                                  file_start_date=None,
#                                                  file_end_date=None):

#     np.set_printoptions(precision=3)
    
#     # take liv2013 date set date range as default if file reference dates are not given
#     if isinstance(file_start_date, type(None)):
#         file_start_date = pd.datetime(1950,1,1)
        
#     if isinstance(file_end_date, type(None)):
#         file_end_date = pd.datetime(2010,12,31)
    
#     # generate the month vector
#     month = pd.date_range(start=file_start_date, end=file_end_date).month
#     month = pd.DataFrame({'month':month})
    
#     # create NEW directory
#     dest_dir = os.path.join(homedir, 'biascorr_WRF_ltm')
#     if not os.path.exists(dest_dir):
#         os.mkdir(dest_dir)
#         print('destdir created')
    
#     # read in the Elevation table
#     zdiff = pd.read_table(mappingfile, sep=',', header='infer')
#     zdiff = zdiff.rename(columns={'RASTERVALU':'Elev','ELEV':'Elev'})
#     zdiff = zdiff[['LAT','LONG_', 'Elev']]
#     zdiff['filename'] = zdiff[['LAT','LONG_']].apply(lambda x: '_'.join(['data',str(x[0]), str(x[1])]), axis=1)
#     #print(zdiff[0:10])

#     # lapse rate vector by month
#     # temperature adjustment vector by month

#     # identify the files to read
#     print('reading in data_long_lat files')
#     data_files = [os.path.join(data_dir,dat) for dat in os.listdir(data_dir) if os.path.basename(dat).startswith('data')]
#     #print('done reading data_long_lat files')
    
#     # loop through each file
#     for eachfile in data_files:
        
#         # subset the zdiff table using the eachfile's filename, then assign Elevation to equal the Elev value
#         Elevation = zdiff[zdiff['filename']==os.path.basename(eachfile)]['Elev'].reset_index(drop=True)
#         print(Elevation)
                
#         # decide on the elevation-based Tcorr
#         #print('Convert BiasCorr to a df')
#         if Elevation.iloc[0] in LowElev:
#             BiasCorr_sub = {k: v for k, v in BiasCorr.items() if k.endswith('_'+lowrange)}
#             BiasCorr_sub_df = pd.DataFrame.from_dict(BiasCorr_sub, orient='columns').reset_index()
#             BiasCorr_sub_df.columns = ['month', 'precip', 'Tmax', 'Tmin']
            
#         elif Elevation.iloc[0] in MidElev:
#             BiasCorr_sub = {k: v for k, v in BiasCorr.items() if k.endswith('_'+midrange)}
#             BiasCorr_sub_df = pd.DataFrame.from_dict(BiasCorr_sub, orient='columns').reset_index()
#             BiasCorr_sub_df.columns = ['month', 'precip', 'Tmax', 'Tmin']
        
#         elif Elevation.iloc[0] in HighElev:
#             BiasCorr_sub = {k: v for k, v in BiasCorr.items() if k.endswith('_'+highrange)}
#             BiasCorr_sub_df = pd.DataFrame.from_dict(BiasCorr_sub, orient='columns').reset_index()
#             BiasCorr_sub_df.columns = ['month', 'precip', 'Tmax', 'Tmin']
       
#         print('reading in eachfile')
#         read_dat = pd.read_table(eachfile, delimiter='\s+', header=None)
#         read_dat.columns = ['precip', 'Tmax','Tmin','wind']
#         print('done reading eachfile')

#         # extrapolate monthly values
#         month_obj = month.merge(BiasCorr_sub_df, how='left', on='month')
#         #print('merged month with Tcorr_df')
#         #print(month_obj.head(35))
        
#         # generate s-vectors
#         s1 = pd.Series(month_obj.Tmin)
#         s2 = pd.Series(month_obj.Tmax)
#         s3 = pd.Series(month_obj.precip)
        
#         read_dat['Tmin'] = np.array(read_dat.Tmin)+np.array(s1)
#         read_dat['Tmax'] = np.array(read_dat.Tmax)+np.array(s2)
#         read_dat['precip'] = np.array(read_dat.precip)*np.array(s3)
        
#         # write it out to the new destination location
#         read_dat.to_csv(os.path.join(dest_dir, os.path.basename(eachfile)), sep='\t', header=None, index=False)
#         print(os.path.join(dest_dir, os.path.basename(eachfile)))
    
#     print('mission complete.')
#     print('this device will now self-destruct.')
#     print('just kidding.')


# def switchUpVICSoil(input_file=None,
#                     output_file='soil',
#                     mappingfile=None,
#                     homedir=None):
#     #Read in table of VIC soil inputs -- assumes all Lat/Long set to zero
#     soil_base = pd.read_table(input_file,header=None)

#     #Make a list of all lat/long values
#     latlong=soil_base.apply(lambda x:tuple([x[2],x[3]]), axis=1)

#     #Read in mappingfile from TreatGeoSelf()
#     maptable = pd.read_table(mappingfile,sep=",")

#     #Make a list Lat/Long files that need to switched up 
#     latlong_1=maptable.apply(lambda x:tuple([x['LAT'],x['LONG_']]), axis=1)

#     #Switch up from 0 to 1 so VIC will run for this Lat/Long point - print new output file (VIC model input file)
#     soil_base[0] = latlong.apply(lambda x: 1 if x in set(latlong_1) else 0)        
#     soil_base.to_csv(output_file, header=False, index=False, sep="\t")
#     print(str(soil_base[0].sum()) +' VIC grid cells have successfully been switched up.') 
#     print('Check your home directory for your new VIC soil model input set to your list of Lat/Long grid centroids.')
    

# def makebelieve(homedir, mappingfile, BiasCorr, metadata, start_catalog_label, end_catalog_label, 
#                 file_start_date=None, file_end_date=None,
#                 data_dir=None, dest_dir_suffix=None):
#     np.set_printoptions(precision=6)

#     # take liv2013 date set date range as default if file reference dates are not given
#     if isinstance(file_start_date, type(None)):
#         file_start_date = metadata[start_catalog_label]['start_date']
        
#     if isinstance(file_end_date, type(None)):
#         file_end_date = metadata[start_catalog_label]['end_date']

#     # generate the month vector
#     month = pd.date_range(start=file_start_date, end=file_end_date).month
#     month = pd.DataFrame({'month':month})

#     # create NEW directory
#     if isinstance(dest_dir_suffix, type(None)):
#         dest_dir_suffix = 'biascorr_output/'

#     dest_dir = os.path.join(homedir, dest_dir_suffix)
#     if not os.path.exists(dest_dir):
#         os.mkdir(dest_dir)
#         print('destdir created')

#     # read in the mappingfile
#     map_df, nstations = mappingfileToDF(mappingfile, colvar='all', summary=False)

#     # compile the BiasCorr dictionary into a pandas panel
#     BiasCorr=pd.Panel.from_dict(BiasCorr)

#     # loop through each file
#     for ind, eachfile in enumerate(map_df.loc[:,start_catalog_label]):
        
#         # identify the file
#         station = map_df.loc[map_df.loc[:,start_catalog_label]==eachfile,['FID', 'LAT', 'LONG_']].reset_index(drop=True)

#         # subset the bias correction to the file at hand
#         print(str(ind)+' station: '+str(tuple(station.loc[0,:])))
#         BiasCorr_df = BiasCorr.xs(key=tuple(station.loc[0,:]),axis=2)
                
#         # read in the file to be corrected
#         read_dat = pd.read_table(eachfile, delimiter=metadata[start_catalog_label]['delimiter'],
#                                  header=None, names=metadata[start_catalog_label]['variable_list'])
        
#         # extrapolate monthly values for each variable
#         for eachvar in read_dat.columns:
                        
#             # identify the corresponding bias correction key
#             for eachkey in BiasCorr_df.columns:
#                 if eachkey.startswith(eachvar):
                                
#                     # subset the dataframe to the variable in loop
#                     BiasCorr_subdf = BiasCorr_df.loc[:,eachkey]

#                     # regenerate row index as month column
#                     BiasCorr_subdf = BiasCorr_subdf.reset_index().rename(columns={'index':'month'})

#                     # generate the s-vector
#                     s = month.merge(BiasCorr_subdf, how='left', on='month').loc[:,eachkey]

#                     if eachvar=='PRECIP':
#                         #Use for ratio precip method
#                         read_dat[eachvar] = np.multiply(np.array(read_dat.loc[:,eachvar]), np.array(s))

#                         #read_dat[eachvar] = np.array(read_dat.loc[:,eachvar])+np.array(s)
#                         #positiveprecip=read_dat[eachvar]
#                         #positiveprecip[positiveprecip<0.]=0.
#                         #read_dat[eachvar] = positiveprecip*.9842
#                     else:
#                         read_dat[eachvar] = np.array(read_dat.loc[:,eachvar])+np.array(s)

#         # write it out to the new destination location
#         filedest = os.path.join(dest_dir, os.path.basename(eachfile))
#         read_dat.to_csv(filedest, sep='\t', header=None, index=False, float_format='%.4f')

#     # update the mappingfile with the file catalog
#     addCatalogToMap(outfilepath=mappingfile, maptable=map_df, folderpath=dest_dir, catalog_label=end_catalog_label)

#     # append the source metadata to the new catalog label metadata
#     metadata[end_catalog_label] = metadata[start_catalog_label]
    
#     # update the metadata json file
#     json.dump(metadata, open('ogh_meta.json', 'w'), ensure_ascii=False)
    
#     print('mission complete. this device will now self-destruct. just kidding.')
#     return(dest_dir, metadata)


# def plot_meanP(dictionary, loc_name, start_date, end_date):
#     # Plot 1: Monthly temperature analysis of Livneh data
#     if 'meanmonth_precip_liv2013_met_daily' and 'meanmonth_precip_wrf2014_met_daily' not in dictionary.keys():
#         pass

#     # generate month indices
#     wy_index=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
#     wy_numbers=[10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9]
#     month_strings=[ 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sept']
    
#     # initiate the plot object
#     fig, ax=plt.subplots(1,1,figsize=(10, 6))

#     if 'meanmonth_precip_liv2013_met_daily' in dictionary.keys():
#         # Liv2013

#         plt.plot(wy_index, dictionary['meanmonth_precip_liv2013_met_daily'][wy_numbers],'r-', linewidth=1, label='Liv Precip')  
    
#     if 'meanmonth_precip_wrf2014_met_daily' in dictionary.keys():
#         # WRF2014
#         plt.plot(wy_index, dictionary['meanmonth_precip_wrf2014_met_daily'][wy_numbers],'b-',linewidth=1, label='WRF Precip')
 
#     if 'meanmonth_precip_livneh2013_wrf2014bc_met_daily' in dictionary.keys():
#         # WRF2014
#         plt.plot(wy_index, dictionary['meanmonth_precip_livneh2013_wrf2014bc_met_daily'][wy_numbers],'g-',linewidth=1, label='WRFbc Precip')
 
#     # add reference line at y=0
#     plt.plot([1, 12],[0, 0], 'k-',linewidth=1)

#     plt.ylabel('Precip (mm)',fontsize=14)
#     plt.xlabel('Month',fontsize=14)
#     plt.xlim(1,12);
#     plt.xticks(wy_index, month_strings);
        
#     plt.tick_params(labelsize=12)
#     plt.legend(loc='best')
#     plt.grid(which='both')
#     plt.title(str(loc_name)+'\nAverage Precipitation\n Years: '+str(start_date.year)+'-'+str(end_date.year)+'; Elevation: '+str(dictionary['analysis_elev_min'])+'-'+str(dictionary['analysis_elev_max'])+'m', fontsize=16)
#     plt.savefig('monthly_precip'+str(loc_name)+'.png')
#     plt.show()
    
    
# def plot_meanTavg(dictionary, loc_name, start_date, end_date):
#     # Plot 1: Monthly temperature analysis of Livneh data
#     if 'meanmonth_temp_avg_liv2013_met_daily' and 'meanmonth_temp_avg_wrf2014_met_daily' not in dictionary.keys():
#         pass

#     # generate month indices
#     wy_index=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
#     wy_numbers=[10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9]
#     month_strings=[ 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sept']
    
#     # initiate the plot object
#     fig, ax=plt.subplots(1,1,figsize=(10, 6))

#     if 'meanmonth_temp_avg_liv2013_met_daily' in dictionary.keys():
#         # Liv2013

#         plt.plot(wy_index, dictionary['meanmonth_temp_avg_liv2013_met_daily'][wy_numbers],'r-', linewidth=1, label='Liv Temp Avg')  
    
#     if 'meanmonth_temp_avg_wrf2014_met_daily' in dictionary.keys():
#         # WRF2014
#         plt.plot(wy_index, dictionary['meanmonth_temp_avg_wrf2014_met_daily'][wy_numbers],'b-',linewidth=1, label='WRF Temp Avg')
 
#     if 'meanmonth_temp_avg_livneh2013_wrf2014bc_met_daily' in dictionary.keys():
#         # WRF2014
#         plt.plot(wy_index, dictionary['meanmonth_temp_avg_livneh2013_wrf2014bc_met_daily'][wy_numbers],'g-',linewidth=1, label='WRFbc Temp Avg')
 
#     # add reference line at y=0
#     plt.plot([1, 12],[0, 0], 'k-',linewidth=1)

#     plt.ylabel('Temp (C)',fontsize=14)
#     plt.xlabel('Month',fontsize=14)
#     plt.xlim(1,12);
#     plt.xticks(wy_index, month_strings);
        
#     plt.tick_params(labelsize=12)
#     plt.legend(loc='best')
#     plt.grid(which='both')
#     plt.title(str(loc_name)+'\nAverage Temperature\n Years: '+str(start_date.year)+'-'+str(end_date.year)+'; Elevation: '+str(dictionary['analysis_elev_min'])+'-'+str(dictionary['analysis_elev_max'])+'m', fontsize=16)
#     plt.savefig('monthly_Tavg'+str(loc_name)+'.png')
#     plt.show()
    
# def plot_meanTmin(dictionary, loc_name, start_date, end_date):
#     # Plot 1: Monthly temperature analysis of Livneh data
#     if 'meanmonth_temp_min_liv2013_met_daily' and 'meanmonth_temp_min_wrf2014_met_daily' not in dictionary.keys():
#         pass

#     # generate month indices
#     wy_index=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
#     wy_numbers=[10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9]
#     month_strings=[ 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sept']
    
#     # initiate the plot object
#     fig, ax=plt.subplots(1,1,figsize=(10, 6))

#     if 'meanmonth_temp_min_liv2013_met_daily' in dictionary.keys():
#         # Liv2013

#         plt.plot(wy_index, dictionary['meanmonth_temp_min_liv2013_met_daily'][wy_numbers],'r-', linewidth=1, label='Liv Temp min')  
    
#     if 'meanmonth_temp_min_wrf2014_met_daily' in dictionary.keys():
#         # WRF2014
#         plt.plot(wy_index, dictionary['meanmonth_temp_min_wrf2014_met_daily'][wy_numbers],'b-',linewidth=1, label='WRF Temp min')
 
#     if 'meanmonth_temp_min_livneh2013_wrf2014bc_met_daily' in dictionary.keys():
#         # WRF2014
#         plt.plot(wy_index, dictionary['meanmonth_temp_min_livneh2013_wrf2014bc_met_daily'][wy_numbers],'g-',linewidth=1, label='WRFbc Temp min')
 
#     # add reference line at y=0
#     plt.plot([1, 12],[0, 0], 'k-',linewidth=1)

#     plt.ylabel('Temp (C)',fontsize=14)
#     plt.xlabel('Month',fontsize=14)
#     plt.xlim(1,12);
#     plt.xticks(wy_index, month_strings);
        
#     plt.tick_params(labelsize=12)
#     plt.legend(loc='best')
#     plt.grid(which='both')
#     plt.title(str(loc_name)+'\nMinimum Temperature\n Years: '+str(start_date.year)+'-'+str(end_date.year)+'; Elevation: '+str(dictionary['analysis_elev_min'])+'-'+str(dictionary['analysis_elev_max'])+'m', fontsize=16)
#     plt.savefig('monthly_Tmin'+str(loc_name)+'.png')
#     plt.show()
    
# def plot_meanTmax(dictionary, loc_name, start_date, end_date):
#     # Plot 1: Monthly temperature analysis of Livneh data
#     if 'meanmonth_temp_max_liv2013_met_daily' and 'meanmonth_temp_max_wrf2014_met_daily' not in dictionary.keys():
#         pass

#     # generate month indices
#     wy_index=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
#     wy_numbers=[10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9]
#     month_strings=[ 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sept']
    
#     # initiate the plot object
#     fig, ax=plt.subplots(1,1,figsize=(10, 6))

#     if 'meanmonth_temp_max_liv2013_met_daily' in dictionary.keys():
#         # Liv2013

#         plt.plot(wy_index, dictionary['meanmonth_temp_max_liv2013_met_daily'][wy_numbers],'r-', linewidth=1, label='Liv Temp max')  
    
#     if 'meanmonth_temp_max_wrf2014_met_daily' in dictionary.keys():
#         # WRF2014
#         plt.plot(wy_index, dictionary['meanmonth_temp_max_wrf2014_met_daily'][wy_numbers],'b-',linewidth=1, label='WRF Temp max')
 
#     if 'meanmonth_temp_max_livneh2013_wrf2014bc_met_daily' in dictionary.keys():
#         # WRF2014
#         plt.plot(wy_index, dictionary['meanmonth_temp_max_livneh2013_wrf2014bc_met_daily'][wy_numbers],'g-',linewidth=1, label='WRFbc Temp max')
 
#     # add reference line at y=0
#     plt.plot([1, 12],[0, 0], 'k-',linewidth=1)

#     plt.ylabel('Temp (C)',fontsize=14)
#     plt.xlabel('Month',fontsize=14)
#     plt.xlim(1,12);
#     plt.xticks(wy_index, month_strings);
        
#     plt.tick_params(labelsize=12)
#     plt.legend(loc='best')
#     plt.grid(which='both')
#     plt.title(str(loc_name)+'\nMaximum Temperature\n Years: '+str(start_date.year)+'-'+str(end_date.year)+'; Elevation: '+str(dictionary['analysis_elev_min'])+'-'+str(dictionary['analysis_elev_max'])+'m', fontsize=16)
#     plt.savefig('monthly_Tmax'+str(loc_name)+'.png')
#     plt.show()
    
    
# def renderWatershed(shapefile, outfilepath, epsg=4326, margin=0.25,
#                     basemap_image='Demographics/USA_Social_Vulnerability_Index'):

#     # generate the figure axis
#     fig = plt.figure(figsize=(3,3), dpi=500)
#     ax1 = plt.subplot2grid((1,1),(0,0))

#     # normalize the color distribution according to the value distribution
#     cmap = mpl.cm.gnuplot2

#     # calculate bounding box based on the watershed shapefile
#     watershed = fiona.open(shapefile)
#     minx, miny, maxx, maxy = watershed.bounds
#     w, h = maxx - minx, maxy - miny
#     watershed.close()

#     # generate basemap
#     m = Basemap(projection='merc', epsg=epsg, resolution='h', ax=ax1,
#                 llcrnrlon=minx-margin*w, llcrnrlat=miny-margin*h, urcrnrlon=maxx+margin*w, urcrnrlat=maxy+margin*h)
#     m.arcgisimage(service=basemap_image, xpixels=500)

#     # read and transform the watershed shapefiles
#     m.readshapefile(shapefile = shapefile.replace('.shp',''), name='watersheds',
#                     drawbounds=True, zorder=None, linewidth=0.5, color='m', antialiased=1, default_encoding='utf-8')
    
#     plt.savefig(outfilepath, dpi=500)
#     plt.show()
#     return(ax1)
    

# def griddedCellGradient(mappingfile, shapefile, outfilepath, plottitle, colorbar_label,
#                         spatial_resolution=1/16, margin=0.25, epsg=3857, column='ELEV', polygon_color='m',
#                         basemap_image='ESRI_Imagery_World_2D', cmap='coolwarm'):
#     """
    
    
#     mappingfile: (dir) the path to the mappingfile for the watershed gridded cell centroids
#     shapefile: (dir) the path to the ESRI shapefile for the watershed shape
#     spatial_resolution: (float) the degree of longitude-latitude separation between gridded cell centroids, e.g., 1/16
#     margin: (float) the fraction of width and height to view outside of the watershed shapefile, e.g., 0.25
#     crs: (dict) the coordinate reference system to use for the geodataframe, e.g. {'init':'epsg:3857'}
#     epsg: (int) the epsg code for regional projection, e.g. 3857
#     column: (str) the name of the column within the mappingfile to visualize with a color gradient
#     basemap_image: (str) the basemap arcgis service e.g., 'Canvas/World_Dark_Gray_Base' or 'ESRI_Imagery_World_2D'
#     cmap: (str) the code for matplotlib colormaps, e.g. 'coolwarm',
#     plottitle: (str) the title of the plot
#     polygon_color: (str) the colormap code to fill each shapefile polygon; default is 'm' for magenta
#     colorbar_label: (str) the label for the colorbar
#     outfilepath: (dir) the path for the output image file
#     """
    
#     # generate the figure axis
#     fig = plt.figure(figsize=(3,3), dpi=500)
#     ax1 = plt.subplot2grid((1,1),(0,0))

#     # read mappingfile, generate gridded cell boxes, and initialize the geodataframe
#     map_df = pd.read_csv(mappingfile)
#     midpt=spatial_resolution/2
#     crs={'init':'epsg:{0}'.format(epsg)}
#     geometry = map_df.apply(lambda x: box(x['LONG_']-midpt, x['LAT']-midpt, x['LONG_']+midpt, x['LAT']+midpt), axis=1)
#     map_df2 = gpd.GeoDataFrame(map_df, crs=crs, geometry=geometry)
    
#     # normalize the color distribution according to the value distribution
#     colormap = mpl.cm.get_cmap(cmap)
#     norm = mpl.colors.LogNorm(map_df2[column].min(), map_df2[column].max())
#     color_producer = mpl.cm.ScalarMappable(norm=norm, cmap=colormap)
    
#     # calculate bounding box based on the watershed shapefile
#     watershed = fiona.open(shapefile)
#     minx, miny, maxx, maxy = watershed.bounds
#     w, h = maxx - minx, maxy - miny
#     watershed.close()

#     # generate basemap
#     m = Basemap(projection='merc', epsg=epsg, resolution='h', ax=ax1,
#                 llcrnrlon=minx-margin*w, llcrnrlat=miny-margin*h, urcrnrlon=maxx+margin*w, urcrnrlat=maxy+margin*h)

#     # read and transform the watershed shapefiles
#     m.readshapefile(shapefile=shapefile.replace('.shp',''), name='watershed', drawbounds=True, color=polygon_color)
#     m.arcgisimage(service=basemap_image, xpixels=500)

#     # load and transform each polygon in shape
#     patches = []
#     for ind, eachpol in map_df2.iterrows():
#         mpoly = shapely.ops.transform(m, eachpol['geometry'])
#         patches.append(PolygonPatch(mpoly, fc=color_producer.to_rgba(eachpol[column]), linewidth=0, alpha=0.5, zorder=5.0))
        
#     # assimilate shapes to plot axis
#     coll = PatchCollection(patches, cmap=cmap, match_original=True, zorder=5.0)
#     ax1.add_collection(coll)
#     coll.set_alpha(0.4)
    
#     # generate colorbar
#     coll.set_array(np.array(map_df2[column]))
#     cbar = plt.colorbar(coll, shrink=0.5)
#     cbar.ax.set_ylabel(colorbar_label, rotation=270, size=3, labelpad=5) # colorbar label
#     cbar.ax.tick_params(labelsize=3) # colorbar tick fontsize
    
#     # save image
#     plt.title(plottitle, fontsize=3)
#     plt.savefig(outfilepath, dpi=500)
#     plt.show()
    
    
# def renderValuesInPoints(vardf, vardf_dateindex, shapefile, outfilepath, plottitle, colorbar_label,
#                          vmin=None,vmax=None,spatial_resolution=1/16, margin=0.5, epsg=3857,
#                          basemap_image='Canvas/World_Dark_Gray_Base', cmap='coolwarm'):
#     """
#     A function to render the dynamics across gridded cell centroids on the spatial landscape
    
#     vardf: (dataframe) a time-series dataframe for a variable with time-points (rows) and gridded cell centroids (column)
#     vardf_dateindex: (datetime or float) a datetime identifier to extract a row of data for visualization
#     shapefile: (dir) the path to a shapefile
#     outfilepath: (dir) the path for the output image file
#     plottitle: (str) the title of the plot
#     colorbar_label: (str) the label for the colorbar
#     spatial_resolution: (float) the degree of longitude-latitude separation between gridded cell centroids, e.g., 1/16
#     margin: (float) the fraction of width and height to view outside of the watershed shapefile
#     epsg: (int) the epsg code for regional projection, e.g. 3857
#     basemap_image: (str) the basemap arcgis service e.g., 'Canvas/World_Dark_Gray_Base' or 'ESRI_Imagery_World_2D'
#     cmap: (str) the code for matplotlib colormaps, e.g. 'coolwarm',
#     """
    
#     # generate the figure axis
#     fig = plt.figure(figsize=(1.5,1.5), dpi=500)
#     ax1 = plt.subplot2grid((1,1),(0,0))

#     # set params
#     if isinstance(vmin, type(None)):
#         vmin=vardf.values.flatten().min()
        
#     if isinstance(vmax, type(None)):
#         vmax=vardf.values.flatten().max()

#     # generate the polygon color-scheme
#     cmap = mpl.cm.get_cmap(cmap)
#     norm = mpl.colors.Normalize(vmin, vmax)
#     color_producer = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)

#     # calculate bounding box based on the watershed shapefile
#     watershed = fiona.open(shapefile)
#     minx, miny, maxx, maxy = watershed.bounds
#     w, h = maxx - minx, maxy - miny
#     watershed.close()
    
#     # generate basemap
#     m = Basemap(projection='merc', epsg=epsg, resolution='h', ax=ax1,
#                 llcrnrlon=minx-margin*w, llcrnrlat=miny-margin*h, urcrnrlon=maxx+margin*w, urcrnrlat=maxy+margin*h)
#     m.arcgisimage(service=basemap_image, xpixels=500)
                         
#     # watershed
#     m.readshapefile(shapefile=shapefile.replace('.shp',''), name='watershed', drawbounds=True, color='m')
    
#     # variable dataframe
#     midpt=spatial_resolution/2
#     crs={'init':'epsg:{0}'.format(epsg)}
#     cat=vardf.T.reset_index(level=[1,2]).rename(columns={'level_1':'LAT','level_2':'LONG_'})
#     geometry = cat.apply(lambda x: shapely.ops.transform(m, box(x['LONG_']-midpt, x['LAT']-midpt, 
#                                                                 x['LONG_']+midpt, x['LAT']+midpt)), axis=1)
#     cat = gpd.GeoDataFrame(cat, crs=crs, geometry=geometry).reset_index(drop=True)

#     # geopandas print
#     cat.plot(column=vardf_dateindex, cmap=cmap, alpha=0.4, ax=ax1, vmin=vmin, vmax=vmax)

#     # assimilate the shapes to plot
#     patches = []
#     for ind, eachpol in cat.iterrows():
#         patches.append(PolygonPatch(eachpol['geometry'], linewidth=0, zorder=5.0,
#                                     fc=color_producer.to_rgba(eachpol[vardf_dateindex])))

#     # assimilate shapes into a patch collection
#     coll = PatchCollection(patches, cmap=cmap, match_original=True, zorder=10.0)
    
#     # generate colorbar
#     coll.set_array(vardf.values.flatten())
#     coll.set_clim([vmin, vmax])
#     cbar = plt.colorbar(coll, shrink=0.5)
#     cbar.ax.set_ylabel(colorbar_label, rotation=270, size=3, labelpad=5) # colorbar label
#     cbar.ax.tick_params(labelsize=3) # colorbar tick fontsize

#     # save image
#     plt.title(plottitle, fontsize=3)
#     plt.savefig(outfilepath)
#     plt.show()

# def renderValuesInPoints_scale(vardf, vardf_dateindex, vardfmin, vardfmax, shapefile, outfilepath, plottitle, 
#                                colorbar_label, spatial_resolution=1/16, margin=0.5, epsg=3857,
#                                basemap_image='Canvas/World_Dark_Gray_Base', cmap='coolwarm'):
#     """
#     A function to render the dynamics across gridded cell centroids on the spatial landscape
    
#     vardf: (dataframe) a time-series dataframe for a variable with time-points (rows) and gridded cell centroids (column)
#     vardf_dateindex: (datetime or float) a datetime identifier to extract a row of data for visualization
#     vardfmin: (int) the minimum value for the colormap scale
#     vardfmax: (int) the maximum value for the colormap scale
#     shapefile: (dir) the path to a shapefile
#     outfilepath: (dir) the path for the output image file
#     plottitle: (str) the title of the plot
#     colorbar_label: (str) the label for the colorbar
#     spatial_resolution: (float) the degree of longitude-latitude separation between gridded cell centroids, e.g., 1/16
#     margin: (float) the fraction of width and height to view outside of the watershed shapefile
#     epsg: (int) the epsg code for regional projection, e.g. 3857
#     basemap_image: (str) the basemap arcgis service e.g., 'Canvas/World_Dark_Gray_Base' or 'ESRI_Imagery_World_2D'
#     cmap: (str) the code for matplotlib colormaps, e.g. 'coolwarm',
#     """
    
#     # generate the figure axis
#     fig = plt.figure(figsize=(1.5,1.5), dpi=500)
#     ax1 = plt.subplot2grid((1,1),(0,0))

#     # generate the polygon color-scheme
#     cmap = mpl.cm.get_cmap(cmap)
#     norm = mpl.colors.Normalize(vardfmin, vardfmax)
#     color_producer = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)

#     # calculate bounding box based on the watershed shapefile
#     watershed = fiona.open(shapefile)
#     minx, miny, maxx, maxy = watershed.bounds
#     w, h = maxx - minx, maxy - miny
#     watershed.close()
    
#     # generate basemap
#     m = Basemap(projection='merc', epsg=epsg, resolution='h', ax=ax1,
#                 llcrnrlon=minx-margin*w, llcrnrlat=miny-margin*h, urcrnrlon=maxx+margin*w, urcrnrlat=maxy+margin*h)
#     m.arcgisimage(service=basemap_image, xpixels=500)
                         
#     # watershed
#     m.readshapefile(shapefile=shapefile.replace('.shp',''), name='watershed', drawbounds=True, color='k')
    
#     # variable dataframe
#     midpt=spatial_resolution/2
#     crs={'init':'epsg:{0}'.format(epsg)}
#     cat=vardf.T.reset_index(level=[1,2]).rename(columns={'level_1':'LAT','level_2':'LONG_'})
#     geometry = cat.apply(lambda x: 
#                          shapely.ops.transform(m, box(x['LONG_']-midpt, x['LAT']-midpt, 
#                                                       x['LONG_']+midpt, x['LAT']+midpt)), axis=1)
#     cat = gpd.GeoDataFrame(cat, crs=crs, geometry=geometry).reset_index(drop=True)

#     # geopandas print
#     cat.plot(column=vardf_dateindex, cmap=cmap, alpha=0.4, ax=ax1,
#              vmin=vardfmin, vmax=vardfmax)

#     # assimilate the shapes to plot
#     patches = []
#     for ind, eachpol in cat.iterrows():
#         patches.append(PolygonPatch(eachpol['geometry'], linewidth=0, zorder=5.0,
#                                     fc=color_producer.to_rgba(eachpol[vardf_dateindex])))

#     # assimilate shapes into a patch collection
#     coll = PatchCollection(patches, cmap=cmap, match_original=True, zorder=10.0)
    
#     # generate colorbar
#     coll.set_array(vardf.values.flatten())
#     coll.set_clim([vardfmin, vardfmax])
#     cbar = plt.colorbar(coll, shrink=0.5)
#     cbar.ax.set_ylabel(colorbar_label, rotation=270, size=3, labelpad=5) # colorbar label
#     cbar.ax.tick_params(labelsize=3) # colorbar tick fontsize

#     # save image
#     plt.title(plottitle, fontsize=3)
#     plt.savefig(outfilepath)
#     plt.show()

    
# def findStationCode(mappingfile, colvar, colvalue):
#     """
#     mappingfile: (dir) the file path to the mappingfile, which contains the LAT, LONG_, and ELEV coordinates of interest
#     colvar: (string) a column name in mappingfile
#     colvalue: (value) a value that corresponds to the colvar column
#     """
#     mapdf = pd.read_csv(mappingfile)
#     outcome = mapdf.loc[mapdf[colvar]==colvalue, :][['FID','LAT','LONG_']].reset_index(drop=True).set_index('FID')
#     return(outcome.to_records())


# def mappingfileSummary(listofmappingfiles, listofwatershednames, meta_file):
#     """
#     Tabulate data availability for all mapping files
    
#     listofmappingfiles: (list) path directories to the mappingfile for each watershed to be compared
#     listofwatershednames: (list) strings for the name of each watershed
#     """
#     datainventory = []
    
#     # loop each mappingfile
#     for mappingfile, watershedname in zip(listofmappingfiles, listofwatershednames):
#         mapdf = pd.read_csv(mappingfile)
        
#         # summarize the total dimensions
#         tmp=[]
#         tmp.append(tuple(['Watershed',watershedname]))
#         tmp.append(tuple(['Median elevation in meters [range](No. gridded cells)',
#                           '{0}[{1}-{2}] (n={3})'.format(int(mapdf.ELEV.median()),
#                                                         int(mapdf.ELEV.min()), 
#                                                         int(mapdf.ELEV.max()),
#                                                         int(len(mapdf)))]))
        
#         # summarize for each gridded data product
#         for each in mapdf.columns:
#             if each in meta_file.keys():
#                 filesobtained = mapdf[mapdf[each].apply(lambda x: pd.notnull(x))].reset_index()
#                 if len(filesobtained)>0:
#                     tmp.append(tuple([each, 
#                                       '{0}[{1}-{2}] (n={3})'.format(int(filesobtained.ELEV.median()), 
#                                                                     int(filesobtained.ELEV.min()), 
#                                                                     int(filesobtained.ELEV.max()), 
#                                                                     int(filesobtained[each].count()))]))

#         # interpret list to table form
#         t1 = pd.DataFrame.from_records(tmp, columns=['datasets','values']).set_index('datasets').T.set_index(['Watershed',
#                                                                       'Median elevation in meters [range](No. gridded cells)'])

#         # compile into summary table
#         if len(datainventory)==0:
#             datainventory=t1.copy()
#         else:
#             datainventory=pd.concat([datainventory, t1], axis=0)
    
#     # conform into datasets by watershed summary
#     datainventory = datainventory.T.fillna(0)
#     datainventory.index.name = None
#     return(datainventory)


# def dissolveShapefile(listOfShapefiles, listOfNames, newShapefilepath):
#     """
#     dissolve MultiPolygon Shapefiles into a single shape polygon
    
#     listOfShapefiles: (list) list of shapefile paths
#     listOfNames: (list) list of shape names corresponding to the order in listOfShapefiles
#     newShapefilepath: (dir) the path to the shapefile of dissolved shapes
#     """
#     listOfNewShapes = []
#     for eachShape, eachName in zip(listOfShapefiles, listOfNames):
        
#         # create dissolved Shapefile destination
#         newShapefile = eachShape.replace('.shp','_2.shp')
        
#         # read shape
#         shape = gpd.read_file(eachShape)
#         shape['shapeName'] = eachName
        
#         # dissolve shape into new shapefile
#         newShape = shape.dissolve(by='shapeName').reset_index()[['shapeName','geometry']]
#         newShape.to_file(newShapefile)
        
#         listOfNewShapes.append(newShape)
        
#     # concatenate the dissolved shape polygons together
#     allShapes = pd.concat(listOfNewShapes, axis=0).reset_index(drop=True)
#     allShapes.to_file(newShapefilepath)
#     return(allShapes)

    
# def renderValueInBoxplot(vardf,outfilepath,plottitle,time_steps,value_name,cmap,
#                          wateryear=False,vmin=None,vmax=None,figsize=(10,4)):
#     """
#     vardf: (dataframe) a dataframe with dates in the rows and stations as the columns
#     outfilepath: (dir) the path for the boxplot png file
#     plottitle: (str) the figure title
#     time_steps: (str) 'month' or 'year' for the axis display
#     value_name: (str) the x-axis label for the data categories being plotted
#     cmap: (str) the colormap code e.g., 'seismic_r'
#     wateryear: (True/False) for monthly displays in a wateryear order
#     vmin: (float) the minimum value for the color display
#     vmax: (float) the maximum value for the color display
#     figsize: (tuple) the shape of the figure dimensions
#     """    
#     # generate long table    
#     longtable = pd.melt(vardf.T, value_name=value_name).rename(columns={'variable':time_steps})
    
#     # if the time_steps column are dates, extract month or year
#     if isinstance(longtable[time_steps][0], type(pd.datetime.strptime('1900-01-01','%Y-%m-%d'))):
#         if time_steps=='month':
#             longtable[time_steps] = longtable[time_steps].apply(lambda x: x.month)
#         elif time_steps=='year':
#             longtable[time_steps] = longtable[time_steps].apply(lambda x: x.year)
    
#     # xaxis order
#     if (wateryear==True):
#         xaxis_order = [10,11,12,1,2,3,4,5,6,7,8,9]
#         xaxis_labels=[pd.datetime.strptime(str(x),'%m').strftime('%b') for x in xaxis_order]
#     else:
#         xaxis_order=sorted(longtable[time_steps].unique())
#         try:
#             # monthly labels
#             xaxis_labels=[pd.datetime.strptime(str(x),'%m').strftime('%b') for x in xaxis_order]
#         except:
#             # non-monthly labels
#             xaxis_labels=[str(x) for x in xaxis_order]
            
#     # set params
#     if isinstance(vmin, type(None)):
#         vmin=longtable[value_name].min()
        
#     if isinstance(vmax, type(None)):
#         vmax=longtable[value_name].max()
    
#     # set scalar normalization
#     norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
    
#     # normalize colors
#     cm_pdt = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)
        
#     # generate colors
#     colors = cm_pdt.to_rgba(longtable.groupby([time_steps])[value_name].median()[xaxis_order])

#     # plot and align colors
#     fig, ax1=plt.subplots(1,1,figsize=figsize)
#     ax1 = sns.boxplot(x=time_steps, y=value_name, order=xaxis_order, data=longtable, palette=colors)
#     ax1.xaxis.set_ticklabels(xaxis_labels, rotation=90)
#     vrange = vmax-vmin
#     plt.ylim(np.round(vmin-(vrange*0.01),0), np.round(vmax+(vrange*0.01),0))

#     # save image
#     plt.title(plottitle, fontsize=12)
#     plt.savefig(outfilepath)
#     plt.show()
#     return(ax1)
    
    
# def multiSiteVisual(listOfShapefiles, listOfNames,
#                     multishape='eachwatershed.shp', singleshape='allwatersheds.shp', fileoutpath='annotated_map.png',
#                     projection='merc', epsg=3857, polygon_color='m', margin=0.75, 
#                     scale_x_dist=0, scale_y_dist=-0.25, scale_ref_length=100, scale_yoffset=10000,
#                     text_x_dist=0, text_y_dist=0.25):
#     """
#     Visualize the study site(s)
    
#     listOfShapefiles: (list) a list of paths to shapefile to visualize e.g. [sauk, elwha]
#     listOfNames: (list) Site names corresponding with listOfShapefiles e.g., ['Sauk-Suiattle river','Elwha river']
#     multishape: (dir) an output shapefile path with each shapefile as a polygon; default is 'eachwatershed.shp'
#     singleshape: (dir) an output shapefile path with all polygons dissolved into one; default is 'allwatersheds.shp'
#     fileoutpath: (dir) an output file path for the final PNG image; default is 'annotated_map.png'
#     projection: (str) the basemap code for the projection; default is 'merc'
#     epsg: (int) the EPSG coordinate reference system code; default is 3857
#     polygon_color: (str) the colormap code to fill each shapefile polygon; default is 'm' for magenta
#     margin: (float) the margin multiplier to set the basemap boundary; default is 0.75 of the height and width
#     scale_x_dist: (float) the distance x-degrees from the singleshape centroid to place the mapscale; default is 0
#     scale_y_dist: (float) the distance y-degrees from the singleshape centroid to place the mapscale; default is -0.25
#     scale_ref_length: (int) the reference distance in km; default is 100
#     scale_yoffset: (int) the vertical height of the mapscale in meters; default is 10000 in the projection scale
#     text_x_dist: (float) the distance x-degrees from each polygon centroid to place the Site name; default is 0
#     text_y_dist: (float) the distance y-degrees from each polygon centroid to place the Site name; default is 0.25
#     """
#     # inspect each shapefile to be in latlong coordinates
#     for eachshp in listOfShapefiles:
#         reprojShapefile(sourcepath=eachshp)
        
#     # dissolve shapefiles into a single shapefile containing multiple shape polygons
#     w1 = dissolveShapefile(listOfShapefiles=listOfShapefiles, listOfNames=listOfNames, newShapefilepath = multishape)
    
#     # dissolve all shapefiles into a single shapefile containing a single shape polygon
#     w2 = w1.copy()
#     w2['shapeName'] = 'watershed'
#     w2 = w2.dissolve(by='shapeName')
#     w2.to_file(singleshape)

#     # calculate bounding box based on the watershed shapefile
#     minx, miny, maxx, maxy = w2.bounds.iloc[0]
#     w, h = maxx - minx, maxy - miny
#     center_x, center_y = np.array(w2.centroid.iloc[0])

#     # generate the figure axis
#     fig = plt.figure(figsize=(3,3), dpi=500)
#     ax1 = plt.subplot2grid((1,1),(0,0))
    
#     # normalize the color distribution according to the value distribution
#     cmap = mpl.cm.gnuplot2
    
#     # generate basemap
#     if projection=='merc':
#         m = Basemap(projection='merc', epsg=epsg, resolution='h', ax=ax1,
#                     llcrnrlon=minx-margin*w, llcrnrlat=miny-margin*h,
#                     urcrnrlon=maxx+margin*w, urcrnrlat=maxy+margin*h)
#     else:
#         # center coordinate (for tranverse mercator projections)
#         lon0, lat0 = np.array(w2.centroid[0])
#         m = Basemap(projection='tmerc', resolution='h', ax=ax1, lat_0=lat0, lon_0=lon0,
#                     llcrnrlon=minx-margin*w, llcrnrlat=miny-margin*h, urcrnrlon=maxx+margin*w, urcrnrlat=maxy+margin*h)

#     # affix boundaries
#     m.drawcountries(linewidth=0.1)
#     m.drawcoastlines(linewidth=0.1)
#     m.drawmapboundary(fill_color='lightgray')
#     m.fillcontinents(color='white', lake_color='lightgray')
#     m.drawrivers(linewidth=0.1, color='lightgray', )
#     m.drawstates(linewidth=0.1, color='gray', linestyle='solid')
#     m.drawcountries(linewidth=0.1, color='black')
    
#     # draw cardinal markers
#     m.drawparallels(np.arange(-180,180,10),labels=[1,0,0,0], fontsize=4, color='black', linewidth=0.5)
#     m.drawmeridians(np.arange(-180,180,10),labels=[0,0,1,0], fontsize=4, color='black', linewidth=0.5)
    
#     # read and transform the watershed shapefiles
#     m.readshapefile(shapefile = singleshape.replace('.shp',''), name='allwatersheds', linewidth=0)
#     m.readshapefile(shapefile = multishape.replace('.shp',''), name='eachwatershed', linewidth=0)
    
#     # load and transform each polygon in shape
#     patches = [PolygonPatch(Polygon(np.array(shape)), fc=polygon_color, ec=polygon_color, linewidth=0.1, zorder=5.0) 
#                for info, shape in zip(m.allwatersheds_info, m.allwatersheds)]

#     # assimilate shapes to plot axis
#     coll = PatchCollection(patches, cmap=cmap, match_original=True, zorder=5.0)
#     ax1.add_collection(coll)

#     # draw distance scale (coordinate in degrees)
#     m.drawmapscale(center_x+scale_x_dist, center_y+scale_y_dist, maxx, maxy, 
#                    length=scale_ref_length, yoffset=scale_yoffset, barstyle='fancy', fontsize=3, linewidth=0.1)

#     # parameters annotated based on non-cyl projections
#     if epsg!=4326:

#         # annotate watersheds
#         for eachinfo, eachpoly in zip(m.eachwatershed_info, m.eachwatershed):
#             if (eachinfo['RINGNUM']==1):

#                 # annotate the text in the projection-scaled position
#                 xycentroid = np.array(Polygon(eachpoly).centroid)
#                 x0,y0 = m(xycentroid[0], xycentroid[1], inverse=True)
#                 xytext = np.array(m(x0+text_x_dist, y0+text_y_dist, inverse=False)) 
#                 text = eachinfo['shapeName'].replace(' ','\n')
#                 plt.annotate(text, fontsize=3, arrowprops=dict(arrowstyle="->"), xy=xycentroid, xytext=xytext)

#     # save and show map
#     plt.savefig(fileoutpath, dpi=500)
#     plt.show()
#     return(w1)


# def remapCatalog(homedir, mappingfile, subdir, catalog_label):
#     """
#     Get the Livneh el al., 2015 Daily Meteorology files of interest using the reference mapping file
    
#     homedir: (dir) the home directory to be used for establishing subdirectories
#     mappingfile: (dir) the file path to the mappingfile, which contains the LAT, LONG_, and ELEV coordinates of interest
#     subdir: (dir) the subdirectory to be established under homedir
#     catalog_label: (str) the preferred name for the series of catalogged filepaths
#     """
#     # check and generate Daily MET livneh 2015 data directory
#     filedir=os.path.join(homedir, subdir)
#     ensure_dir(filedir)
    
#     # generate table of lats and long coordinates
#     maptable = pd.read_csv(mappingfile)
    
#     # update the mappingfile with the file catalog
#     addCatalogToMap(outfilepath=mappingfile, maptable=maptable, folderpath=filedir, catalog_label=catalog_label)
    
    
# def computeGCSurfaceArea(shapefile, spatial_resolution, vardf):
#     """
#     Data-driven computation of gridded cell surface area using the list of gridded cells centroids
    
#     shapefile: (dir) the path to the study site shapefile for selecting the UTM boundary
#     spatial_resolution: (float) the spatial resolution in degree coordinate reference system e.g., 1/16
#     vardf: (dataframe) input dataframe that contains FID, LAT and LONG references for each gridded cell centroid
    
#     return: (mean surface area in meters-squared, standard deviation in surface area)
#     """
    
#     # ensure projection into WGS84 longlat values
#     reprojShapefile(shapefile)

#     # generate the figure axis
#     fig = plt.figure(figsize=(2,2), dpi=500)
#     ax1 = plt.subplot2grid((1,1),(0,0))

#     # calculate bounding box based on the watershed shapefile
#     watershed = gpd.read_file(shapefile)
#     watershed['watershed']='watershed'
#     watershed = watershed.dissolve(by='watershed')

#     # extract area centroid, bounding box info, and dimension shape
#     lon0, lat0 = np.array(watershed.centroid.iloc[0])
#     minx, miny, maxx, maxy = watershed.bounds.iloc[0]

#     # generate traverse mercatur projection
#     m = Basemap(projection='tmerc', resolution='l', ax=ax1, lat_0=lat0, lon_0=lon0,
#                 llcrnrlon=minx, llcrnrlat=miny, urcrnrlon=maxx, urcrnrlat=maxy)

#     # generate gridded cell bounding boxes
#     midpt_dist=spatial_resolution/2
#     cat=vardf.T.reset_index(level=[1,2]).rename(columns={'level_1':'LAT','level_2':'LONG_'})
#     geometry = cat.apply(lambda x: 
#                          shapely.ops.transform(m, box(x['LONG_']-midpt_dist, x['LAT']-midpt_dist,
#                                                       x['LONG_']+midpt_dist, x['LAT']+midpt_dist)), axis=1)

#     # compute gridded cell area
#     gc_area = geometry.apply(lambda x: x.area)
#     plt.gcf().clear()
#     return(gc_area.mean(), gc_area.std())


# def monthlyExceedence_cfs (df_dict,daily_streamflow_dfname,gridcell_area,exceedance):
#     """
#     df_dict: (dict) dictionary of spatial-temporal computation dataframes
#     daily_streamflow_dfname: (str) name of daily streamflow dataframe in df_dict in millimeters per second (mm/s)
#     gridcell_area: (float) the estimated surface area of the gridded area in square meters
#     exceedance: (float) the percent exceedance probability
#     """
    
#     # dataset name
#     dataset = daily_streamflow_dfname.split('_',1)[1]

#     # convert mm_s to m_s
#     mm_s = df_dict[daily_streamflow_dfname]
#     m_s = mm_s*0.001

#     # multiply streamflow (mps) with grid cell surface area (m2) to produce volumetric streamflow (cms)
#     cms = m_s.multiply(np.array(gridcell_area))

#     # convert m^3/s to cfs; multiply with (3.28084)^3
#     cfs = cms.multiply((3.28084)**3)

#     # output to df_dict
#     df_dict['cfs_'+daily_streamflow_dfname] = cfs

#     months = range(1,13)
#     Exceed=pd.DataFrame()

#     # for each month
#     for ind, eachmonth in enumerate(months):
#         month_res = cfs.iloc[cfs.index.month==eachmonth,:].apply(lambda x: np.percentile(x, 100-exceedance), axis=0)
#         Exceed = pd.concat([Exceed, pd.DataFrame(month_res).T], axis=0)
    
#     Exceed.index=months
#     df_dict['EXCEED{0}_{1}'.format(exceedance,dataset)] = Exceed
#     return(df_dict)


# def monthlyExceedence_mmday (df_dict,daily_streamflow_dfname,exceedance):
#     """
#     df_dict: (dict) dictionary of spatial-temporal computation dataframes
#     daily_streamflow_dfname: (str) name of daily streamflow dataframe in df_dict in millimeters per second (mm/s)
#     gridcell_area: (float) the estimated surface area of the gridded area in square meters
#     exceedance: (float) the percent exceedance probability
#     """
    
#     # dataset name
#     dataset = daily_streamflow_dfname.split('_',1)[1]

#     # initialize the streamflow in mm_day
#     mmday = df_dict[daily_streamflow_dfname]

#     months = range(1,13)
#     Exceed=pd.DataFrame()

#     # for each month
#     for ind, eachmonth in enumerate(months):
#         month_res = mmday.iloc[mmday.index.month==eachmonth,:].apply(lambda x: np.percentile(x, 100-exceedance), axis=0)
#         Exceed = pd.concat([Exceed, pd.DataFrame(month_res).T], axis=0)
    
#     Exceed.index=months
#     df_dict['EXCEED{0}_mmday_{1}'.format(exceedance,dataset)] = Exceed
#     return(df_dict)