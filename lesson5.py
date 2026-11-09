import json

with open("warehouse.json", "r", encoding="utf-8") as file:
      inventory = json.load(file)

def restock_item(product_name, added_quantity):
    for item in inventory:
        if item["name"] == product_name:
            item["stock"] = item["stock"] + added_quantity
            return f"Поставка принята! {product_name}: теперь на складе {item['stock']} шт."
    
    return f"Товар {product_name} не найден в каталоге."
def sell_item(product_name, sold_quantity):
                for item in inventory:
                    if item["name"] == product_name:
                        if item["stock"] < sold_quantity:
                             return f"Ошибка! На складе всего {item['stock']} шт., нельзя продать {sold_quantity} шт."
                        item["stock"] = item["stock"] - sold_quantity 
                        revenue = item["price"] * sold_quantity
                        return f"Продано! {product_name} ({sold_quantity} шт.) на сумму {revenue} руб. Остаток: {item['stock']} шт."
while True:
    print("\n--- МЕНЮ СКЛАДА ---")
    print("1. Показать остатки")
    print("2. Принять поставку")
    print("3. Продать товар")
    print("0. Выход")

    choice = input("Выберите действие (0-3): ")
    
    if choice == "1":
        for item in inventory:
            print(f"- {item['name']}: {item['stock']} шт. ({item['price']} руб.)")
            
    elif choice == "2":
        name = input("Введите точное название табака: ")
        try:
            qty = int(input("Сколько пачек привезли? "))
            print(restock_item(name, qty))
        except ValueError:
            print("Ошибка: количество должно быть целым числом!")
    elif choice == "3":
        name = input("Какой табак вы продаете? ")
        try:
           qty = int(input("Сколько пачек продаете? "))
           print(sell_item(name, qty))
        except ValueError:
             print("Ошибка: количество должно быть целым числом!")
    elif choice == "0":
        print("Сохраняем базу и выходим...")
        break  # Разрываем бесконечный цикл и идем к сохранению файла внизу!
        
    else:
        print("Неизвестная команда, попробуйте снова.")

     
with open("warehouse.json", "w", encoding="utf-8") as file:
      json.dump(inventory, file, ensure_ascii=False, indent=4)