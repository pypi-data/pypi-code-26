import warnings
import functools

import numpy as np
import scipy.odr as odr
import matplotlib.pyplot as plt
import pandas as pd

from . import global_funcs
from . import global_enums


class XYFit(object):
    def __init__(self, data, fn, initialParams, paramNames = None, paramUnits = None, name = '', method = global_enums.FitMethods.ODR):
        self.data = data
        self.fn = fn
        self.initialParams = initialParams
        self.method = method
        self.name = ''

        xError = self.data.xError if np.count_nonzero(self.data.xError) != 0 else None
        yError = self.data.yError if np.count_nonzero(self.data.yError) != 0 else None

        self.fitObj = None
        self.fitParams = None
        self.fitParamsStdError = None
        self.reducedChi2 = None
        self.R2 = None

        if self.method == global_enums.FitMethods.ODR:
            Rdata = odr.RealData(self.data.x, self.data.y, xError, yError)
            self.fitObj = odr.ODR(Rdata, odr.Model(self.fn), self.initialParams).run()
        
            self.fitParams = self.fitObj.beta
            self.fitParamsStdError = self.fitObj.sd_beta

            #The following 2 lines raise warnings in pylint. The code is OK tough.
            self.reducedChi2 = self.fitObj.res_var #See http://mail.scipy.org/pipermail/scipy-user/2012-May/032207.html
            self.R2 = 1 - np.sum(self.fitObj.eps**2)/self.fitObj.sum_square if np.argwhere(np.array(self.fitObj.sd_beta) == 0).size == 0  else 1

        self.paramNames = ['$B_{' + str(i) + '}$' for i in range(len(self.fitParams))]
        if paramNames is not None:
            if len(paramNames) != len(self.fitParams):
                warnings.warn('len(paramsName) != len(fitParams): Default parameter names selected.')
            else:
                seen = set()
                flag = False
                for name in paramNames:
                    if name not in seen:
                        seen.add(name)
                    else:
                        flag = True
                if flag:
                    warnings.warn('Found repeated values in paramNames: Default parameter names selected.')
                else:
                    self.paramNames = paramNames
        self.paramUnits = paramUnits

    def getFitFn(self):
        return functools.partial(self.fn, self.fitParams)
    
    def quickPlot(self, plotType = global_enums.PlotType.ErrorBar, purgeStep = 1):
        if purgeStep <= 0:
            warnings.warn('purgeStep has to be at least 1. Setting purgeStep = 1.')
            purgeStep = 1
        fig , ax = plt.subplots(1,1)
        if plotType == global_enums.PlotType.ErrorBar:
            ax.errorbar(self.data.x[::purgeStep], self.data.y[::purgeStep], xerr = self.data.xError[::purgeStep], \
                        yerr = self.data.yError[::purgeStep], fmt = 's')
        elif plotType == global_enums.PlotType.Line:
            ax.plot(self.data.x[::purgeStep], self.data.y[::purgeStep], '-')
        elif plotType == global_enums.PlotType.Point:
            ax.plot(self.data.x[::purgeStep], self.data.y[::purgeStep], 's')

        x = np.linspace(self.data.x[0], self.data.x[-1], 1000)
        ax.plot(x, self.getFitFn()(x))

        ax.set_xlabel(self.data.xLabel if self.data.xUnits is None else self.data.xLabel + ' (' + self.data.xUnits + ')')
        ax.set_ylabel(self.data.yLabel if self.data.yUnits is None else self.data.yLabel + ' (' + self.data.yUnits + ')')
        ax.set_title(self.data.name)
        return fig, ax

    def dataFrame(self, rounded = True, separatedError = False, relativeError = False, transpose = False, saveCSVFile = None, CSVSep = ',', CSVDecimal = '.'):
        perrors = [global_funcs.roundToFirstSignifficantDigit(x) for x in self.fitParamsStdError] if rounded else self.fitParamsStdError
        pvalues = [global_funcs.roundToError(self.fitParams[i], perrors[i]) for i in range(len(self.fitParams))] if rounded else self.fitParams
        
        R2col = [np.round(self.R2, 5)]
        rowNames = ['B']
        if separatedError:
            rowNames += ['$\\Delta B$']
            R2col += ['-']
        if relativeError:
            rowNames += ['$\\Delta B$ (rel)']
            R2col += ['-']
        rowNames += ['$B_0$']
        R2col += ['-']
        
        colNames = []
        if self.paramUnits is not None:
            colNames = [self.paramNames[i] + ' (' + self.paramUnits[i] + ')' if self.paramUnits[i] != '' \
                        else self.paramNames[i] for i in range(len(self.paramNames))]
        else:
            colNames = self.paramNames
        colNames.append('$R^2$')
        
        tblCols = {}
        for i in range(len(pvalues)):
            if relativeError:
                relError = perrors[i]/pvalues[i] if pvalues[i] != 0 else '-'
                if separatedError:
                    tblCols[colNames[i]] = [pvalues[i], perrors[i], relError, self.initialParams[i]]
                else:
                    tblCols[colNames[i]] = [str(pvalues[i]) + ' $\\pm$ ' + str(perrors[i]), relError, self.initialParams[i]]
            else:
                if separatedError:
                    tblCols[colNames[i]] = [pvalues[i], perrors[i], self.initialParams[i]]
                else:
                    tblCols[colNames[i]] = [str(pvalues[i]) + ' $\\pm$ ' + str(perrors[i]), self.initialParams[i]]
                    
        tblCols['$R^2$'] = R2col
        
        table = pd.DataFrame(tblCols, columns = colNames, index = rowNames)
        table = table.T if transpose else table
        
        if saveCSVFile is not None:
            table.to_csv(saveCSVFile, sep = CSVSep, decimal = CSVDecimal)
        
        return table

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#External functions:

