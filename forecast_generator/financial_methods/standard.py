import os
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'Moro.settings'
django.setup()
import pandas as pd
import numpy as np
from decimal import *
from dateutil.relativedelta import *
from x_returns import xnpv, xirr

def duplicator_check(data_set):
    if len(data_set) == 1:
        return data_set[0]
    else:
        for item in data_set:
            print(item.id , ' | ', item.category, ' | ' , item.amount, ' | ', item.created)
        keeper = int(input('Which of the above would you like to keep? '))
        for item in data_set:
            if item.id != keeper:
                item.data_status = 'Archived'
                item.save()
            else:
                target = item
        return target

def project_value_adjustor(investment, financial_solution, projects):
    adjusted_value = 0

    if investment.project_set.filter(project_status='Active').exists():
        for project in investment.project_set.filter(project_status='Active'):
            dev_fee_set = project.projectrevenuestracker_set.filter(category='Dev Fee').filter(data_status='Active')
            dev_fee_obj = duplicator_check(dev_fee_set)
            dev_fee = dev_fee_obj.amount
            p_total_value = (dev_fee * 1000000) * project.capacity
            project.tot_value = p_total_value
            project.save()
            adjusted_value += p_total_value * project.risk_adj

        return adjusted_value
    else:
        adjusted_value += investment.tot_value * financial_solution.risk_adj
        return adjusted_value

def disposition_dates(close_date, ntp_delta, cod_delta, random=True):
    if not random:
        ntp = close_date + relativedelta(months=+ntp_delta)
        cod = ntp + relativedelta(months=+cod_delta)
        
        return ntp, cod
    
    else:
        ntp = close_date + relativedelta(months=+np.random.randint(6, ntp_delta))
        cod = ntp + relativedelta(months=+np.random.randint(6, cod_delta))

        return ntp, cod


def interest_calc(period, t, interest_rate, p_bop, p_eop, pik):
    interest = interest_rate * Decimal((int(t.day) / 365)) * Decimal(((p_bop + p_eop) / 2))

    uncapped_interest = pik
    if (period + 1) % 3 != 0:
        pik += interest
        return interest, pik, p_eop
    else:
        capped_interest = pik + interest
        p_eop += capped_interest
        pik = 0
        return interest, uncapped_interest, capped_interest, pik, p_eop

def origination_fee_calc(period, principle, orig_fee):
    if period == 0:
        origination_fee = principle * orig_fee
        return origination_fee
    return 0

def com_fee_calc(period, principle, comm_fee):
    if period == 0:
        com_fee = principle * comm_fee
        return com_fee
    else:
        return 0

def fin_fee_calc(fin_fee, p_eop):
    fin_fee = fin_fee * p_eop
    return fin_fee

def draw_calculation(period, t, facility, investment, draw_number=0, manual=False, draw_schedule=False):
    # Draw schedule of type {Draws: [{interval: date, value: float}]}
    draw = 0
    if not manual:
        if period < draw_number:
            draw += -facility / draw_number
            return Decimal(draw)
        return Decimal(draw)
    else:
        if draw_schedule:
            projects = investment.project_set.filter(status='Active')
            for d in projects.draw_set.filter(data_status='Active').filter(date__icontains=t.year).filter(date__icontains=t.month):
                draw += d.amount
            if draw <= facility:
                return Decimal(draw)
            elif draw > facility:
                return Decimal(-facility)

def draw_calculation_v2(period, t, facility, investment, draw_number=0, manual=False, draw_schedule=False):
    # Draw schedule of type {Draws: [{interval: date, value: float}]}
    draw = 0
    if not manual:
        if period < draw_number:
            draw += -facility / draw_number
            return Decimal(draw)
        return Decimal(draw)
    else:
        if draw_schedule:
            projects = investment.project_set.filter(status='Active')
            project_draws = projects.draw_set.filter(data_status='Active').filter(date__contains=t.year).filter(date__contains=t.month)
            wc_draws = investment.draw_set.filter(status='Active').filter(date__contains=t.year).filter(date__contains=t.month)
            for pd in project_draws:
                draw += pd.amount
            for wcd in wc_draws:
                draw += wcd.amount
            if draw <= facility:
                return Decimal(draw)
            elif draw > facility:
                return Decimal(-facility)

