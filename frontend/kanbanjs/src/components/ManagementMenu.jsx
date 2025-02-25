import { useState, useEffect, useRef } from "react";
import { STATE_CREATE_CARD, STATE_UPDATE_CARD } from "../App";
import { getUrl } from "../requests";

import { postUrl, deleteUrl, putUrl } from "../requests";

const ManagementPanel = (props) => {
  const {
    setState,
    setFormVisible,
    setShowInvisibleColumns,
    draggingBoardUseState,
    formDataUseState,
  } = props;

  const { setCards } = props;
  const { selectedCardUseState } = props;
  const [selected, setSelected] = selectedCardUseState;

  const [formData, setFormData] = formDataUseState;

  const [mouseCoordinates, setMouseCoordinates] = useState({ x: 0, y: 0 });
  const [draggingEnabled, setEnableDragging] = draggingBoardUseState; // checkbox for enabling board dragging
  const [hidden, setHidden] = useState(true);
  const kanban_invisible = useRef(null);
  const handleCreateCard = () => {
    console.log("Create card action triggered");
    setState(STATE_CREATE_CARD);
    setFormVisible(true);
  };

  const handleEditCard = () => {
    console.log("Edit card action triggered");
    setState(STATE_UPDATE_CARD);
    if (selected != null)
      setFormData({
        title: selected.title,
        description: selected.description,
        assignee: selected.assignee,
        status: selected.status,
        dueDate: selected.dueDate,
        priority: selected.priority,
        period: selected.period,
        // createdAt: new Date()
      });
    setFormVisible(true);
  };

  const handleDelete = () => {
    console.log("Delete action triggered");
    deleteUrl(`http://127.0.0.1:8000/api/cards/${selected.id}`, {}).then(() =>
      getUrl("http://127.0.0.1:8000/api/cards").then((data) => {
        console.log("Fetched data:", data);
        setCards(data);
      }),
    );
  };

  const handleDuplicate = () => {
    console.log("Duplicate action triggered");
    console.log({ selected });
    if (selected != null) {
      setFormData({
        title: selected.title,
        description: selected.description,
        assignee: selected.assignee,
        status: selected.status,
        dueDate: selected.dueDate,
        priority: selected.priority,
        period: selected.period,
        // createdAt: new Date()
      });
      postUrl(`http://127.0.0.1:8000/api/cards`, formData).then(() =>
        getUrl("http://127.0.0.1:8000/api/cards").then((data) => {
          setCards(data);
        }),
      );
    }
  };

  const handleSync = () => {
    console.log("Sync action triggered");
    getUrl("http://127.0.0.1:8000/api/cards").then((data) => {
      console.log("Fetched data:", data);
      setCards(data);
    });
  };

  const handleToggleDraggingBoard = () => {
    setEnableDragging((prev) => !prev);
  };

  const toggle = (event) => {
    const contextMenu = document.getElementById("management-panel");
    if (contextMenu) {
      event.preventDefault();
      setMouseCoordinates({ x: event.clientX, y: event.clientY });

      setHidden((prev) => !prev);
    }
  };

  const handleClickOutside = (e) => {
    const contextMenu = document.getElementById("management-panel");
    if (contextMenu) {
      setHidden(true);
    }
  };

  useEffect(() => {
    document.addEventListener("contextmenu", toggle);
    document.addEventListener("click", handleClickOutside);

    return () => {
      document.removeEventListener("contextmenu", toggle);
      document.removeEventListener("click", handleClickOutside);
    };
  }, []);

  return (
    <div
      id="management-panel"
      className={`${hidden ? "context-menu hidden" : "context-menu"}`}
      style={{
        left: `${mouseCoordinates.x}px`,
        top: `${mouseCoordinates.y}px`,
      }}
    >
      <ul>
        <li onClick={handleSync}>sync</li>
        <li onClick={handleCreateCard}>create</li>
        <li onClick={handleEditCard}>edit</li>
        <li onClick={handleDelete}>delete</li>
        <li onClick={handleDuplicate}>duplicate</li>
        <li>
          <label
            htmlFor="kanban_dragging"
            style={{ marginTop: "10px", cursor: "pointer" }}
          >
            Enable dragging columns
            <input
              type="checkbox"
              id="kanban_dragging"
              ref={kanban_invisible}
              onChange={handleToggleDraggingBoard}
              style={{ marginLeft: "10px" }}
            />
          </label>
        </li>
      </ul>
    </div>
  );
};

export default ManagementPanel;
