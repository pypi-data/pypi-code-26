import pandas as _pd
import numpy as _np
from .load import Load
# from .model_selection import eta


class _datastruct:

    db = None

    def __parse_dict(self, data):

        for k, v in data:
            setattr(self, k, v)


class Dataset(_datastruct):

    def __init__(self, data_struct={}):

        # This raises AttributeError
        # self.SDF = None
        # self.SDE = None
        # self.CVF = None
        # self.CVE = None

        if 'obj_data' in data_struct:
            self.__parse_version1data(data_struct["obj_data"])

        elif isinstance(data_struct, dict):
            self.__parse_dict(data_struct)
        else:
            pass

        return

    def __parse_version1data(self, data):

        # self._loaded = True
        self._description = data["description"]
        names = _pd.Series(data["names"], name="node")
        names.name = "node"
        self._nodes = names
        M = data["M"]
        samples = _pd.Series(["S" + str(i + 1) for i in range(M)], name="sample")
        self.X = _pd.DataFrame(data["Y"], index=names, columns=samples).T
        self.P = _pd.DataFrame(data["P"], index=names, columns=samples).T
        self.E = _pd.DataFrame(data["E"], index=names, columns=samples).T
        self.F = _pd.DataFrame(data["F"], index=names, columns=samples).T

        self.__created__ = data["created"]
        self.s2 = _pd.Series(_np.array([_np.array(i) for i in data["lambda"]]), index=["E", "F"])
        self.name = data["dataset"]
        self.__model__ = data["network"]
        self.__model_eq__ = "X ~ -_np.dot(P, _np.linalg.pinv(A).T)"

        return

    @property
    def SDE(self):
        """Standard devation estimate of noise for each datapoint in Y"""
        if hasattr(self, "_Dataset__SDE"):
            SDE = self._Dataset__SDE
        else:
            SDE = _pd.DataFrame(_np.sqrt(self.s2["E"]), index=self.X.index, columns=self.X.columns)

        return SDE

    @property
    def SDF(self):
        """Standard devation estimate of noise for each datapoint in P"""
        if hasattr(self, "_Dataset__SDF"):
            SDF = self._Dataset__SDF
        else:
            SDF = _pd.DataFrame(_np.sqrt(self.s2["F"]), index=self.P.index, columns=self.P.columns)

        return SDF

    def _covFroms2(self, N, index):

        s2 = self.s2["E"]
        if isinstance(s2, float):
            cv = _np.repeat(s2, N)
        else:
            if s2.shape[0] < N:
                cv = _np.repeat(s2, N)
            else:
                cv = s2

        CV = _pd.DataFrame(_np.diag(cv), index=index, columns=index)

        return CV

    @property
    def CVE(self):
        """covariance matrix of the noise in Y, if non existing will create it from the variance s2 variable"""
        N = self.shape["X"][1]
        index = self._nodes
        if hasattr(self, "_Dataset__CVE"):
            CV = self._Dataset__CVE
        else:
            CV = self._covFroms2(N, index)

        return CV

    @property
    def CVF(self):
        """covariance matrix of the noise in P, if non existing will create it from the variance s2 variable"""
        N = self.shape["P"][1]
        index = self._nodes
        if hasattr(self, "_Dataset__CVF"):
            CV = self._Dataset__CVF

        else:
            CV = self._covFroms2(N, index)

        return CV

    def cov(self, of="s2"):

        if hasattr(self, "covY"):
            covY = self.covY
        else:
            if of == "s2":
                s2y = self.s2["E"]
                if s2y.shape[0] < self.X.shape[1]:
                    sdy = _np.repeat(s2y, self.X.shape[1])
                covY = _pd.DataFrame(_np.diag(sdy), index=self.X.columns, columns=self.X.columns)

        if hasattr(self, "covP"):
            covP = self.covP
        else:
            if of == "s2":
                s2p = self.s2["F"]
                if s2p.shape[0] < self.P.shape[1]:
                    sdp = _np.repeat(s2p, self.P.shape[1])
                covP = _pd.DataFrame(_np.diag(sdp), index=self.P.columns, columns=self.P.columns)

        return {"covY": covY, "covP": covP}

    def design_target(self):
        """Return data in format common to machine learning pipeline
        X, y = data.design_target()

        X : m × n data matrix with m samples and n variables
        y : m × p data matrix with m samples and p target values

        X, y in this space is defined as the transpose of the variables Y and P stored in the dataset.
        """

        return (self.X, self.P)

    @property
    def shape(self):

        S = {}
        if hasattr(self, "X"):
            SY = self.X.shape
            S["X"] = SY
        if hasattr(self, "P"):
            SP = self.P.shape
            S["P"] = SP

        return S

    @classmethod
    def load(cls, URI=None, db=None, **kwargs):

        if URI is None:
            URI = "N10/Nordling-ID1446937-D20150825-N10-E15-SNR3291-IDY15968.json"
            if db is None and cls.db is None:
                db = cls.get_db()
            else:
                db = cls.db

        loaded = Load(URI, db, **kwargs)

        if isinstance(loaded, list):
            return loaded
        else:
            return cls(loaded)

    @classmethod
    def set_defaults(cls, clear=False):

        if clear:
            cls.db = None
        else:
            cls.db = "https://bitbucket.org/api/2.0/repositories/sonnhammergrni/gs-datasets/src/master"

    @classmethod
    def get_db(cls):

        return "https://bitbucket.org/api/2.0/repositories/sonnhammergrni/gs-datasets/src/master"


