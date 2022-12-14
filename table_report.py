import csv
import re
from datetime import datetime as DT
import prettytable
from prettytable import ALL as ALL
import os
import sys

def csv_reader(file_name):
    ''' Получает данные о файле и считывает его, проверяет, чтобы файл не был пустым, возвращает вакансии и названия полей

    file_name(str): название файла
    '''
    if os.stat(file_name).st_size == 0:
        print("Пустой файл")
        exit()
    else:
        csv_read = csv.reader(open(file_name, 'r', encoding='utf-8-sig'))
        list_data = [x for x in csv_read]
        columns = list_data[0]
        vac = [x for x in list_data[1:] if len(x) == len(columns) and x.count('') == 0]
        return columns, vac

def cleaning(vac):
    ''' Очищает вакансии от html тегов

    vac(str): поле вакансии
    '''
    vac = re.sub('<.*?>', '', vac)
    vac = vac.replace('\r\n', ' ')
    vac = vac.replace(u'\xa0', ' ')
    vac = vac.replace(u'\u2002', ' ')
    vac = vac.strip()
    vac = re.sub(' +', ' ', vac)
    return vac

def csv_filter(reader, list_naming):
    ''' Очищает вакансии, возвращает массив словарей

    reader(array):  лист с названиями полей
    list_naming(array): массив массивов с вакансиями
    '''

    vacancies = []
    for vac in list_naming:
        for i in range(len(vac)):
            vac[i] = cleaning(vac[i])
    for i in range(len(list_naming)):
        vacancies.append(dict(zip(reader, list_naming[i])))
    return vacancies

def bool(value, action1, action2):
    ''' Заменяет поля с булевыми значениями на новые

    value(str):  значение поля, которое нужно перевести
    action1, action2(str): значения, на которые нужно заменить true или false
    '''

    if value.lower() == 'true':
        value = action1
    if value.lower() == 'false':
        value = action2
    return value

def salary(f):
    ''' Переводит зарплату в формат с пробелом

    f(str):  зарплата
    '''

    f = int(float(f))
    return '{0:,}'.format(f).replace(',', ' ')

def formatter(row, rus_names):
    ''' Форматирует все вакансии, переводит нужные поля, зарплату объединяет в одно поле, дату переводит в нужный формат

    row(dict): вакансия с английскими названиями полей
    rus_names(dict): русские названия полей
    '''

    row['premium'] = bool(row['premium'], 'Да', 'Нет')
    row['salary_currency'] = rus_names[row['salary_currency']]
    row['experience_id'] = rus_names[row['experience_id']]
    row['salary_gross'] = bool(row['salary_gross'], '(Без вычета налогов)', '(С вычетом налогов)')
    row[
        'salary_gross'] = f"{salary(row['salary_from'])} - {salary(row['salary_to'])} ({row['salary_currency']}) {row['salary_gross']}"
    del row['salary_currency']
    del row['salary_to']
    del row['salary_from']
    row['published_at'] = DT.strptime(row['published_at'], '%Y-%m-%dT%H:%M:%S+%f').strftime('%d.%m.%Y')
    return row

def rus(data_vacancies, dic_naming):
    ''' Переводит все поля на русский, возвращает массив словарей

    data_vacancies(array): массив со словарями вакансий
    dic_naming(dict): русские названия полей
    '''

    rus_vac=[]
    for o in range(len(data_vacancies)):
        data = {}
        for i, k in data_vacancies[o].items():
            data[dic_naming[i]] = k
        rus_vac.append(data)
    return rus_vac


def division_numbers(str,filter):
    ''' Возвращает номера строк,которые нужны будут для вывода

    str(array): строка с числами для  вывода строк
    filter(str): отфильтрованные вакансии
    '''

    if len(str) == 0:
        return 1, len(filter)
    if str.find(' '):
        str = str.split(' ')
        if len(str) == 2:
            return int(str[0]), int(str[1]) - 1
        if len(str) == 1:
            return int(str[0]), len(filter)
    else:
        return int(str), len(filter)

def fil_prem(fil_vac: list, fil_value):
    ''' Фильтрует вакансии, если параметр фильрации премиум-вакансия

    fil_vac(list): массив вакансий
    fil_value(str): значение для фильтрации
    '''

    dic_translator = {
        'Да': 'True',
        'Нет': 'False'
    }
    return [vacancy for vacancy in fil_vac if vacancy['premium'] == dic_translator[fil_value]]


def column_output(str):
    ''' Отбирает нужные колонки таблицы для вывода по введенному параметру, если строка пустая, возвращает все колонки

    str(str): названия нужных колонок
    '''

    if len(str) == 0:
        return ["№", "Название", "Описание", "Навыки", "Опыт работы", "Премиум-вакансия", "Компания", "Оклад",
                "Название региона", "Дата публикации вакансии"]
    else:
        str = str.split(', ')
        str.insert(0, '№')
        return str

