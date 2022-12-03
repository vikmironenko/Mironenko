import csv
from datetime import datetime
from statistics import mean
import matplotlib.pyplot as plt
import numpy as np


class SalaryDict:
    ''' Класс для для получения данных по зарплатам для выбранной вакансии
    '''

    def __init__(self):
        ''' Создает словари для дальнейшей работы

        salary_dict (dict) : словарь для всех зарплат в файле, где ключ - это название города, а значение - массив зарплат
        average_salary_dict (dict) : словарь для записи средних зарплат
        '''
        self.salary_dict = {}
        self.__average_salary_dict = {}

    def add_salary(self, key, salary):
        ''' Добавляет все поля salary в словарь по городам, если ключа нет в словаре, на место ключа записывает пустой массив

            key (str or int) : ключ для получения зарплаты в словаре
            salary (int or float) : зарплата, которую добавляет в словарь
        '''

        if self.salary_dict.get(key) is None:
            self.salary_dict[key] = []
        return self.salary_dict[key].append(salary)

    def get_average_salary(self):
        ''' Записывает в average_salary_dict среднюю зарплату, возвращает словарь, где ключ - это название города, а значение - средняя зп
        '''

        for key, value in self.salary_dict.items():
            self.__average_salary_dict[key] = int(mean(value))
        return self.__average_salary_dict

    def top_salary(self, big_cities):
        ''' Находит самые большие срдение зарплаты, записывает в словарь топ 10

            big_cities (array) : массив самых крупных городов
        '''

        self.get_average_salary()
        sorted_dict = dict(sorted(self.__average_salary_dict.items(), key=lambda x: x[1], reverse=True))
        big_salary_dict = {}
        for key, value in sorted_dict.items():
            if key in big_cities:
                big_salary_dict[key] = value
        return {x: big_salary_dict[x] for x in list(big_salary_dict)[:10]}


class CountDict:
    ''' Класс для получения количества вакансий для выбранной профессии'''

    def __init__(self):
        ''' length (int) : счетчик для получения количества вакансий
            count_dict (dict) : словарь, куда будут записываться данные по количеству
            big_cities (array) : массив самых крупных городов
            top_proportion_dict (dict) :
        '''
        self.length = 0
        self.count_dict = {}
        self.big_cities = []
        self.top_proportion_dict = {}

    def add(self, key):
        ''' Считает количество вакансий для городов и годов, записывает число в словарь

           key (str or int) : ключ для получения данных в словаре
        '''
        if self.count_dict.get(key) is None:
            self.count_dict[key] = 0
        self.count_dict[key] += 1
        self.length += 1
        return

    def get_proportion(self):
        ''' Выбирает самые крупные города
            Получает процент для каждого города, город с большим значением записывает в массив'''

        proportion_dict = {}
        for key, value in self.count_dict.items():
            proportion = value / self.length
            if proportion >= 0.01:
                self.big_cities.append(key)
                proportion_dict[key] = round(proportion, 4)
        sorted_dict = dict(sorted(proportion_dict.items(), key=lambda x: x[1], reverse=True))
        self.top_proportion_dict = {x: sorted_dict[x] for x in list(sorted_dict)[:10]}
        return


class Vacancy:
    ''' Класс для получения данных о вакансии'''

    def __init__(self, data):
        ''' Записывает в нужные поля все данные о вакансии, для зарплаты ищет среднее и переводит в рубли, время переводит в нужный формат

        data(array) : массив с одной вакансией
        '''

        if len(data) != 6:
            data = [data[0], data[6], data[7], data[9], data[10], data[11]]
        self.__dict_currency = {"AZN": 35.68, "BYR": 23.91, "EUR": 59.90, "GEL": 21.74, "KGS": 0.76, "KZT": 0.13,
                                "RUR": 1, "UAH": 1.64, "USD": 60.66, "UZS": 0.0055}
        self.job = data[0]
        self.salary = (float(data[1]) + float(data[2])) / 2 * self.__dict_currency[data[3]]
        self.city = data[4]
        self.year = int(datetime.strptime(data[5], "%Y-%m-%dT%H:%M:%S%z").strftime('%Y'))


