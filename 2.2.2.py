import table_report
import report_img

def main():
    ''' Получает данные от пользователя и запускает одну из программ'''

    str = input('Введите тип формирования данных: ')
    if str == 'Вакансии':
        table_report.get_table()
    elif str == 'Статистика':
        report_img.get_report()
    else:
        print('Неверный ввод')

main()