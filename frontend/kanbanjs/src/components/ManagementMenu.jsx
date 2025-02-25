import { useState, useEffect, useRef } from "react";
import { STATE_CREATE_CARD, STATE_UPDATE_CARD } from "../App";
import { getUrl, postUrl, deleteUrl, putUrl } from "../requests";
import ContextMenu from "./ContextMenu";
import ContextMenuItem from "./ContextMenuItem";

// Helper function to extract form data from a card.
const extractCardData = (card) => ({
  title: card.title,
  description: card.description,
  assignee: card.assignee,
  status: card.status,
  dueDate: card.dueDate,
  priority: card.priority,
  period: card.period,
});

const ManagementPanel = ({
  setState,
  setFormVisible,
  setShowInvisibleColumns,
  draggingBoardUseState,
  formDataUseState,
  setCards,
  selectedCardUseState,
}) => {
  const [selected, setSelected] = selectedCardUseState;
  const [formData, setFormData] = formDataUseState;
  const [mouseCoordinates, setMouseCoordinates] = useState({ x: 0, y: 0 });
  const [draggingEnabled, setEnableDragging] = draggingBoardUseState;
  const [hidden, setHidden] = useState(true);
  const kanban_invisible = useRef(null);

  const refreshCards = () => {
    getUrl("http://127.0.0.1:8000/api/cards").then((data) => {
      console.log("Fetched data:", data);
      setCards(data);
    });
  };

  const handleCreateCard = () => {
    console.log("Create card action triggered");
    setState(STATE_CREATE_CARD);
    setFormVisible(true);
  };

  const handleEditCard = () => {
    console.log("Edit card action triggered");
    setState(STATE_UPDATE_CARD);
    if (selected != null) {
      setFormData(extractCardData(selected));
    }
    setFormVisible(true);
  };

  const handleDelete = () => {
    console.log("Delete action triggered");
    deleteUrl(`http://127.0.0.1:8000/api/cards/${selected.id}`, {}).then(
      refreshCards,
    );
  };

  const handleDuplicate = () => {
    console.log("Duplicate action triggered");
    if (selected != null) {
      postUrl(
        `http://127.0.0.1:8000/api/cards`,
        extractCardData(selected),
      ).then(refreshCards);
    }
  };

  const handleSync = () => {
    console.log("Sync action triggered");
    refreshCards();
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

  const menuItems = [
    { label: "sync", onClick: handleSync },
    { label: "create", onClick: handleCreateCard },
    { label: "edit", onClick: handleEditCard },
    { label: "delete", onClick: handleDelete },
    { label: "duplicate", onClick: handleDuplicate },
  ];

  return (
    <ContextMenu hidden={hidden} position={mouseCoordinates}>
      {menuItems.map((item) => (
        <ContextMenuItem
          key={item.label}
          label={item.label}
          onClick={item.onClick}
        />
      ))}
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
    </ContextMenu>
  );
};

export default ManagementPanel;
