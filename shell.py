from src.config import get_engine, get_session
from src.db_models import Base, HistoryRecord, KanbanCard  # Импортируйте свои модели
import IPython

engine = get_engine()
Session = get_session(engine)

# Определяем переменные, доступные в сессии шелла
locals_dict = globals().copy()
locals_dict.update(
    {
        "engine": engine,
        "Session": Session,
        "Base": Base,
        "KanbanCard": KanbanCard,
        "HistoryRecord": HistoryRecord,
    }
)

IPython.start_ipython(argv=[], user_ns=locals_dict)
