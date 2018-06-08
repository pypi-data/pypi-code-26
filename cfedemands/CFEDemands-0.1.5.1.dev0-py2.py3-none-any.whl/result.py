# [[file:~/Research/CFEDemands/Empirics/cfe_estimation.org::result_class][result_class]]
# Tangled on Thu Jun  7 21:40:57 2018
import numpy as np
import pandas as pd
from . import estimation 
import xarray as xr
import warnings
from collections import namedtuple

def is_none(x):
    """
    Tests for None in an array x.
    """
    if np.any(np.equal(x,None)):
        return True
    else:
        try:
            if len(x.shape)==0:
                return True
        except AttributeError:
            if isinstance(x,str):
                if len(x)==0: return True
                else: return False
            elif np.isscalar(x): return x is None
            elif isinstance(x,list): return None in x
            else:
                raise(TypeError,"Problematic type.")

def to_dataframe(arr,column_index=None,name=None,dropna_all=True):
    """Convert =xarray.DataArray= into a =pd.DataFrame= with indices etc. usable by =cfe=.
    """
    df = arr.to_dataframe('foo').squeeze()

    if column_index is not None:
        df = df.unstack(column_index)

    if dropna_all:
        df.dropna(how='all',inplace=True)

    df.name = name
    return df

def from_dataframe(df,index_name=None):
    """Convert from dataframe used in cfe.estimation to xarray.DataArray.
    """
    if index_name is not None:
        df.index = df.index.set_names(index_name)

    df = pd.DataFrame(df) # Series to dataframe
    if not is_none(df.columns.names):
        df = df.stack(df.columns.names)

    arr = df.squeeze().to_xarray()

    return arr

Indices = namedtuple('Indices',['j','t','m','i','k'])

