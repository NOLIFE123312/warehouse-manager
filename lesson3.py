inventory = [
    {"name": "Darkside core", "price": 1400, "stock": 25},
    {"name": "Musthave Pinkman", "price": 1500, "stock": 4},
    {"name": "Black Burn", "price": 1450, "stock": 18},
    {"name": "Tangiers Birquq", "price": 2400, "stock": 2},
]
def calculate_order(price, quantity, delivery_cost):
    items_cost = price * quantity 
    if items_cost >= 5000:
        total = items_cost
    else:
        total = items_cost + delivery_cost
    return total
order1 = calculate_order(1500, 2, 300)
order2 = calculate_order(1500, 4, 300)
print(order1)
print(order2)