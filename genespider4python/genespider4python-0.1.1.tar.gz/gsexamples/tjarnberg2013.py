import pandas as pd
import numpy as np
from gspy import data as gsd
from gspy import model_selection as gsms
from gspy import linear_model as gslm
import sklearn.metrics as metrics
from sklearn.linear_model import Lasso
# from sklearn.preprocessing import StandardScaler


def load_data(netpath="gs_networks/random/N10/", datapath="gs_datasets/N10/"):

    network = "Nordling-D20100302-random-N10-L25-ID1446937.json"
    net = gsd.Model.load(network, netpath)
    datasets = gsd.Dataset.load(datapath, wildcard="Nordling-*")

    dataset = {}
    for d in datasets:
        data = gsd.Dataset.load(d)
        dataset[data.name] = data

    return net, dataset


def infer_networks(dataset, zetavec=np.logspace(-6, 0, num=100), **kwargs):

    for name, data in dataset.items():

        if name == "Nordling-ID1446937-D20150825-N10-E20-SNR16783-IDY15818":
            X, Y = data.design_target()

            iters = fit_methods(X, -Y, zetavec, method=Lasso, **kwargs)

            return iters


def fit_methods(X, Y, zetavec, method=Lasso, **kwargs):

    for cv, (train, test) in enumerate(gsms.cv_filter_splitter(X, Y)):

        X_train, Y_train = X.iloc[train], Y.iloc[train]
        X_test, Y_test = X.iloc[test], Y.iloc[test]

        for y in Y_train:

            for z in zetavec:

                yt = Y_train[y]
                yv = Y_test[y]
                lsf = method(warm_start=True, **kwargs)
                lsf.set_params(alpha=z)
                lsf.fit(X_train, -yt)

                y_pred = lsf.predict(X_test)
                mse = metrics.mean_squared_error(-yv, y_pred)
                q2 = metrics.r2_score(-yv, y_pred)

                y_pred = lsf.predict(X_train)
                r2 = metrics.r2_score(-yt, y_pred)

                yield y, cv, lsf, mse, q2, r2


def fit_method(X, Y, docv=True, method=Lasso, **kwargs):

    if docv:
        for cv, (train, test) in enumerate(gsms.cv_filter_splitter(X, Y)):

            X_train, Y_train = X.iloc[train], Y.iloc[train]
            # X_test, Y_test = X.iloc[test], Y.iloc[test]

            yield from fit_variable(X_train, Y_train, method=method, warm_start=True, cv=cv, **kwargs)
    else:

        yield from fit_variable(X, Y, method=method, warm_start=True, **kwargs)


def fit_variable(X, Y, **kwargs):

    for v in Y:
        y = Y[v]
        yield from penalize(X, y, **kwargs)


def penalize(X, y, zetavec=np.logspace(-6, 0, num=100), method=Lasso, cv=0, **kwargs):

    for z in zetavec:

        mth = method(**kwargs)
        mth.set_params(alpha=z)
        mth.fit(X, y)

        # y_pred = lsf.predict(X)
        # r2 = metrics.r2_score(-y, y_pred)

        # y_pred = lsf.predict(X_test)
        # mse = metrics.mean_squared_error(-Y_test[y], y_pred)
        # q2 = metrics.r2_score(-Y_test[y], y_pred)
        # cv = yield z

        yield mth, y.name, cv


def Tjarnberg2013():

    net, datasets = load_data()

    infer_networks(datasets)


if __name__ == '__main__':

    Tjarnberg2013()
