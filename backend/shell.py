from src.config import get_engine, get_session
from src.db_models import (
    Base,
    HistoryRecord,
    KanbanCard,
    User,
)
import IPython

engine = get_engine()
Session = get_session(engine)


def create_all():
    Base.metadata.create_all(engine)


locals_dict = globals().copy()
locals_dict.update(
    {
        "engine": engine,
        "Session": Session,
        "Base": Base,
        "KanbanCard": KanbanCard,
        "HistoryRecord": HistoryRecord,
        "User": User,
        "create_all": create_all,
    }
)

IPython.start_ipython(argv=[], user_ns=locals_dict)
