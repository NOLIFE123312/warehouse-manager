from fastembed import TextEmbedding
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from database import Product, Session

# 2. Инициализируем нейросеть смыслов, Qdrant и клиент Ollama один раз при старте
print("⏳ Загружаем RAG-модуль (FastEmbed + Qdrant)...")
embed_model = TextEmbedding(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)
qdrant = QdrantClient(":memory:")
llm_client = OpenAI(
    api_key="ollama",
    base_url="http://localhost:11434/v1"
)

COLLECTION_NAME = "tobacco_knowledge"


def get_vector(text: str) -> list[float]:
    return list(embed_model.embed([text]))[0].tolist()


# 3. Загружаем актуальные остатки из SQLite в векторную базу Qdrant
def sync_db_to_qdrant() -> int:
    db = Session()
    # Берем ТОЛЬКО те товары, у которых остаток больше 0
    products = db.query(Product).filter(Product.stock > 0).all()
    db.close()

    # Пересоздаем коллекцию, чтобы убрать проданные и удаленные позиции
    if qdrant.collection_exists(COLLECTION_NAME):
        qdrant.delete_collection(COLLECTION_NAME)

    qdrant.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE)
    )

    if not products:
        return 0

    points = [
        PointStruct(
            id=item.id,
            vector=get_vector(f"{item.name}. Цена: {item.price} руб. В наличии: {item.stock} шт."),
            payload={
                "name": item.name,
                "price": item.price,
                "stock": item.stock
            }
        )
        for item in products
    ]

    qdrant.upsert(collection_name=COLLECTION_NAME, points=points)
    return len(points)


# 4. Главная функция RAG для FastAPI и Telegram-бота
def ask_rag(question: str) -> dict:
    # Синхронизируемся с реальной базой перед поиском
    available_count = sync_db_to_qdrant()

    if available_count == 0:
        return {
            "question": question,
            "matched_tobaccos": [],
            "ai_answer": "На складе сейчас нет табаков в наличии (все остатки на нуле)."
        }

    # Ищем топ-3 подходящих товара из актуального наличия
    results = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=get_vector(question),
        limit=3
    ).points

    context_lines = []
    matched_names = []
    for hit in results:
        matched_names.append(hit.payload["name"])
        context_lines.append(
            f"- {hit.payload['name']} | Цена: {hit.payload['price']} руб. | В наличии: {hit.payload['stock']} шт."
        )

    retrieved_context = "\n".join(context_lines)

    response = llm_client.chat.completions.create(
        model="qwen2.5:3b",
        temperature=0.3,
        messages=[
            {
                "role": "system",
                "content": (
                    "Ты опытный кальянный мастер и помощник по складу. "
                    "Отвечай кратко и по делу на русском языке, используя ТОЛЬКО товары "
                    "из переданного списка наличия. Если уместно, указывай цену и остаток. "
                    "Если подходящего товара нет, честно скажи об этом и ничего не выдумывай."
                )
            },
            {
                "role": "user",
                "content": f"Актуальное наличие на складе:\n{retrieved_context}\n\nВопрос: {question}"
            }
        ]
    )

    return {
        "question": question,
        "matched_tobaccos": matched_names,
        "ai_answer": response.choices[0].message.content
    }


print("✅ RAG-модуль подключен к warehouse_db.sqlite!")


if __name__ == "__main__":
    test_result = ask_rag("Что есть из фруктового и сколько стоит?")
    print("Найдено в SQLite:", test_result["matched_tobaccos"])
    print("\nОтвет ИИ:\n", test_result["ai_answer"])