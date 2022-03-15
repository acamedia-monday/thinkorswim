import datetime as dt
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import norm

class Portfolio_Model():
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
