import pandas as pd
import math

file = 'vacancies_dif_currencies.csv'
data = pd.read_csv(file)
currencies = pd.read_csv('dataframe.csv')
data.insert(1, 'salary', None)

for i in data.itervatuples():
    s_from = i.salary_from
    s_to = i.salary_to
    s_currency = i.salary_currency
    salary = i.salary
    if type(s_currency) is str:
        if not math.isnan(s_from):
            salary = s_from
        elif not math.isnan(s_to):
            salary = s_to
        elif not math.isnan(s_from) and not math.isnan(s_to):
            salary = (s_from + s_to) / 2

        if s_currency != 'RUR' and s_currency in ["BYR", "USD", "EUR", "KZT", "UAH"]:
            val_cur = currencies[currencies['date']
                                 == f'01/{i.published_at[5:7]}/{i.published_at[:4]}'][s_currency].values[0]
            salary = salary * val_cur if not math.isnan(val_cur) else None
        elif s_currency != 'RUR':
            salary = None
        data.at[data.index[int(i.Index)], 'salary'] = salary

data.pop('salary_from')
data.pop('salary_to')
data.pop('salary_currency')
data.to_csv("vac_salary.csv", index=False)
