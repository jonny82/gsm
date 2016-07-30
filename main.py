import decimal
decimal.getcontext().rounding = 'ROUND_HALF_UP'

# нормы расхода бензина в летние и зимние месяцы (город/межгород)
fuel_norma_summer = {"incity": 0.093, "outcity": 0.089} # расход летом
fuel_norma_winter = {"incity": 0.102, "outcity": 0.098} # расход зимой
fuel_norma = {"summer": fuel_norma_summer, "winter": fuel_norma_winter}
    

# путевой лист/расходы за день
class DayRecord:
    def __init__(self,
                date_waybill,       # дата путевого листа/дня
                number_waybill,     # номер путевого листа
                speedometer_begin,  # показания спидометра в начале дня
                speedometer_end,    # показания спидометра в конце дня
                fuel_begin,         # количество бензина в начале дня
                fuel_added):        # количество бензина заправлено
        
        self.date_waybill             = date_waybill
        self.number_waybill           = number_waybill
        self.speedometer_begin        = speedometer_begin
        self.speedometer_end          = speedometer_end        
        self.fuel_begin               = fuel_begin
        self.fuel_added               = fuel_added
        
        # расчет общего километража
        self.distance = self.speedometer_end - self.speedometer_begin
        
        # расчет километража по городу и межгороду
        if self.distance < 370:
            self.distance_outcity = 0               # километраж вне города
            self.distance_incity = self.distance    # километраж по городу
        else:
            self.distance_outcity = 370
            self.distance_incity = self.distance - 370
        
        # расчет расхода бензина и остатка. Пока - только по летней норме
        self.fuel_balance = decimal.Decimal(        # расход бензина
                self.distance_outcity * fuel_norma["summer"]["outcity"] + 
                self.distance_incity * fuel_norma["summer"]["incity"]
                ).quantize(decimal.Decimal(".00"))

        # расчет остатка бензина        
        self.fuel_end = decimal.Decimal(            # остаток бензина
                self.fuel_begin - self.fuel_balance + self.fuel_added
                ).quantize(decimal.Decimal(".00"))

"""
class MonthRecord:
    def __init__(self,
                speedometer_begin,
                speedometer_end,
                fuel_natural_begin,
                fuel_ticket_begin,
                fuel_norm,
                fuel_expense,
                fuel_natural_end,
                fuel_ticket_end):
"""

if __name__ == "__main__":
    date_waybill = input("дата путевого листа/дня: ")
    number_waybill = input("номер путевого листа: ")
    speedometer_begin = int(input("показания спидометра в начале дня: "))
    speedometer_end = int(input("показания спидометра в конце дня: "))
    fuel_begin = decimal.Decimal(input("количество бензина в начале дня: "))
    fuel_added = decimal.Decimal(input("количество бензина заправлено: "))
    
    current_day = DayRecord(
                date_waybill,
                number_waybill,
                speedometer_begin,
                speedometer_end,
                fuel_begin,
                fuel_added)
    
    print("\n\n\t", "-" * 40)
    print("\t\t\tПутевой лист.")
    print("дата путевого листа/дня:", current_day.date_waybill)
    print("номер путевого листа:", current_day.number_waybill)
    print()
    
    print("показания спидометра в начале дня:", current_day.speedometer_begin)
    print("показания спидометра в конце дня:", current_day.speedometer_end)
    print("общий километраж:", current_day.distance)
    print("километраж по городу:", current_day.distance_incity)
    print("километраж по межгороду:", current_day.distance_outcity)
    print()
    
    print("количество бензина в начале дня:", current_day.fuel_begin)
    print("заправлено бензина:", current_day.fuel_added)
    print("расход бензина:", current_day.fuel_balance)
    print("остаток бензина:", current_day.fuel_end)
    print("\t", "-" * 40, "\n\n")