class Result(xr.Dataset):

    def __init__(self,**kwargs):
        try:
            ds = kwargs.pop('data')
            super(Result,self).__init__(ds.variables,attrs=ds.attrs)
        except KeyError:
            arrs = dict(alpha=None, beta=None, delta=None,
                        prices=None,characteristics=None,loglambdas=None,
                        a=None, yhat=None, ce=None,
                        cehat=None, e=None, delta_covariance=None, 
                        se_delta=None, se_beta=None, se_a = None,
                        y=None,logp=None,z=None)

            for k in arrs:
                try:
                    arrs[k] = kwargs.pop(k)
                except KeyError:
                    pass

            attrs = dict(numeraire=None,firstround=None,
                         min_proportion_items=1./8,min_xproducts=30,
                         useless_expenditures=True,
                         stderr_tol=0.01,
                         indices = Indices('j','t','m','i','k'),
                         verbose=False)

            attrs.update(kwargs)

            super(Result,self).__init__(data_vars=arrs, attrs=attrs)


        if is_none(self.z) and  not is_none(self.characteristics):
            self['z'] = self.characteristics
        elif not is_none(self.z) and  is_none(self.characteristics):
            self['characteristics'] = self.z
        elif is_none(self.characteristics) and not is_none(self.y):
            self['characteristics'] = pd.DataFrame(index=self.y.isel(i=0).index).to_xarray()
            self['z'] = self['characteristics']

        if is_none(self.logp) and not is_none(self.prices):
            self['logp'] = np.log(self.prices)
        elif not is_none(self.logp) and is_none(self.prices):
            self['prices'] = np.exp(self.logp)

        if not is_none(self.beta) and not is_none(self.alpha):
            assert(self.alpha.shape == self.beta.shape)

        if is_none(self.attrs['firstround']) and not is_none(self.y):
            self.attrs['firstround'] = self.y.coords['t'][0].item()

        if not is_none(self.numeraire):
            numeraire = self.numeraire
            try:
                self.set_numeraire(numeraire)
            except KeyError:
                warnings.warn('No prices for numeraire %s.' % numeraire)
                self.attrs['numeraire']=None

    def drop_useless_expenditures(self):
        if self.attrs['useless_expenditures']:
            y = self.y
            min_proportion_items = self.attrs['min_proportion_items']
            min_xproducts = self.attrs['min_xproducts']

            use_goods=y.coords['i'].data

            # Convert to pd.DataFrame
            y = to_dataframe(y.sel(i=use_goods).rename({'m':'mkt'}),'i')

            # The criterion below (hh must have observations for at least min_proportion_items of goods) ad hoc
            using_goods=(y.T.count()>=np.floor(len(use_goods) * min_proportion_items))
            y=y.loc[using_goods] # Drop households with too few expenditure observations, keep selected goods

            y = estimation.drop_columns_wo_covariance(y,min_obs=min_xproducts,VERBOSE=False)
            # Only keep goods with observations in each (t,mkt)
            y = y.loc[:,(y.groupby(level=['t','mkt']).count()==0).sum()==0]

            y = from_dataframe(y).rename({'mkt':'m'}).dropna('i',how='all')

            new = self.sel(i=y.coords['i'],j=y.coords['j'])

            new.attrs['useless_expenditures'] = False

            self.__dict__.update(new.__dict__)

        return to_dataframe(self.y.rename({'m':'mkt'}),'i')

    def get_reduced_form(self,VERBOSE=False):
        y = self.drop_useless_expenditures() # Returns a dataframe
        z = to_dataframe(self.z.rename({'m':'mkt'}),'k')

        a,ce,d,sed,sea,V = estimation.estimate_reduced_form(y,z,return_se=True,return_v=True,VERBOSE=VERBOSE)
        ce.dropna(how='all',inplace=True)

        self['a'] = from_dataframe(a,'i').rename({'mkt':'m'})
        self['delta'] = from_dataframe(d).to_array('k')
        self['ce'] = from_dataframe(ce).rename({'mkt':'m'})
        self['se_delta'] = from_dataframe(sed)
        self['se_a'] = from_dataframe(sea).rename({'mkt':'m'})
        self['delta_covariance'] = V.to_xarray().rename({'items':'i','major_axis':'k','minor_axis':'kp'})

    def get_loglambdas(self):
        if is_none(self.loglambdas):
            if is_none(self.ce):
                self.get_reduced_form()

            min_obs = self.attrs['min_xproducts']

            ce = to_dataframe(self.ce.rename({'m':'mkt'}),'i')

            bphi,logL = estimation.get_loglambdas(ce,TEST=False,min_obs=min_obs)

            assert np.abs(logL.groupby(level='t').std().iloc[0] - 1) < 1e-12, \
                "Problem with normalization of loglambdas"

            cehat=np.outer(pd.DataFrame(bphi),pd.DataFrame(-logL).T).T
            cehat=pd.DataFrame(cehat,columns=bphi.index,index=logL.index)

            self['cehat'] = from_dataframe(cehat).rename({'mkt':'m'})
            self['loglambdas'] = logL.to_xarray().rename({'mkt':'m'})
            self['beta'] = bphi.to_xarray()

        return self.loglambdas

    def get_beta(self):
        if is_none(self.beta):
            self.get_loglambdas()

        return self.beta

    def get_cehat(self):
        if is_none(self.beta):
            self.get_loglambdas()

        return self.cehat

    def get_stderrs(self):
        if is_none(self.se_beta):
            if is_none(self.ce):
                self.get_reduced_form()

            tol = self.attrs['stderr_tol']
            VB = self.attrs['verbose']

            ce = to_dataframe(self.ce.rename({'m':'mkt'}),'i')

            se = estimation.bootstrap_elasticity_stderrs(ce,tol=tol,VERBOSE=VB)
            self['se_beta'] = from_dataframe(se)

        return self['se_beta']

    def anova(self):
        """Table analyzing variance of expenditures.
        """
        self.get_reduced_form()

        miss2nan = self.ce*0

        cehat = self.get_cehat()

        y = self.drop_useless_expenditures() # A dataframe

        df = pd.DataFrame({'Prices':to_dataframe(self.a.var(['t','m'],ddof=0)),
                          'Characteristics':to_dataframe(self.z.dot(self.delta.T).var(['j','t','m'],ddof=0)),
                          '$\log\lambda$':to_dataframe((self.cehat + miss2nan).var(['j','t','m'],ddof=0)),
                          'Residual':to_dataframe((self.ce-self.cehat).var(['j','t','m'],ddof=0))})

        df = df.div(y.var(ddof=0),axis=0)
        df['Total var'] = y.var(ddof=0)

        df.sort_values(by=r'$\log\lambda$',inplace=True,ascending=False)

        return df

    def get_predicted_log_expenditures(self):
        cehat = self.get_cehat()
        self['yhat'] = cehat + self.z.dot(self.delta) + self.a

        self['e'] = self.y - self.yhat

        return self.yhat

    def get_alpha(self):
        """Return log of alpha parameters.  These are determined by the first
        round of data on expenditures, and assumed equal across markets.
        """
        numeraire = self.numeraire
        if not is_none(self.alpha):
            return self.alpha
        elif numeraire is not None and np.any(self.logp[numeraire] != 0.):
            self.set_numeraire(numeraire=numeraire)

        if is_none(self.a):
            self.get_reduced_form()

        self['alpha'] = self.a.sel(t=self.firstround,drop=True).mean('m')
        self['se_alpha'] = np.sqrt((self.se_a.sel(t=self.firstround,drop=True)**2).sum('m'))/len(self.se_a.coords['m'])

        return self.alpha

    def set_numeraire(self,new_numeraire=None):
        """Set the numeraire, and adjust units for all relevant prices & expenditures.
        """
        # List of units (in logs) that need to be changed with change of numeraire; logp must be last
        change_logunits=['y','yhat','logp']

        # List of units in levels that need to be changed with change of numeraire; prices must be last
        change_units=['expenditures','price']

        if new_numeraire is not None:
            self.attrs['numeraire'] = new_numeraire

        if self.attrs['numeraire'] is None:
            raise ValueError('Must supply numeraire')
        else:
            numeraire = self.attrs['numeraire']

        try: # Levels
            pidx = self['prices'].sel(i=numeraire).copy()
            self['prices'] = self['prices']/pidx
        except (AttributeError,TypeError):
            pass

        try:
            pidx = self['logp'].sel(i=numeraire).copy()
            self['logp'] = self['logp'] - pidx
            self['y'] = self['y'] - pidx
            self['yhat'] = self.yhat - pidx
        except (AttributeError,TypeError):
            pass


    def set_barloglambda_t():
        # FIXME: Issue here with dividing by a random variable.  What
        # properties do we want estimator of barloglambda_t to have?
        try: 
            if not is_none(self.a) and not is_none(self.beta):
                self['barloglambda_t'] = -self.a.sel(i=numeraire)/self.beta.sel(i=numeraire)
                self['a'] = self.a - self.barloglambda_t
                self['loglambdas'] = self.loglambdas + self.barloglambda_t # Add term associated with numeraire good
            elif not is_none(self.prices):
                self['barloglambda_t'] = self.prices.mean('i').fillna(0)*0.

        except (AttributeError,TypeError):
            pass

    def resample_lambdas(self):
        """Resample self.loglambdas, producing a new object with preference
        parameters drawn from self and a measurement error process for
        expenditures which is log-normal.
        """
        d = self.dims
        S = np.random.randint(0,d['j'],size=d['j'])

        R = Result(data=self)

        foo = self.loglambdas.isel(j=S)
        foo.coords['j'] = self.loglambdas.coords['j']
        R['loglambdas'] =  foo + self.loglambdas*0.

        foo = self.z.isel(j=S)
        foo.coords['j'] = self.z.coords['j']

        R['z'] = foo
        R['characteristics'] = R.z

        R['cehat'] = R.loglambdas * R.beta

        # Retrieve mean & std of errors
        foo = (self.ce - self.cehat).to_dataframe('e').dropna()
        mu = foo.mean()
        sigma = foo.std()

        # Generate new errors lognormally distributed
        R['e'] = xr.DataArray(np.random.normal(loc=mu,scale=sigma,size=(d['j'],d['t'],d['m'],d['i'])),coords=R.ce.coords)

        # Add missings back in where appropriate
        foo = self.y.isel(j=S)
        foo.coords['j'] = self.z.coords['j']
        R['e'] = R['e'] + 0*foo

        R['ce'] = R.cehat + R.e

        R['yhat'] = R.cehat + R.z.dot(R.delta) + R.a

        R['y'] = R.yhat + R.e

        return R
