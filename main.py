# добавить подстановку предыдущих значений при вводе данных путевого листа

import decimal
import pickle
import datetime


decimal.getcontext().rounding = "ROUND_HALF_UP"


# "летние" и "зимние" месяцы для расчета расхода бензина по нормам расхода
# "летние" месяцы
MONTHS_SUMMER = (4, 5, 6, 7, 8, 9, 10)
# "зимние" месяцы
MONTHS_WINTER = (1, 2, 3, 11, 12)
# все месяцы
MONTHS = {"summer": MONTHS_SUMMER, "winter": MONTHS_WINTER}

# нормы расхода бензина в "летние" и "зимние" месяцы (город/межгород)
# норма расхода бензина летом
FUEL_NORMA_SUMMER = {"inside_city": 0.093, "outside_city": 0.089}
# норма расхода бензина зимой
FUEL_NORMA_WINTER = {"inside_city": 0.102, "outside_city": 0.098}
# общая норма расхода бензина
FUEL_NORMA = {"summer": FUEL_NORMA_SUMMER, "winter": FUEL_NORMA_WINTER}


# путевой лист и расходы за день
class DayRecord:
    def __init__(self,
                 date_waybill,                # дата путевого листа/дня
                 number_waybill,              # номер путевого листа
                 speedometer_begin,           # показания спидометра в начале дня
                 speedometer_end,             # показания спидометра в конце дня
                 fuel_begin,                  # количество бензина в начале дня
                 fuel_added,                  # количество бензина заправлено
                 distance=None,               # общий километраж
                 distance_outside_city=None,  # километраж вне города
                 distance_inside_city=None,   # километраж по городу
                 type_of_month=None,          # вид месяца: "зимний" или "летний"
                 fuel_balance=None,           # расход бензина
                 fuel_end=None):              # остаток бензина

        self.date_waybill = date_waybill
        self.number_waybill = number_waybill
        self.speedometer_begin = speedometer_begin
        self.speedometer_end = speedometer_end
        self.fuel_begin = fuel_begin
        self.fuel_added = fuel_added

        # расчет общего километража
        if distance is None:
            self.distance = self.speedometer_end - self.speedometer_begin
        else:
            self.distance = distance

        # расчет километража по городу и межгороду
        if self.distance < 370:               # 370: расстояние Абаза-Абакан-Абаза
            if distance_outside_city is None:
                self.distance_outside_city = 0
            else:
                self.distance_outside_city = distance_outside_city
            if distance_inside_city is None:
                self.distance_inside_city = self.distance
            else:
                self.distance_inside_city = distance_inside_city
        else:
            if distance_outside_city is None:
                self.distance_outside_city = 370
            else:
                self.distance_outside_city = distance_outside_city
            if distance_inside_city is None:
                self.distance_inside_city = self.distance - 370
            else:
                self.distance_inside_city = distance_inside_city

        # определение, "зимний" это месяц или "летний"
        if type_of_month is None:
            for key in MONTHS.keys():
                if self.date_waybill.month in MONTHS[key]:
                    self.type_of_month = key
                    break
        else:
            self.type_of_month = type_of_month

        # расчет расхода бензина в зависимости от времени года
        if fuel_balance is None:
            self.fuel_balance = decimal.Decimal(
                self.distance_outside_city * FUEL_NORMA[self.type_of_month]["outside_city"] +
                self.distance_inside_city * FUEL_NORMA[self.type_of_month]["inside_city"]
                ).quantize(decimal.Decimal(".00"))
        else:
            self.fuel_balance = fuel_balance

        # расчет остатка бензина
        if fuel_end is None:
            self.fuel_end = decimal.Decimal(
                self.fuel_begin - self.fuel_balance + self.fuel_added
                ).quantize(decimal.Decimal(".00"))
        else:
            self.fuel_end = fuel_end

    def print_day_record(self):
        print("-" * 79)
        print("ПУТЕВОЙ ЛИСТ.\n")
        print("дата путевого листа/дня:", self.date_waybill)
        print("номер путевого листа:", self.number_waybill)
        print("показания спидометра в начале дня:", self.speedometer_begin)
        print("показания спидометра в конце дня:", self.speedometer_end)
        print("общий километраж:", self.distance)
        print("километраж по городу:", self.distance_inside_city)
        print("километраж по межгороду:", self.distance_outside_city)
        print("количество бензина в начале дня:", self.fuel_begin)
        print("заправлено бензина:", self.fuel_added)
        print("расход бензина:", self.fuel_balance)
        print("остаток бензина:", self.fuel_end)
        print("-" * 79, "\n\n")


