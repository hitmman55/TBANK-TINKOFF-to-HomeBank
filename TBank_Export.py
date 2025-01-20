import csv
from datetime import datetime

def tbank_to_qif(input_csv, output_qif, account_type="Bank"):
    """
    Считывает CSV из ТБАНК и генерирует QIF-файл (для Homebank).
    account_type может быть: 'Bank', 'CCard', 'Cash' и т.п.

    Пример полей CSV (индексы):
    0: Дата операции (строка, наподобие '20.01.2025 12:35')
    1: Дата платежа
    2: Номер карты
    3: Статус
    4: Сумма операции
    5: Валюта операции
    6: Сумма платежа
    7: Валюта платежа
    8: Кэшбэк
    9: Категория
    10: MCC
    11: Описание
    12: Бонусы
    13: Округление
    14: Сумма операции с округлением
    """

    with open(input_csv, 'r', encoding='cp1251') as f_in, \
         open(output_qif, 'w', newline='', encoding='utf-8') as f_out:
        
        csv_in = csv.reader(f_in, delimiter=';')
        
        # Пропускаем строку заголовков (если есть)
        header = next(csv_in, None)

        # Пишем заголовок для QIF (тип счёта - Bank, CCard или Cash)
        f_out.write(f"!Type:{account_type}\n")

        for row in csv_in:
            # row[0] = "20.01.2025 12:35"
            # row[4] = "6045" (сумма)
            # row[9] = "Переводы" (категория)
            # row[11] = "Перевод средств" (описание)

            raw_datetime = row[0]
            amount_str = row[4]
            category_str = row[9]
            payee_str = row[11]

            # Парсим дату (берём только дату без секунд)
            # Если в файле ещё и секунды, используйте '%d.%m.%Y %H:%M:%S'
            date_obj = datetime.strptime(raw_datetime, '%d.%m.%Y %H:%M:%S')
            # QIF чаще всего использует формат D/M/YYYY:
            date_str = date_obj.strftime('%d/%m/%Y')

            # Преобразуем сумму в float
            # Если нужно различать доход/расход, раскомментируйте логику
            amount_val = float(amount_str.replace(',', '.'))

            # Пример: если категория = "Переводы", считаем это доходом (плюс),
            # иначе делаем минус:
            # if category_str != "Переводы":
            #     amount_val = -abs(amount_val)

            # Формируем блок QIF (по строкам)
            lines = []
            # D - дата
            lines.append(f"D{date_str}")
            # T - сумма (T+число для дохода, T-число для расхода)
            lines.append(f"T{amount_val:.2f}")
            # P - Payee (кому/от кого)
            lines.append(f"P{payee_str}")
            # M - Memo (доп. комментарий) - если нужен
            # lines.append(f"MДоп. комментарий")

            # L - Категория (если хотите привязать в Homebank)
            lines.append(f"L{category_str}")

            # ^ - конец транзакции
            lines.append("^")

            # Записываем в файл
            for line in lines:
                f_out.write(line + "\n")

    print(f"Готово! Сформирован файл {output_qif}")

# ==========================
# Точка входа для запуска
# ==========================
if __name__ == "__main__":
    # Здесь вы указываете свой входной CSV и желаемое имя выходного QIF
    input_csv = "tbank_input.csv"
    output_qif = "tbank_output.qif"

    # 'Bank' - счёт как банковский; можно задать 'CCard' (кредитка) или 'Cash' (наличные)
    tbank_to_qif(input_csv, output_qif, account_type="Bank")