# result_class ends here

# [[file:~/Research/CFEDemands/Empirics/cfe_estimation.org::result_to_file][result_to_file]]
# Tangled on Thu Jun  7 21:40:57 2018
    def to_dataset(self,fn=None):
        """Convert Result instance to xarray.Dataset."""
        D = xr.Dataset()
        for k in vars(self):
            v = self.__dict__[k]
            if type(v) in np.ScalarType or isinstance(v,dict):
                D.attrs[k] = v
            elif isinstance(v,pd.Series):
                D[k] = v.to_xarray()
            elif isinstance(v,pd.DataFrame):
                D[k] = v.stack().to_xarray()
            elif isinstance(v,pd.Panel):
                D[k] = v.to_frame().stack().to_xarray()
            elif isinstance(v,set):
                D[k] = tuple(v)
            elif v is None: pass
            else:
                print("Problem type: %s, %s" % (k,type(v)))

        if fn is not None:
            D.to_netcdf(fn)

        return D

    def to_pickle(self,fn):
        """Pickle Result instance in file fn."""
        import pickle

        d = self.to_dict()
        with open(fn,'wb') as f:
            pickle.dump(d,f)

        return d

def from_dataset(fn):
    """
    Read persistent netcdf (xarray.Dataset) file to Result.
    """

    D = xr.open_dataset(fn)

    R = Result(data=D)

    return R

def from_shelf(fn):
    import shelve

    with shelve.open(fn):
        pass

def from_pickle(fn):
    import xarray as xr
    import pickle

    with open(fn,'rb') as f:
        X = pickle.load(f)

    D = xr.Dataset.from_dict(X)

    R = Result(data=D)

    return R
# result_to_file ends here
