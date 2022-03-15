import datetime as dt
from dateutil.relativedelta import relativedelta
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import norm

class Pricer():
    opt = {'type':'call','t':dt.date(2022,6,17),'r':.01,'vol':.3}
    bc = np.busdaycalendar(holidays=['2022-01-07','2022-02-23','2022-03-08','2022-05-02','2022-05-09','2022-11-04'])
    spec = {'csize':1,'cval':114.213,'margin':5732.86}
    
    # Function returns option delta according to the Black Scholes model.
    def get_delta(self, stock=100, strike=100):
        next_year = dt.date.today() + relativedelta(years=1)
        f_date = self.opt['t'] - relativedelta(days=7)
        wdays = np.busday_count(dt.date.today().strftime('%Y-%m-%d'), next_year.strftime('%Y-%m-%d'),
                                busdaycal=self.bc)
        t = np.busday_count(f_date.strftime('%Y-%m-%d'), self.opt['t'].strftime('%Y-%m-%d'),
                            busdaycal=self.bc)/wdays
        d1 = np.log(np.array(stock)/strike)+(self.opt['r']+self.opt['vol']**2/2)*t
        d1 = norm.cdf(d1/(self.opt['vol']*np.sqrt(t)))
        if self.opt['type'] == 'put': d1 = d1-1
        return d1
    
    def get_ladder(self, s_start=100, s_end=100):
        ladder = pd.DataFrame(np.linspace(s_start,s_end,11),columns=['stock'])
        ladder['delta'] = self.get_delta(ladder['stock'], s_end)
        ladder['gamma'] = ladder['delta'] - ladder['delta'].shift(1)
        ladder.loc[ladder['gamma'].isna(), 'gamma'] = ladder['delta']
        return ladder

        def get_bond_price(my=.20):
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
        bond['discounted'] = bond['flow']*np.power(1+my,-bond['date'])
        print('Gross bond price is {gross}'.format(gross=bond['discounted'].sum()))
        print('Clean bond price is {clean}'.format(clean=bond['discounted'].sum()-accrued))
