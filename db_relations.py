from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# Создаем новый файл базы данных специально для связанных таблиц
engine = create_engine("sqlite:///warehouse_linked.sqlite")
Base = declarative_base()

# ТАБЛИЦА 1: Категории (Родительская таблица)
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    # Мостик к товарам: позволяет узнать все товары этой категории
    products = relationship("Product", back_populates="category")

# ТАБЛИЦА 2: Товары (Дочерняя таблица)
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)

    # ВНЕШНИЙ КЛЮЧ: хранит ID категории из таблицы categories
    category_id = Column(Integer, ForeignKey("categories.id"))

    # Мостик к категории: позволяет достать название категории прямо из товара
    category = relationship("Category", back_populates="products")

# Создаем обе таблицы в базе
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# Заполняем базу, если она пустая
if session.query(Category).count() == 0:
    # 1. Сначала создаем категории
    light = Category(name="Легкий табак")
    medium = Category(name="Средний табак")
    strong = Category(name="Крепкий табак")

    # 2. Создаем товары и сразу привязываем их к объектам категорий!
    item1 = Product(name="Darkside Core", price=1400, category=medium)
    item2 = Product(name="Musthave Pinkman", price=1450, category=medium)
    item3 = Product(name="Tangiers Birquq", price=2500, category=strong)

    session.add_all([medium, strong, item1, item2, item3])
    session.commit()
    print("Связанные таблицы успешно созданы и заполнены!")

# --- МАГИЯ №1: Читаем данные из двух таблиц сразу ---
print("\n--- ВСЕ ТОВАРЫ И ИХ КАТЕГОРИИ ---")
all_items = session.query(Product).all()
for item in all_items:
    # Мы берем имя товара из таблицы products, а имя категории — из таблицы categories!
    print(f"Товар: {item.name} ({item.price} руб.) | Категория: {item.category.name}")

# --- МАГИЯ №2: Настоящий JOIN-запрос ---
# Допустим, клиент просит показать ТОЛЬКО "Средний табак".
# Мы объединяем (join) таблицу Product с таблицей Category и фильтруем по имени категории:
print("\n--- РЕЗУЛЬТАТ JOIN-ЗАПРОСА (Только Средний табак) ---")
medium_tobaccos = session.query(Product).join(Category).filter(Category.name == "Средний табак").all()

for item in medium_tobaccos:
    print(f"- {item.name}: {item.price} руб.")