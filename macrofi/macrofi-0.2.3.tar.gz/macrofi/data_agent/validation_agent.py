# 估值模型
from datetime import datetime
from sklearn import linear_model
from pyfi import WindHelper


def licha(begin_date, end_date):
    """10-1利差"""
    df = WindHelper.edb(codes=["gz10y", "gk10y", "gz1y", "gk1y"], begin_date=begin_date, end_date=end_date)
    licha = 0.5*(df["gz10y"] - df["gz1y"]) + 0.5*(df["gk10y"]-df["gk1y"])
    return licha.dropna()


def val_spread(begin_date, end_date):
    """CPI和PPI月度拟合模型和实际收益率之差
    Y - estimator(Y)
    """
    return None


def case1():
    begin_date = datetime(2008, 1, 1)
    end_date = datetime(2013, 9, 1)
    df = WindHelper.edb(codes=["gz1y", "gz10y"], begin_date=begin_date, end_date=end_date)
    df.loc[:, "10_1y"] = df.loc[:, "gz10y"] - df.loc[:, "gz1y"]
    df.reset_index(inplace=True)
    df2 = df[["gz1y", "10_1y"]].dropna()
    lm = linear_model.LinearRegression()
    lm.fit(df2[["gz1y"]], df2[["10_1y"]])
    beta = lm.coef_[0][0]
    alpha = lm.intercept_[0]
    df2.loc[:, "diff"] = df2.loc[:, "10_1y"] - df.loc[:, "gz1y"] * beta - alpha


def case2():
    begin_date = datetime(2008, 1, 1)
    end_date = datetime(2013, 9, 1)
    print(licha(begin_date, end_date))


if __name__ == "__main__":
    case2()
