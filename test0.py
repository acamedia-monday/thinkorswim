import datetime as dt
from dateutil.relativedelta import relativedelta
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import norm

class Pricer():
    opt = {'t':dt.date(2022,6,17),'r':.01,'vol':.3,'csize':1,'cval':114.213,'margin':5732.86}
    trade = {'dir':'sell','stop':20,'expos':-100000.0}
    bc = np.busdaycalendar(holidays=['2022-01-07','2022-02-23','2022-03-08','2022-05-02','2022-05-09','2022-11-04'])
    size = None
    ladder = None
    
    # Function returns both dirty and clean prices of the OFZ 26233 issue.
    def get_bond_price(self, yld=.20):
        bond = pd.DataFrame({'date':['2022-02-02','2022-08-03','2023-02-01','2023-08-02','2024-01-31','2024-07-31',
                                     '2025-01-29','2025-07-30','2026-01-28','2026-07-29','2027-01-27','2027-07-28',
                                     '2028-01-26','2028-07-26','2029-01-24','2029-07-25','2030-01-23','2030-07-24',
                                     '2031-01-22','2031-07-23','2032-01-21','2032-07-21','2033-01-19','2033-07-20',
                                     '2034-01-18','2034-07-19','2035-01-17','2035-07-18']})
        px_date=dt.date.today()
        bond_coupon = 30.42
        bond_par = 1000.00
        bond.index = pd.to_datetime(bond['date'], format='%Y-%m-%d')
        last_coupon_dt = bond.index[bond.index.date<=px_date].max().date()
        next_coupon_dt = bond.index[bond.index.date>px_date].min().date()
        accrued = bond_coupon*(px_date - last_coupon_dt).days/(next_coupon_dt - last_coupon_dt).days
        bond = bond.loc[bond.index.date>px_date,]
        bond['flow'] = [bond_coupon for i in range(bond.count()[0])]
        bond.iloc[bond.count()[0]-1,1] = bond.iloc[bond.count()[0]-1,1]+bond_par
        for i in bond.index: bond.loc[i,'date'] = (i.date()-px_date).days/365
        bond['date'] = bond['date'].astype(float)
        bond['discounted'] = bond['flow']*np.power(1+yld,-bond['date'])
        print('Gross bond price is {gross}'.format(gross=bond['discounted'].sum()))
        print('Clean bond price is {clean}'.format(clean=bond['discounted'].sum()-accrued))

    # Function returns option deltas and gammas according to the Black Scholes model.
    def get_greeks(self, stock=100, strike=120):
        if self.size is None:
            item = 11
            self.ladder = pd.DataFrame([0.0]*item, columns=['size'])
        else:
            item = len(self.size)
            self.ladder = pd.DataFrame(self.size, columns=['size'])
        self.ladder['stock'] = np.linspace(stock,strike,item)
        next_year = dt.date.today() + relativedelta(years=1)
        f_date = self.opt['t'] - relativedelta(days=7)
        wdays = np.busday_count(dt.date.today().strftime('%Y-%m-%d'), next_year.strftime('%Y-%m-%d'),
                                busdaycal=self.bc)
        t = np.busday_count(f_date.strftime('%Y-%m-%d'), self.opt['t'].strftime('%Y-%m-%d'),
                            busdaycal=self.bc)/wdays
        d1 = np.log(np.array(self.ladder['stock'])/strike)+(self.opt['r']+self.opt['vol']**2/2)*t
        self.ladder['delta'] = norm.cdf(d1/(self.opt['vol']*np.sqrt(t)))
        if strike>stock:
            if self.trade['dir'] == 'sell': self.ladder['delta'] = -self.ladder['delta']
        else:
            self.ladder['delta'] = self.ladder['delta'] - 1
            if self.trade['dir'] == 'sell': self.ladder['delta'] = -self.ladder['delta']
        self.ladder['gamma'] = self.ladder['delta'] - self.ladder['delta'].shift(1)
        self.ladder.loc[self.ladder['gamma'].isna(), 'gamma'] = self.ladder['delta']
    
    # Function returns the ladder with gamma-sized position entries.
    def get_ladder(self, multi=1):
        self.ladder['multi'] = multi
        if self.size is None: self.ladder['size'] = self.ladder['gamma']*self.ladder['multi']
        self.ladder['cumsize'] = self.ladder['size'].cumsum(skipna=True)
        self.ladder['val'] = self.ladder['stock']*self.ladder['size']*self.opt['csize']*self.opt['cval']
        self.ladder['val'] = self.ladder['val'].round(decimals=5)
        self.ladder['cumval'] = self.ladder['val'].cumsum(skipna=True)
        self.ladder['cumval'] = self.ladder['cumval'].round(decimals=5)
        self.ladder['avg'] = self.ladder['cumval']/(self.ladder['delta']*self.ladder['multi']*self.opt['csize']*self.opt['cval'])
        self.ladder['stop'] = self.ladder['stock']-self.trade['stop']
        self.ladder.loc[self.ladder['delta']<0,'stop'] = self.ladder['stock']+self.trade['stop']
        self.ladder['loss'] = self.ladder['stop']*self.ladder['cumsize']*self.opt['csize']*self.opt['cval']
        self.ladder['loss'] = self.ladder['loss'].round(decimals=5)
        self.ladder['loss'] = self.ladder['loss']-self.ladder['cumval']
        self.ladder['margin'] = -abs(self.ladder['cumsize'])*self.opt['margin']
        self.ladder['expos'] = self.ladder['loss']+self.ladder['margin']
        
    def pricer(self):
        multi = 1.0
        multi_p = 1.0
        epsi = .01
        approx = True
        proxy_p = 0.0
        self.get_greeks(stock=1.09, strike=1.05)
        self.get_ladder(multi)