class Report:
    ''' Класс для рисования графиков'''

    def __init__(self):
        ''' Создает нужные перемнные'''

        self.salary_year = SalaryDict()
        self.count_year = CountDict()
        self.job_salary_year = SalaryDict()
        self.job_count_year = CountDict()
        self.job_salary_city = SalaryDict()
        self.job_count_city = CountDict()

    def get_data(self, vacancies, job):
        ''' Добавляет все нужные данные в словари из вакансий

        vacancies(array): массив всех вакансий
        job(str) : нужная вакансия
        '''

        for vacancy in vacancies:
            self.salary_year.add_salary(vacancy.year, vacancy.salary)
            self.count_year.add(vacancy.year)
            self.job_salary_city.add_salary(vacancy.city, vacancy.salary)
            self.job_count_city.add(vacancy.city)
            if job in vacancy.job:
                self.job_salary_year.add_salary(vacancy.year, vacancy.salary)
                self.job_count_year.add(vacancy.year)
        if self.job_salary_year.salary_dict == {}:
            self.job_salary_year.salary_dict = {x: [0] for x in self.salary_year.salary_dict.keys()}
        if self.job_count_year.count_dict == {}:
            self.job_count_year.count_dict = {x: 0 for x in self.count_year.count_dict.keys()}
        self.job_count_city.get_proportion()
        return

    def generate_image(self):
        ''' Генерирует картинку для всех графиков'''

        def build_graphs(numb, str):
            ''' Создаем области для 4 графиков

            numb(int): характеристика расположения графа
            str(str): название области графа
            '''
            ax = self.fig.add_subplot(numb)
            ax.set_title(str)
            return ax

        def do_graph_salary(obj, dict1, dict2, str1, str2):
            ''' Создаем график зарплат

            obj(): область нахождения графика
            dict1, dict2 (dict): словари данных с зарплатами
            str1, str2(str): подписи для графиков
            '''
            obj.bar(x_list1, dict1.values(), self.width, label=str1)
            obj.bar(x_list2, dict2.values(), self.width, label=str2)
            obj.set_xticks(x_nums, dict1.keys(), rotation='vertical')
            obj.tick_params(axis='both', labelsize=8)
            obj.legend(fontsize=8)
            obj.grid(axis='y')

        ''' self.width: ширина колонок графика
        x_list1, x_list2: расположение столбцов графиков
        '''

        self.width = 0.4
        x_nums = np.arange(len(self.salary_year.get_average_salary().keys()))
        x_list1 = x_nums - self.width / 2
        x_list2 = x_nums + self.width / 2

        self.fig = plt.figure()

        ''' Создание графиков'''

        self.ax = build_graphs(221, 'Уровень зарплат по годам')
        do_graph_salary(self.ax, self.salary_year.get_average_salary(), self.job_salary_year.get_average_salary(),
                        'средняя з/п', f'з/п {job}')

        self.bx = build_graphs(222, 'Количество вакансий по годам')
        do_graph_salary(self.bx, self.count_year.count_dict, self.job_count_year.count_dict,
                        'количество вакансий', f'количество вакансий \n{job}')

        cx = build_graphs(223, 'Уровень зарплат по городам')
        plt.rcdefaults()
        y_pos = np.arange(len(self.job_salary_city.top_salary(self.job_count_city.big_cities).keys()))
        cx.barh(y_pos, self.job_salary_city.top_salary(self.job_count_city.big_cities).values(), align='center')
        cx.set_yticks(y_pos, labels=self.job_salary_city.top_salary(self.job_count_city.big_cities).keys(), fontsize=6)

        self.dx = build_graphs(224, 'Доля вакансий по городам')
        self.dx.pie(self.job_count_city.top_proportion_dict.values(),
                    labels=self.job_count_city.top_proportion_dict.keys(),
                    textprops={'fontsize': 8}, startangle=21)
        self.dx.axis("equal")

        plt.tight_layout()
        plt.savefig('graph.png')

    def print_result(self):
        ''' Выводит все словари с данными'''

        print(f"Динамика уровня зарплат по годам: {self.salary_year.get_average_salary()}")
        print(f"Динамика количества вакансий по годам: {self.count_year.count_dict}")
        print(f"Динамика уровня зарплат по годам для выбранной профессии: {self.job_salary_year.get_average_salary()}")
        print(f"Динамика количества вакансий по годам для выбранной профессии: {self.job_count_year.count_dict}")
        print(
            f"Уровень зарплат по городам (в порядке убывания): {self.job_salary_city.top_salary(self.job_count_city.big_cities)}")
        print(f"Доля вакансий по городам (в порядке убывания): {self.job_count_city.top_proportion_dict}")
        return


def csv_reader(file_name):
    ''' Получает данные о файле и считывает его, проверяет, чтобы файл не был пустым, возвращает лист с вакансиями'''

    file = open(file_name, encoding='utf_8_sig')
    reader = csv.reader(file)
    list_data = list(filter(lambda x: '' not in x, reader))
    if len(list_data) == 0:
        return print("Пустой файл")
    if len(list_data[1:]) == 0:
        return print('Het данных')
    return list_data[1:]


def get_report():
    '''Получает данные от пользователя, проверяет чтобы вакансии не были пустыми, вызывает все методы, формирует графики, выводит результат'''
    file_name = input("Введите название файла: ")
    job = input("Введите название профессии: ")
    job = job[0].lower() + job[1:]
    file = open(file_name, encoding="utf_8_sig")
    data = csv_reader(file_name)

    if data is not None:
        vacancies = [Vacancy(x) for x in data]
        result = Report()
        result.get_data(vacancies, job)
        result.print_result()
        result.generate_image(job)