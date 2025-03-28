import os
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'Moro.settings'
django.setup()
from decimal import *
from dateutil.relativedelta import *
import calendar
# import xirr.math as xer
from .standard import *
from forecast_generator.models import ClassicData, ReturnsModelData

def returns_model(investment, financial_io, filter_status, adjusted_status, target_status,
                  projection_source, waterfall=None, sweep_gates=3, projects=False, manual_draw=False):
    for rmd in financial_io.returnsmodeldata_set.filter(data_status=filter_status):
        rmd.data_status = adjusted_status
        rmd.save()
    # Following line should be under consideration for an automated financial solution within randomization tolerances (for theoretical projection information)
    t = financial_io.closing_date
    principal = financial_io.facility_size * financial_io.draw_utilization

    inflows = []
    outflows = []
    net = []

    xirr_tester = {'values': [], 'dates':[]}

    adjusted_value = project_value_adjustor(investment, financial_io, projects)

    financialSeries = {
        'irr': {}, 'moic': {}, 'npv': {}, 'margin': {}
    }

    periods = range(0, financial_io.term + 1)
    p = 0
    pik = 0
    hurdle = 0

    for period in periods:
        days_in_month = calendar.monthrange(t.year, t.month)
        now = t.strftime('%m/%d/%Y')
        n = f"{t.month}/{days_in_month}/{t.year}"
        # proForma['colList'].append(str(now))

        p_bop = p

        com_fee = com_fee_calc(period, principal, financial_io.commitment_fee)
        p += com_fee

        draw = draw_calculation(period, t, principal, draw_number=financial_io.draw_num, manual=manual_draw)
        principal = principal - draw
        outflows.append([now, draw, t])
        p += -draw

        incentive = 0
        repayment = 0
        cashflow = 0
        if not waterfall:
            ci, closing_p, ntp_p, cod_p = disposition_calc(t, investment, financial_io, adjusted_value, projects)
            incentive += ci
        elif waterfall:
            closing_p = False
            cf, ntp_p, cod_p = waterfall_disposition_calc(t, investment, financial_io, waterfall, projects)
            cashflow += cf

            counter = 1

            while cashflow > 0 and counter <= sweep_gates:
                hurdle_num = 'hurdle_' + str(counter)
                sweep_num = 'sweep_' + str(counter)
                try:
                    waterfall_hurdle = getattr(waterfall, hurdle_num)
                    waterfall_sweep = getattr(waterfall, sweep_num)

                    ci_add, repayment_add, cashflow_reduction = waterfall_noncash_calc(
                    waterfall, p, hurdle, waterfall_hurdle, waterfall_sweep, cashflow
                    )

                    fin_fee = fin_fee_calc(financial_io.financing_fee, p)
                    incentive += ci_add
                    repayment += repayment_add
                    cashflow -= cashflow_reduction
                    if counter == 1:
                        inflows.append([now, fin_fee + incentive + -repayment, t])
                        net.append([now, inflows[-1][1] + outflows[-1][1], t])
                    else:
                        inflows[-1] = [now, fin_fee + incentive + -repayment, t]
                        net[-1] = [now, inflows[-1][1] + outflows[-1][1], t]

                    finSeries = right_size(inflows, outflows, net)
                    hurdle += -hurdle
                    hurdle += calc_moic(finSeries)

                    counter += 1
                except AttributeError:
                    break
        
        maturity_repayment = False
        if t.month == financial_io.maturity_date.month and t.year == financial_io.maturity_date.year:
            maturity_repayment = True
            repayment += -p
            p += repayment

        # Because PIK relies on principle balance at the end of the period, interest calculation should be absolute last
        # in the HLT calc?
        interest, uncapped_interest, capped_interest, pik_new, p_eop = interest_calc(period, t, financial_io.interest_rate, p_bop, p, pik)
        fin_fee = fin_fee_calc(financial_io.financing_fee, p)

        interest_monthly = interest
        uncapitalized_interest = uncapped_interest
        capitalized_interest = capped_interest
        pik = pik_new
        p = p_eop

        inflows.append([now, Decimal(fin_fee + incentive + -repayment), t])
        net.append([now, Decimal(inflows[-1][1] + outflows[-1][1]), t])

        fin_series_t = right_size(inflows, outflows, net)

        moic_t = calc_moic(fin_series_t)
        npv_t = calc_npv(fin_series_t)

        financialSeries['moic'][str(now)] = float(moic_t)
        financialSeries['npv'][str(now)] = float(npv_t)
        financialSeries['margin'][str(now)] = float(moic_t * p - p)

        returns = {'Principal Balance - BOP': p_bop, 'Interest': interest_monthly, 'Interest - Uncapitalized': uncapitalized_interest, 'Interest - Capitalized': capitalized_interest, 
                   'Pik': pik, 'Commitment Fee': com_fee, 'Extension Fee': '', 'Financing Fee': fin_fee, 'Incentive Fee': incentive, 'Draws': draw, 'Repayment': repayment, 
                   'Principal Balance - EOP': p_eop, 'Inflows': Decimal(inflows[-1][1]), 'Outflows': Decimal(outflows[-1][1]), 'Net': Decimal(inflows[-1][1] + outflows[-1][1])}
        
        for key, value in returns.items():
            analysis = ReturnsModelData(
                date=t,
                amount=value,
                category=key,
                project_informed=projects,
                ntp_proceed=ntp_p,
                cod_proceed=cod_p,
                closing_proceed=closing_p,
                maturity_repayment=maturity_repayment,
                data_status=target_status,
                projection_source=projection_source,
                classic=financial_io
            )

            analysis.save()

        t += relativedelta(months=+1)

    fin_series_final = right_size(inflows, outflows, net)
    print(fin_series_final)
    print(calc_irr(fin_series_final))

    financial_io.IRR = calc_irr(fin_series_final)
    fin_moic = calc_moic(fin_series_final)
    financial_io.MOIC = fin_moic
    financial_io.NPV = calc_npv(fin_series_final)
    financial_io.margin = fin_moic * financial_io.facility_size - financial_io.facility_size

    financial_io.save()

    return financialSeries