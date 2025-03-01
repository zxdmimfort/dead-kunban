from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db_models import Base

# ...existing code...


def get_engine(db_path="database.db"):
    """Возвращает объект Engine для подключения к SQLite с использованием SQLAlchemy."""
    engine = create_engine(f"sqlite:///{db_path}", echo=True)
    return engine


def get_session(engine):
    """Возвращает новую сессию для работы с базой данных."""
    Session = sessionmaker(bind=engine)
    return Session


if __name__ == "__main__":
    engine = get_engine()
    # Создаем таблицы, если они не существуют
    Base.metadata.create_all(engine)

    # Пример использования сессии
    session = get_session(engine)

    # Добавим пример записи, если нужно
    # example_entry = Example(name="Пример")
    # session.add(example_entry)
    # session.commit()
    # session.close()
