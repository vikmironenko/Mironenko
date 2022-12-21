import pandas as pd

file = 'vacancies_dif_currencies.csv'
data = pd.read_csv(file)
curs = data['salary_currency'].unique()

currency = []
for i in curs:
    if list(data['salary_currency']).count(i) > 5000:
        currency.append(i)
del currency[0]

data.sort_values(by='published_at', inplace=True)
start,end = list(data['published_at'])[0], list(data['published_at'])[-1]
dataframe = pd.DataFrame(columns=["date", "BYR", "USD", "EUR", "KZT", "UAH"])

for year in range(2003, 2023):
    for month in range(1, 13):
        if month == 1 and year == 2003:
            date = '24/01/2003'
        elif month == 7 and year == 2022:
            date = '19/07/2022'
        else:
            date = f'01/0{month}/{year}' if month < 10 else f'01/{month}/{year}'
        result = f'http://www.cbr.ru/scripts/XML_daily.asp?date_req={date}'
        new_row = {'date': date}
        values_cur = pd.read_xml(result, encoding='cp1251')
        for cur in currency:
            if len(values_cur[values_cur['CharCode'] == cur]['Value'].values) != 0:
                value = '.'.join(str(values_cur[values_cur['CharCode'] == cur]['Value'].values[0]).split(','))
                new_row[cur] = float(value) / int(values_cur[values_cur['CharCode'] == cur]['Nominal'].values[0])
        dataframe = pd.concat([dataframe, pd.DataFrame.from_records([new_row])], axis=0, ignore_index=True)
        if date == '19/07/2022':
            break

dataframe.to_csv("dataframe.csv", index=False)