class Model(_datastruct):

    def __init__(self, data_struct={}):

        if 'obj_data' in data_struct:
            self.__parse_version1data(data_struct["obj_data"])

        elif isinstance(data_struct, dict):
            self.__parse_dict(data_struct)
        else:
            pass

        return

    def __parse_version1data(self, data):

        # self._loaded = True
        self.name = data["network"]
        self.structure = data["network"].split("-")[2]
        self._description = data["description"]
        names = _pd.Series(data["names"], name="node")
        names.name = "node"
        names = names.apply(lambda x: x[0] + x[1:].zfill(2))
        self._nodes = names
        fr = names.copy()
        fr.name = "source"
        to = names.copy()
        to.name = "target"
        model_params = _pd.DataFrame(data["A"], index=to, columns=fr).T
        self.params = model_params.stack()[~(model_params.stack() == 0)]
        self.params.name = "value"
        self.__created__ = data["created"]

    @property
    def G(self):

        if not hasattr(self, '_Model__G'):
            G = -self.pinv()
            return _pd.DataFrame(G, index=self.A.index, columns=self.A.columns)
        else:
            return self._Model__G

    @G.setter
    def G(self, G):
        if isinstance(G, _pd.DataFrame):
            self.__G = G
        else:
            self.__G = _pd.DataFrame(G, index=self.A.index, columns=self.A.columns)

    @property
    def A(self):
        N = _np.prod(self.shape)

        if self.params.shape[0] < N * 0.34:
            return self.params.unstack(0).fillna(0).to_sparse(fill_value=0)
        else:
            return self.params.unstack(0).fillna(0)

        return

    def pinv(self, store=False, **kwargs):

        if not hasattr(self, '_Model__G'):
            G = _np.linalg.pinv(self.A, **kwargs)
            if store:
                self.G = -G
        else:
            if self._Model__G is None:
                G = _np.linalg.pinv(self.A, **kwargs)
                if store:
                    self.G = -G
            else:
                G = -self.G

        return G

    @property
    def shape(self):

        paramind = self.params.index
        N = tuple([max(i) + 1 for i in paramind.labels])

        return N

    @classmethod
    def load(cls, URI=None, db=None, **kwargs):

        if URI is None:
            URI = cls._get_ds()
            if db is None and cls.db is None:
                db = cls._get_db()
            else:
                db = cls.db

        loaded = Load(URI, db, **kwargs)

        if isinstance(loaded, list):
            return loaded
        else:
            return cls(loaded)

    @classmethod
    def set_defaults(cls, clear=False):

        if clear:
            cls.db = None
        else:
            cls.db = cls._get_db()

    @classmethod
    def _get_db(cls):

        return "https://bitbucket.org/api/2.0/repositories/sonnhammergrni/gs-networks/src/master"

    @classmethod
    def _get_ds(cls):

        return "random/N10/Nordling-D20100302-random-N10-L25-ID1446937.json"