# список путевых листов/дней и расходование ГСМ за месяц
class MonthRecord:
    def __init__(self,
                 date_begin,               # начальная дата
                 waybill_number_begin,     # начальный номер путевого листа
                 speedometer_begin,        # начальные показания спидометра
                 fuel_natural_begin,       # начальное количество бензина
                 fuel_ticket_begin,        # начальное кол-во бензина талонами
                 fuel_month_norm,          # норма расхода на месяц (250 л.)
                 day_records=None,         # список записей путевых листов
                 waybill_number_end=None,  # последний номер путевого листа
                 speedometer_end=None,     # последние показания спидометра
                 fuel_balance=None,        # расход бензина
                 fuel_natural_end=None,    # итоговое количество бензина
                 fuel_ticket_end=None,     # итоговое количество бензина талонами
                 filename=None):           # имя файла с данными месяца

        self.date_begin = date_begin
        self.waybill_number_begin = waybill_number_begin
        self.speedometer_begin = speedometer_begin
        self.fuel_natural_begin = fuel_natural_begin
        self.fuel_ticket_begin = fuel_ticket_begin
        self.fuel_month_norm = fuel_month_norm

        if day_records is None:
            self.day_records = []
        else:
            self.day_records = day_records

        if waybill_number_end is None:
            self.waybill_number_end = self.waybill_number_begin
        else:
            self.waybill_number_end = waybill_number_end

        if speedometer_end is None:
            self.speedometer_end = self.speedometer_begin
        else:
            self.speedometer_end = speedometer_end

        if fuel_balance is None:
            self.fuel_balance = 0
        else:
            self.fuel_balance = fuel_balance

        if fuel_natural_end is None:
            self.fuel_natural_end = self.fuel_natural_begin + \
                                    self.fuel_ticket_begin + self.fuel_month_norm
        else:
            self.fuel_natural_end = fuel_natural_end

        if fuel_ticket_end is None:
            self.fuel_ticket_end = 0
        else:
            self.fuel_ticket_end = fuel_ticket_end

        if filename is None:
            self.filename = str(self.date_begin.year) + "-" + str(self.date_begin.month).zfill(2)
        else:
            self.filename = filename

    def print_month(self):
        print("-" * 79)
        print("МЕСЯЦ:", self.filename, "\n")
        if len(self.day_records):
            print("Количество записей:", len(self.day_records), "\n")
            print("{:^10}{:^9}{:^11}{:^9}{:^9}{:^9}{:^9}{:^9}{:^9}".format(
                "ДАТА", "№ П/Л", "СПИДОМЕТР", "ГОРОД", "М/ГОРОД", "ОБЩИЙ", "РАСХОД", "ОСТАТОК", "ЗАПРАВКА"))
            for i in self.day_records:
                print("{:>10}{:>9}{:>11}{:>9}{:>9}{:>9}{:>9}{:>9}{:>9}".format(
                    str(i.date_waybill), i.number_waybill, i.speedometer_end, i.distance_inside_city,
                    i.distance_outside_city, i.distance, i.fuel_balance, i.fuel_end, i.fuel_added))
        else:
            print("Список записей пуст.")
        print()

        print("начальная дата:", self.date_begin)
        print("начальный номер путевого листа:", self.waybill_number_begin)
        print("итоговый номер путевого листа:", self.waybill_number_end)
        print("начальные показания спидометра:", self.speedometer_begin)
        print("итоговые показания спидометра:", self.speedometer_end)
        print("начальное количество бензина:", self.fuel_natural_begin)
        print("итоговое количество бензина:", self.fuel_natural_end)
        print("начальное кол-во бензина талонами:", self.fuel_ticket_begin)
        print("итоговое кол-во бензина талонами:", self.fuel_ticket_end)
        print("норма расхода бензина на месяц: ", self.fuel_month_norm)
        print("расход бензина:", self.fuel_balance)
        print("файл записей ", self.filename)
        print("-" * 79, "\n")

    # добавление нового дня и изменение данных месяца после добавлении дня
    def add_day(self):
        print("\nНовый день.\n")

        if len(self.day_records):
            temp = self.waybill_number_begin
        else:
            temp = self.waybill_number_end + 1
        temp2 = input("дата путевого листа/дня (Enter для значения", str(temp), "): ")
        if temp2 == "":
            date_waybill = temp
        else:
            date_waybill = temp2
            # преобразование даты путевого листа в тип datetime
            date_waybill = datetime.datetime.strptime(date_waybill, "%d.%m.%Y").date()


        number_waybill = int(input("номер путевого листа: "))
        speedometer_begin = int(input("показания спидометра в начале дня: "))
        speedometer_end = int(input("показания спидометра в конце дня: "))
        fuel_begin = decimal.Decimal(input("количество бензина в начале дня: "))
        fuel_added = decimal.Decimal(input("количество бензина заправлено: "))

        cur_day = DayRecord(
            date_waybill,
            number_waybill,
            speedometer_begin,
            speedometer_end,
            fuel_begin,
            fuel_added)

        cur_day.print_day_record()

        self.day_records.append(cur_day)
        self.waybill_number_end = cur_day.number_waybill
        self.speedometer_end = cur_day.speedometer_end
        self.fuel_natural_end -= cur_day.fuel_balance
        self.fuel_balance += cur_day.fuel_balance


