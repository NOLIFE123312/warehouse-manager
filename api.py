from fastapi import FastAPI
from pydantic import BaseModel
from database import Product, Session
from rag import ask_rag

class ProductCreate(BaseModel):
    name: str
    price: int
    stock: int

class QuestionRequest(BaseModel):
    question: str
# Создаем приложение FastAPI
app = FastAPI(title="Warehouse API", description="API управления складом табака")

# Главная страница сервера (проверка связи)
@app.get("/")
def home():
    return {"message": "Сервер склада работает! Перейди на /docs для управления."}

# Получить список всех табаков из базы в формате JSON
@app.get("/products")
def get_all_products():
    db = Session()
    products = db.query(Product).all()
    db.close()
    return products

@app.post("/products")
def create_product(item: ProductCreate):
    db = Session()
    new_product = Product(name=item.name, price=item.price, stock=item.stock)
    db.add(new_product)
    db.commit()
    db.close()
    return {"status": "Товар успешно добавлен!", "product": item.name}

# Твоя функция расчета бюджета, но теперь как веб-эндпоинт!
@app.get("/budget")
def get_warehouse_budget():
    db = Session()
    products = db.query(Product).all()
    db.close()

    total_sum = 0
    for item in products:
        total_sum += item.price * item.stock

    return {
        "total_products": len(products),
        "total_budget_rub": total_sum
    }
@app.get("/low-stock")
def get_low_stock(limit: int = 5):
    db = Session()
    low_products = db.query(Product).filter(Product.stock <=limit).all()
    db.close()

    return {
        "max_stock_limit": limit,
        "found_count": len(low_products),
        "products": low_products
    }
@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    db = Session()
    product = db.query(Product).filter_by(id=product_id).first()

    if not product:
        db.close()
        return {"error": "Товар с таким ID не найден!"}
    
    
    delete_name = product.name
    db.delete(product)
    db.commit()
    db.close()

    return {"status": "Удалено!",
            "product": delete_product
    }
@app.post("/ask-ai")
def ask_ai(data:QuestionRequest):
    result = ask_rag(data.question)
    return result