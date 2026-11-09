from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

# 1. Подключаемся к базе данных (файл warehouse_db.sqlite создастся сам)
engine = create_engine("sqlite:///warehouse_db.sqlite")
Base = declarative_base()

# 2. Описываем чертеж таблицы товаров (Модель)
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)      # Уникальный номер товара (1, 2, 3...)
    name = Column(String, nullable=False)       # Название табака (текст)
    price = Column(Integer, nullable=False)      # Цена (число)
    stock = Column(Integer, default=0)          # Остаток на складе (число)

# 3. Создаем саму таблицу в базе данных
Base.metadata.create_all(engine)

# 4. Открываем сессию (канал связи с базой для записи и чтения)
Session = sessionmaker(bind=engine)
session = Session()

# 5. Добавляем первый товар в SQL-базу (если таблица еще пустая)
if session.query(Product).count() == 0:
    item1 = Product(name="Darkside Core", price=1400, stock=25)
    item2 = Product(name="Tangiers Birquq", price=2400, stock=17)
    
    session.add_all([item1, item2])
    session.commit()  # Сохраняем изменения в базе!
    print("Товары успешно записаны в SQL-базу!")

# 6. Читаем все товары из базы данных и выводим на экран
all_products = session.query(Product).all()
print("\n--- СПИСОК ИЗ БАЗЫ ДАННЫХ SQL ---")
for product in all_products:
    print(f"ID: {product.id} | {product.name} — {product.stock} шт. по {product.price} руб.")

tobacco = session.query(Product).filter_by(name="Tangiers Birquq").first()
if tobacco:
    tobacco.stock = tobacco.stock + 10
    tobacco.price = 2500
    session.commit()
    print(f"Обновлено! Новый остаток и цена {tobacco.name}: {tobacco.stock} шт. и {tobacco.price} руб.")