# Меню - создание месяца
def create_new_month():
    print("\nНовый месяц.\n")
    date_begin = input("начальная дата: ")
    waybill_number_begin = int(input("начальный номер путевого листа: "))
    speedometer_begin = int(input("начальные показания спидометра: "))
    fuel_natural_begin = decimal.Decimal(input("начальное количество бензина: "))
    fuel_ticket_begin = decimal.Decimal(input("начальное количество бензина талонами: "))
    fuel_month_norm = int(input("норма расхода на месяц: "))

    # преобразование начальной даты в тип datetime
    date_begin = datetime.datetime.strptime(date_begin, "%d.%m.%Y").date()

    new_month = MonthRecord(
                date_begin,
                waybill_number_begin,
                speedometer_begin,
                fuel_natural_begin,
                fuel_ticket_begin,
                fuel_month_norm)

    return new_month


# Меню - открыть файл с данными месяца
def open_file():
    file_name = input("Введите имя файла: ")

    with open(file_name, "rb") as f:
        cur_month = pickle.load(f)

    return cur_month


# Меню - запись месяца в файл
def write_to_file(cur_month):
    with open(cur_month.filename, "wb") as f:
        pickle.dump(cur_month, f)


if __name__ == "__main__":
    current_month = None
    current_day = None

    while True:
        print("1. Открыть месяц.")
        print("2. Создать новый месяц.")
        print("3. Распечатать текущий месяц.")
        print("4. Создать новый день.")
        print("0. Выход")
        choice = int(input("\n Введите номер команды: "))
        if choice == 1:
            current_month = open_file()
            current_month.print_month()
        elif choice == 2:
            current_month = create_new_month()
            current_month.print_month()
            write_to_file(current_month)
        elif choice == 3:
            if current_month is not None:
                current_month.print_month()
            else:
                print("Сначала нужно создать новый месяц или открыть имеющийся.\n")
        elif choice == 4:
            if current_month is not None:
                current_month.add_day()
                write_to_file(current_month)
            else:
                print("Сначала нужно создать новый месяц или открыть имеющийся.\n")
        else:
            break
