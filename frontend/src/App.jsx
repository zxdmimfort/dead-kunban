import { useState, useRef, useEffect } from "react";
import ManagementPanel from "./components/ManagementMenu.jsx";
import "./App.css";
import "./card.css";
import KanbanС from "./components/Kanban.jsx";
import CreateCardDialog from "./components/Dialog.jsx";
import Card from "./Card.jsx";

class Kanban {
  constructor() {
    this.cards = [];
  }
}

export const STATE_CREATE_CARD = "CREATE";
export const STATE_UPDATE_CARD = "UPDATE";

export function showGently(element) {
  if (element) {
    element.style.opacity = "0";
    element.style.display = "";
    element.style.transition = "opacity 0.5s";
    setTimeout(() => {
      element.style.display = "inline";
      element.style.opacity = "1";
    }, 100);
  }
}

export function hideGently(element) {
  if (element) {
    element.style.opacity = "1";
    element.style.transition = "opacity 0.5s";
    setTimeout(() => {
      element.style.opacity = "0";
      setTimeout(() => {
        element.style.display = "none";
      }, 500);
    }, 100);
  }
}

function App() {
  const [mode, setMode] = useState(STATE_CREATE_CARD);
  const [showInvisibleColumns, setShowInvisibleColumns] = useState(false);
  const [kanban, setKanban] = useState({ columns: [], cards: [] });
  const selectedCardUseState = useState(null);
  const [visible, setFormVisible] = useState(false);
  const draggingBoardUseState = useState(false);

  function setCards(data) {
    let kanban = new Kanban();
    kanban.cards = data.cards.map((cardData) => {
      const card = new Card();
      Object.assign(card, cardData);
      return card;
    });
    setKanban({ cards: kanban.cards });
  }

  const formDataUseState = useState({
    title: "",
    description: "",
    assignee: "",
    status: "",
    dueDate: "",
    priority: "normal",
    period: "-1",
    // createdAt: new Date()
  });

  return (
    <>
      <ManagementPanel
        setState={setMode}
        setFormVisible={setFormVisible}
        setShowInvisibleColumns={setShowInvisibleColumns}
        selectedCardUseState={selectedCardUseState}
        formDataUseState={formDataUseState}
        setCards={setCards}
        draggingBoardUseState={draggingBoardUseState}
      />
      <KanbanС
        kanban={kanban}
        setCards={setCards}
        showInvisibleColumns={showInvisibleColumns}
        selectedCardUseState={selectedCardUseState}
        draggingBoardUseState={draggingBoardUseState}
      />

      <CreateCardDialog
        mode={mode}
        formDataUseState={formDataUseState}
        visible={visible}
        setFormVisible={setFormVisible}
        selectedCardUseState={selectedCardUseState}
      />
    </>
  );
}

export default App;
