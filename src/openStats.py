'''
Created on 14/05/2012

@author: Sebastian Lopez Buritica
'''

from statlib import stats
from scipy import stats as stats2
import math
import numpy as np

def isnumeric(data):
    if isinstance(data, (int, float, long, np.ndarray)):
        return True
    return False

class statistics:
    def __init__(self, data, name= None, missing= None):
        if isnumeric(data) and not isinstance( data, (np.ndarray)):
            data= [data]
        self.missing=  missing
        self.Name=     name
        self.N=        len(data)
        self.suma=     sum(data)
        self.mean=     stats.mean(data)
        if len(data) > 1:
            self.variance= stats.var(data)
            self.stderr=   stats.sterr(data)
            self.stddev=    stats.stdev(data)
        else:
            self.variance= None
            self.stderr=   None
            self.stddev=   None
        self.sumsquares= stats.ss(data)
        self.minimum=  min(data)
        self.firstquartilescore= stats.firstquartilescore(data)
        self.thirdquartilescore= stats.thirdquartilescore(data)
        self.interquartilerange= self.thirdquartilescore - self.firstquartilescore
        self.maximum=  max(data)
        self.range=    self.maximum-self.minimum
        if any([dat < 0 for dat in data]):
            self.geomean=  None
        else:
            self.geomean=  stats.geometricmean(data)
        try:
            self.harmmean= stats.harmonicmean(data)
        except ZeroDivisionError:
            self.harmmean = None
        self.skewness=  stats.skew(data)
        self.kurtosis=  stats.kurtosis(data)
        self.median=    stats.median(data)
        
        self.samplevar= stats.samplevar(data)
        if self.mean !=0 and self.stddev != None:
            self.coeffvar= self.stddev/float(self.mean)
        else:
            self.coeffvar = None
        self.mode= stats.mode(data)[1][0]
        
def normProb( x, loc= 0, scale= 1):
    return stats2.norm(loc= loc, scale= scale).cdf(x)

def normProbInv( x, loc= 0, scale= 1):
    return stats2.norm(loc= loc, scale= scale).ppf(x)

def OneSampleTests(colData, tests, userMean):
    # detect the selected tests
    posible={'t-test':     False,
             'Sign Test':  False,
             'Chi square test for variance':False}
    
    for test in tests:
        if test in posible.keys():
            posible[test]= True
    
    # calculating descriptive statistics
    de= statistics(colData)
    result= list()
    # ttest= (t, 2 tailed prob)
    if posible['t-test']:
        ttest= stats.ttest_1samp( colData, userMean)
        result.append(ttest)
        
    def OneSampleSignTest(data1, usermean):
        """
        This method performs a single factor sign test. The data must be 
        supplied to this method along with a user hypothesised mean value.
        Usage: OneSampleSignTest(data1, usermean)
        Returns: nplus, nminus, z, prob.
        """
        nplus=0
        nminus=0
        for i in range(len(data1)):
            if (data1[i] < usermean):
                nplus+= 1
                
            if (data1[i] > usermean):
                nminus+= 1
                
        ntotal= nplus + nminus
        try:
            z= nplus- (ntotal/2)/ math.sqrt(ntotal/2)
        except ZeroDivisionError:
            z=     0
            prob= -1.0
        else:
            prob= stats.erfcc(abs(z) / 1.4142136)
        return (z, prob)
    #####
    def ChiSquareVariance(de, usermean):
        """
        This method performs a Chi Square test for the variance ratio.
        Usage: ChiSquareVariance(self, usermean)
        Returns: df, chisquare, prob
        """
        df = de.N - 1
        try:
            chisquare = (de.stderr / usermean) * df
        except ZeroDivisionError:
            chisquare = 0.0
        prob = stats.chisqprob( float(chisquare), df) 
        
        return (df, chisquare, prob)
    #####
    if posible['Sign Test']:
        oneSampleST= OneSampleSignTest( colData, userMean)
        result.append(oneSampleST)
        
    if posible['Chi square test for variance']:
        chisqtest= ChiSquareVariance( de, userMean)
        result.append(chisqtest)
    
    return result

def twoSampleTests(colData, tests, userMean):
    posible={'t-test':     False,
             'Sign Test':  False,
             'Chi square test for variance':False}
    
    for test in tests:
        if test in posible.keys():
            posible[test]= True