def reportManyFits(fitList, fitNames = None, rounded = True, separatedError = False, relativeError = False, saveCSVFile = None, CSVSep = ',', CSVDecimal = '.'):
    paramNumber = len(fitList[0].fitParams)
    for i in range(len(fitList)):
        if len(fitList[i].fitParams) != paramNumber:
            warnings.warn('fit[' + str(i) + '] in fitList has different number of fitted parameters.')
            return None
    
    if fitNames is None:
        flag = False
        for fit in fitList:
            if fit.name != '' or fit.data.name != '':
                flag = True
        if flag:
            fitNames = []
            for fit in fitList:
                name = fit.data.name
                if name != '':
                    name += ' - '
                name += fit.name #if fit.name == '', won't change name.
                #worst case: name == ''
                fitNames += [name]
    elif len(fitNames) != len(fitList):
        warnings.warn('len(fitNames) != len(fitList): Fit names removed from table.')
        fitNames = None
    
    rows = []
    for index in range(len(fitList)):
        fit = fitList[index]

        perrors = [roundToFirstSignifficantDigit(x) for x in fit.fitParamsStdError] if rounded else fit.fitParamsStdError
        pvalues = [roundToError(fit.fitParams[i], perrors[i]) for i in range(len(fit.fitParams))] if rounded else fit.fitParams

        columns = []
        if fitNames is not None:
            columns += [fitNames[index]]

        for i in range(len(pvalues)):
            if separatedError:
                columns += [pvalues[i], perrors[i]]
            else:
                columns += [str(pvalues[i]) + ' $\\pm$ ' + str(perrors[i])]
            if relativeError:
                columns += [perrors[i]/pvalues[i]if pvalues[i] != 0 else '-']
        
        columns += [np.round(fit.R2, 5)]
        
        rows += [columns]
    
    colNames = ['Name'] if fitNames is not None else []
    
    paramNames = []
    if fitList[0].paramUnits is not None:
        paramNames = [fitList[0].paramNames[i] + ' (' + fitList[0].paramUnits[i] + ')' if fitList[0].paramNames[i] != '' \
                        else fitList[0].paramNames[i] for i in range(len(fitList[0].paramNames))]
    else:
        paramNames = fitList[0].paramNames
    
    for i in range(len(paramNames)):
        colNames += [paramNames[i]]
        if separatedError:
            colNames += ['$\\Delta$ ' + paramNames[i]]
        if relativeError:
            colNames += ['$\\Delta$ ' + fitList[0].paramNames[i] + ' (rel)']
    
    colNames += ['$R^2$']

    table = pd.DataFrame(rows, columns = colNames)
        
    if saveCSVFile is not None:
        table.to_csv(saveCSVFile, sep = CSVSep, decimal = CSVDecimal)
    
    return table