def draw_calc(period, facility, draw_number=0, manual=False, draw_schedule=None):
    # Draw schedule of type {Draws: [{interval: date, value: float}]}
    draw = 0
    if not manual:
        if period < draw_number:
            draw += -facility / draw_number
            return Decimal(draw)
        return Decimal(draw)
    else:
        if draw_schedule:
            try:
                draw_request = draw_schedule['Draws'][period]['value']
                if draw_request <= facility:
                    draw += -draw_request
                    return Decimal(draw)
                elif draw_request > facility:
                    return Decimal(-facility)
            except IndexError:
                draw += 0
            return Decimal(draw)
        return Decimal(draw)

def draw_revolver_calc(period, term, facility, draw_number=1, manual=False, draw_schedule=None):
    draw = 0
    if not manual:
        if period < draw_number:
            draw += -facility / draw_number
            return draw
        else:
            if facility > 0 and len(period) < term - 3:
                return -facility
            return draw
    else:
        if draw_schedule:
            try:
                draw_request = draw_schedule['Draws'][period]['value']
                if draw_request <= facility:
                    draw += -draw_request
                    return draw
                elif draw_request > facility:
                    return -facility
            except IndexError:
                if facility > 0:
                    return -facility
        return draw

def collateral_value_t(t, collateral, maturity):
    # Project dispositions and future cashflows can be collateralized against draws assuming:
    # 1. Disposition event of projects in pipeline occur before the maturity date of the loan
    # 2. Project cashflow in time series start at or before the moment in time the cashflow value is to be compared
    # against requested draws
    if collateral.guarantee_value:
        return collateral.guarantee_value
    elif collateral.capacity and collateral.disposition_unit_value:
        value = collateral.capacity * collateral.disposition_unit_value * collateral.discount_rate
        # NPV of delta between t and anticpated NTP & COD
        limit = pd.date_range(t, maturity, freq='MS').tolist()
        limit_num = len(limit)
        ntp_delta = pd.date_range(t, collateral.ntp, freq='MS').tolist()
        cod_delta = pd.date_range(t, collateral.cod, freq='MS').tolist()
        financial_series = {'Net': [], 'Dates': []}

        for i in range(limit_num):
            net = 0
            try:
                if limit[i].year == ntp_delta[i].year and limit[i].month == ntp_delta[i].month:
                    net += value * collateral.ntp_value
            except IndexError:
                net += 0

            try:
                if limit[i].year == cod_delta[i].year and limit[i].month == cod_delta[i].month:
                    net += value * collateral.cod_value
            except IndexError:
                net += 0

            financial_series['Net'].append(net)
            financial_series['Date'].append(t)
            t += relativedelta(months=+1)

        return calc_npv(financial_series)

    elif collateral.cashflow_series:
        # Right size the cashflow series of type {Revenues: [{interval: date, value: $}]} and run through xnpv with t as
        # d0. Would require checking that cashflow series ends after t
        # Also relies on determining the delta between the beginning of the cashflow series and t in the interest of
        # properly indexing the starting point for the npv calculation
        financial_series = {'Net': [], 'Dates': []}
        if collateral.cashflow_series['Revenues'][-1]['interval'] > t:
            # Mathematical determination of index based on date differentials
            cash_periods = len(collateral.cashflow_series['Revenues'])
            delta = len(pd.date_range(t, collateral.cashflow_series['Revenues'][-1]['interval'], freq='MS').tolist())
            starting_cash_index = cash_periods - delta
            for i in range(starting_cash_index - 1, cash_periods):
                financial_series['Net'].append(collateral.cashflow_series['Revenues'][i]['value'])
                financial_series['Date'].append(collateral.cashflow_series['Revenues'][i]['interval'])

            return calc_npv(financial_series)
        else:
            return 0

def draw_collateralized(t, investment, financial_solution):
    cash_collateral = 0

    for collateral in investment.collateral_set.all():
        cash_collateral += collateral_value_t(t, collateral, financial_solution.maturity_date)

    return cash_collateral

