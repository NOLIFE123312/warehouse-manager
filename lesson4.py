#inventory = [
#    {"name": "Darkside Core", "price": 1400, "stock": 25},
#    {"name": "Musthave Pinkman", "price": 1500, "stock": 4},
#    {"name": "Black Burn", "price": 1450, "stock": 18},
#    {"name": "Tangiers Birquq", "price": 2400, "stock": 2},
#]

#def process_sale(product_name, quantity):
#    # Ищем товар в нашей базе
#    for item in inventory:
#        if item["name"] == product_name:  # Два равно == проверяют совпадение!
#            
#            # 1. Проверяем, хватает ли товара на складе
#            if item["stock"] < quantity:
#                return f"Отказ: {product_name} осталось всего {item['stock']} шт."
#            
#            # 2. Если хватает — списываем со склада и считаем сумму
#            item["stock"] = item["stock"] - quantity
#            total_price = item["price"] * quantity
#            return f"Успешно! Продано: {product_name} ({quantity} шт.) на сумму {total_price} руб. Остаток: {item['stock']} шт."
#            
#    # Этот return сработает, ТОЛЬКО если цикл прошел весь список и не нашел совпадений
#    return f"Ошибка: товар '{product_name}' не найден в базе."
#
# Проверяем работу нашего мини-бэкенда:
#print(process_sale("Musthave Pinkman", 3))  # Должно продать и оставить 1 шт.
#print(process_sale("Musthave Pinkman", 2))  # А тут уже должен быть отказ, ведь осталась всего 1 шт.!
#print(process_sale("Al Fakher", 1))         # Такого товара нет в списке
inventory = [
    {"name": "Darkside Core", "price": 1400, "stock": 25},
    {"name": "Black Burn", "price": 1500, "stock": 3},
    {"name": "Musthave Pinkman", "price": 1450, "stock": 6},
    {"name": "Tangiers Birquq", "price": 1600, "stock": 17},
]

def restock_item(product_name, added_quantity):
    for item in inventory:
        if item["name"] == product_name:
            item["stock"] = item["stock"] + added_quantity
            return f"Поставка принята! {product_name}: теперь на складе {item['stock']} шт."
    
    return f"Товар {product_name} не найден в каталоге."
print(restock_item("Tangiers Birquq", 5))
print(restock_item("Сарма", 5))