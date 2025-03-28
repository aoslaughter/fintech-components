markets = [
    ("iso-ne", "ISO-NE"), ("nyiso", "NYISO"), ("pjm", "PJM"),
    ("caiso", "CAISO"), ("miso", "MISO"), ("ercot", "ERCOT")
           ]

technologies = [
    ("solar", "solar"), ("storage", "Storage"), ("onshore wind", "Onshore Wind"),
    ("Wind - Offshore", "Wind - Offshore"), ("hydrogen", "Hydrogen")
    ]

data_statuses = [('active', 'Active'), ('archived', 'Archived'), ('underwritten', 'Underwritten'),
                 ('marked', 'Marked'), ('active - forecast', 'Active - Forecast'),
                 ('archived - forecast', 'archived - Forecast'),('actual', 'Actual'),
                 ('target', 'Target')]

projection_choices = [('automated', 'Automated'), ('manual', 'Manual'),
                      ('underwritten model', 'Underwritten Model'), ('pam model', 'PAM Model')]

returns_model_choices = [('principal balance - bop', 'Principal Balance - BOP'), ('interest', 'Interest'),
                         ('interest - uncapitalized', 'Interest - Uncapitalized'), 
                         ('interest - capitalized', 'Interest - Capitalized'),
                         ('pik', 'Pik'), ('deposit refunds', 'Deposit Refunds'),
                         ('commitment fee', 'Commitment Fee'), ('extension fee', 'Extension Fee'),
                         ('origination fee', 'Origination Fee'), ('estimated closing costs', 'Estimated Closing Costs'),
                         ('financing fee', 'Financing Fee'), ('incentive fee', 'Incentive Fee'),
                         ('draws', 'Draws'), ('repayment', 'Repayment'), ('interest repayment', 'Interest Repayment'), 
                         ('principal balance - eop', 'Principal Balance - EOP'),
                         ('incentive fee - pl', 'Incentive Fee - PL'), ('minimum moic', 'Minimum MOIC'), 
                         ('inflows', 'Inflows'), ('outflows', 'Outflows'), ('net', 'Net')]

proceed_choices = [('ntp proceed', 'NTP Proceed'), ('cod proceed', 'COD Proceed'), ('closing proceed', 'Closing Proceed'), ('maturity repayment', 'Maturity Repayment')]