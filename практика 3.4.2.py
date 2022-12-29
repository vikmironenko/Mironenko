import pandas as pd
import pdfkit
from jinja2 import Environment, FileSystemLoader

def statistics(file, job):
    data = pd.read_csv(file, encoding='utf-8-sig').dropna()\
            .assign(salary=lambda x: x['salary'].astype('int64'),
                    area_name=lambda x: x['area_name'].astype('category'))\
            .assign(year=lambda x: x.apply(lambda y: y['published_at'].split('T')[0].split('-')[0], axis=1))
    salary = data[['year', 'salary']].groupby('year').mean().round().to_dict()['salary']
    selected_salary = data[data.name.apply(lambda x: job.lower() in x.lower())][['year', 'salary']].groupby('year').mean().round().to_dict()['salary']
    c = data.groupby('year').count().to_dict()['salary']
    selected_c = data[data.name.apply(lambda x: job.lower() in x.lower())].groupby('year').count().to_dict()['salary']
    header = ['год', 'зарплата по годам', 'зарплата по годам для выбранной профессии', 'количество вакансий',
              'количество вакансий для выбранной профессии']
    dict = dict()
    for i in salary:
        dict[i] = dict()
        dict[i][header[0]] = i
        dict[i][header[1]] = salary[i]
        dict[i][header[2]] = selected_salary[i]
        dict[i][header[3]] = c[i]
        dict[i][header[4]] = selected_c[i]

    env = Environment(loader=FileSystemLoader('.'))
    temp = env.get_template("pdf_template.html")
    pdf_temp = temp.render({'header': header, 'd': dict})
    config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
    pdfkit.from_string(pdf_temp, '3.4.2.pdf', configuration=config)

    print('Динамика уровня зарплат по годам:', salary)
    print('Динамика уровня зарплат по годам для выбранной профессии:', selected_salary)
    print('Динамика количества вакансий по годам:', c)
    print('Динамика количества вакансий по годам для выбранной профессии:',selected_c)

file = input('Введите название файла: ')
job = input('Введите название вакансии: ')

statistics(file, job)