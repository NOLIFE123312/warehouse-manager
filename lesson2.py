item_name = "Табак"
price = 1500
stock_count = 60
sold_today = int(input("Введите количество проданных пачек: ")) 

if sold_today > stock_count:
    print(f"Ошибка! На складе всего {stock_count} шт, нельзя продать {sold_today}")
else:
    remaining_stock = stock_count - sold_today
    revenue = sold_today * price
    print(f"Товар: {item_name}")
    print(f"Успешно! Отслаось на складе: {remaining_stock} шт., выручка: {revenue} руб. ")  
    if remaining_stock < 10 :
        print("ВНИМАНИЕ: Запас критически мал.")
    else:   
        print("Запас в норме.")