def filtrate(string, vacancies, filter_dict):
    ''' Возвращает отфильтрованные вакансии

    string(str): строка с параметром фильтрации
    vacancies(array): все вакансии
    filter_dict(dict): словарь с функциями для фильтрации
    '''

    s = 0
    if string == '':
        return vacancies
    if ':' not in string:
        print('Формат ввода некорректен')
        exit()
    header, value = string.split(': ')
    for nam in filter_dict.keys():
        if header == nam:
            s += 12
    if s == 0:
        print("Параметр поиска некорректен")
        exit()
    results = filter_dict[header](vacancies, value)
    if len(results) == 0:
        print('Ничего не найдено')
        exit()
    return results

def get_table():
    ''' Создает и выводит таблицу, фильтрует нужные вакансии по параметру'''

    rus_names = {'name': 'Название',
                 'description': 'Описание',
                 'key_skills': 'Навыки',
                 'experience_id': 'Опыт работы',
                 'premium': 'Премиум-вакансия',
                 'employer_name': 'Компания',
                 'salary_from': 'Нижняя граница вилки оклада',
                 'salary_to': 'Верхняя граница вилки оклада',
                 'salary_gross': 'Оклад',
                 'salary_currency': 'Идентификатор валюты оклада',
                 'area_name': 'Название региона',
                 'published_at': 'Дата публикации вакансии',
                 'noExperience': 'Нет опыта',
                 'between1And3': 'От 1 года до 3 лет',
                 'between3And6': 'От 3 до 6 лет',
                 'moreThan6': 'Более 6 лет',
                 'AZN': 'Манаты',
                 'BYR': 'Белорусские рубли',
                 'EUR': 'Евро',
                 'GEL': 'Грузинский лари',
                 'KGS': 'Киргизский сом',
                 'KZT': 'Тенге',
                 'RUR': 'Рубли',
                 'UAH': 'Гривны',
                 'USD': 'Доллары',
                 'UZS': 'Узбекский сум'}

    filter_dict = {
        'Название': lambda fil_vac, fil_value: [vacancy for vacancy in fil_vac if vacancy['name'] == fil_value],
        'Описание': lambda fil_vac, fil_value: [vacancy for vacancy in fil_vac if vacancy['description'] == fil_value],
        'Компания': lambda fil_vac, fil_value: [vacancy for vacancy in fil_vac if
                                                vacancy['employer_name'] == fil_value],
        'Название региона': lambda fil_vac, fil_value: [vacancy for vacancy in fil_vac if
                                                        vacancy['area_name'] == fil_value],
        'Навыки': lambda fil_vac, fil_value: [vacancy for vacancy in fil_vac if
                                              set(fil_value.split(', ')).issubset(vacancy['key_skills'].split('\n'))],
        'Опыт работы': lambda fil_vac, fil_value: [vacancy for vacancy in fil_vac if
                                                   rus_names[vacancy['experience_id']] == fil_value],
        'Премиум-вакансия': fil_prem,
        'Оклад': lambda fil_vac, fil_value: [vacancy for vacancy in fil_vac
                                             if int(vacancy['salary_from']) <= int(fil_value) <= int(
                vacancy['salary_to'])],
        'Дата публикации вакансии': lambda fil_vac, fil_value: [vacancy for vacancy in fil_vac
                                                                if DT.strptime(vacancy['published_at'],
                                                                               '%Y-%m-%dT%H:%M:%S+%f').strftime(
                '%d.%m.%Y') == fil_value],
        'Идентификатор валюты оклада': lambda fil_vac, fil_value: [vacancy for vacancy in fil_vac
                                                                   if
                                                                   rus_names[vacancy['salary_currency']] == fil_value]
    }
    ''' Создание таблицы, получает данные от пользователя'''

    table = prettytable.PrettyTable(hrules=ALL)
    names_table = []

    read = csv_reader(input('Введите название файла: '))
    filter_str = input('Введите параметр фильтрации: ')
    numbers = input('Введите диапазон вывода: ')
    name_columns = input('Введите требуемые столбцы: ')
    names = read[0]
    vac = read[1]

    filter = csv_filter(names, vac)
    filter = filtrate(filter_str, filter, filter_dict)
    for vacancy in filter:
        vacancy = formatter(vacancy, rus_names)
    try:
        for i in rus(filter, rus_names)[0].keys():
            names_table.append(i)
    except IndexError:
        print("Нет данных")
        sys.exit()

    table.field_names = ["№"] + names_table
    table.max_width = 20
    table.align = 'l'

    number = 1
    for i in range(len(filter)):
        items = []
        items.append(number)
        for k in filter[i].values():
            if len(k) > 100:
                k = k[:100] + (k[100:] and '...')
            items.append(k)
        number += 1
        table.add_row(items)

    print(table.get_string(start=division_numbers(numbers,filter)[0] - 1, end=division_numbers(numbers,filter)[1],
                           fields=column_output(name_columns)))