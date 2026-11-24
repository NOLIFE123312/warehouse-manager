from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

# check_same_thread=False защищает от ошибок при работе SQLite из разных потоков (FastAPI и asyncio.to_thread)
engine = create_engine(
    "sqlite:///warehouse_db.sqlite",
    connect_args={"check_same_thread": False}
)
Base = declarative_base()


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    stock = Column(Integer, default=0)


# Создаст таблицу автоматически, какой бы из файлов проекта ни запустился первым
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)