def disposition_calc(t, investment, fin_solution, adjusted_value, projects):
    incentive = 0
    closing_proceed = False
    ntp_proceed = False
    cod_proceed = False

    if t.year == fin_solution.closing_date.year and t.month == fin_solution.closing_date.month:
        closing_proceed = True
        incentive += (adjusted_value * fin_solution.acquisition_closing_earn * fin_solution.ci)
    if projects:
        for project in investment.project_set.filter(project_status='Active'):
            if t.year == project.ntp.year and t.month == project.ntp.month:
                ntp_proceed = True
                incentive += (project.tot_value * fin_solution.ntp_earn * fin_solution.ci)
            elif t.year == project.cod.year and t.month == project.cod.month:
                cod_proceed = True
                incentive += (project.tot_value * fin_solution.cod_earn * fin_solution.ci)

        return incentive, closing_proceed, ntp_proceed, cod_proceed
    
    else:
        if t.year == fin_solution.ntp.year and t.month == fin_solution.ntp.month:
            ntp_proceed = True
            incentive += (adjusted_value * fin_solution.ntp_earn * fin_solution.ci)
        elif t.year == fin_solution.cod.year and t.month == fin_solution.cod.month:
            cod_proceed = True
            incentive += (adjusted_value * fin_solution.cod_earn * fin_solution.ci)

        return incentive, closing_proceed, ntp_proceed, cod_proceed


def waterfall_disposition_calc(t, investment, financial_solution, waterfall, projects):
    cashflow = 0
    # closing_proceed = False
    ntp_proceed = False
    cod_proceed = False

    if projects:
        for project in investment.project_set.filter(project_status='Active'):
            if t.year == project.ntp.year and t.month == project.ntp.month:
                ntp_proceed = True
                cashflow += (project.tot_value * project.risk_adj * waterfall.ntp_cut)
            elif t.year == project.cod.year and t.month == project.cod.month:
                cod_proceed = True
                cashflow += (project.tot_value * project.risk_adj * waterfall.cod_cut)
        
        return cashflow, ntp_proceed, cod_proceed
    
    else:
        if t.year == investment.ntp.year and t.month == investment.ntp.month:
            ntp_proceed = True
            cashflow += (investment.tot_value * financial_solution.risk_adj * financial_solution.ntp_earn)
        elif t.year == investment.cod.year and t.month == investment.cod.month:
            cod_proceed = True
            cashflow += (investment.tot_value * financial_solution.risk_adj * financial_solution.cod_earn)

        return cashflow, ntp_proceed, cod_proceed

def waterfall_noncash_calc(waterfall, p_eop, hurdle, hurdle_bar, sweep_rate, cashflow):
    ci = 0
    repayment = 0
    sweep = 0

    cashflow -= (cashflow * waterfall.priority_cut)

    if hurdle < hurdle_bar:
        add_return = (p_eop * hurdle_bar)
        sweep += min(sweep_rate * cashflow, add_return)

        applied_principle = p_eop - sweep

        if p_eop > float(0) >= applied_principle:
            repayment += -p_eop
            # p_eop += repayment
            # The difference between what is outstanding principle and the cash to sweep in this cycle is incentive fee (repayment is)
            ci += (sweep + repayment)
        elif p_eop <= float(0):
            ci += sweep
        elif applied_principle > float(0):
            repay = -sweep
            repayment += repay
            # p_eop += repay

    return ci, repayment, -sweep

def extension_calc(period):
    pass

def right_size(inflow, outflow, net):
    r_size = {'Inflows': [], 'Outflows': [], 'Net': [], 'Dates': []}
    cycle = range(len(inflow))

    for i in cycle:
        r_size['Inflows'].append(inflow[i][1])
        r_size['Outflows'].append(outflow[i][1])
        r_size['Net'].append(net[i][1])
        r_size['Dates'].append(net[i][2])

    return r_size

def calc_irr(financial_data):
    irr = xirr(financial_data['Net'], financial_data['Dates'])
    return irr

def calc_moic(financial_data):
    moic = (-sum(financial_data['Inflows']) / sum(financial_data['Outflows']))
    return moic

def calc_npv(financial_data):
    npv = xnpv(.12, financial_data['Net'], financial_data['Dates'])
    return npv

if __name__ == '__main__':
    pass