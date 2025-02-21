import { useState, useRef, useEffect } from 'react'
import ManagementPanel from './ManagementMenu.jsx'
import './App.css'
import './card.css'
import KanbanС from './Kanban.jsx'
import CreateCardDialog from './Dialog.jsx'
import Card from './Card.jsx'


class Kanban {
  constructor() {
      this.cards = []
  }
};


export const STATE_CREATE_CARD = "CREATE";
export const STATE_UPDATE_CARD = "UPDATE";

export function showGently(element) {
  if (element) {
      element.style.opacity = '0';
      element.style.display = '';
      element.style.transition = 'opacity 0.5s';
      setTimeout(() => {
          element.style.display = 'inline';
          element.style.opacity = '1';
      }, 100);
  }
}

export function hideGently(element) {
  if (element) {
      element.style.opacity = '1';
      element.style.transition = 'opacity 0.5s';
      setTimeout(() => {
          element.style.opacity = '0';
          setTimeout(() => {
              element.style.display = 'none';
          }, 500);
      }, 100);
  }
}

function App() {
  
  const [mode, setMode] = useState(STATE_CREATE_CARD)
  const [showInvisibleColumns, setShowInvisibleColumns] = useState(false)
  const [kanban, setKanban] = useState({'columns': [], 'cards': []});
  const selectedCardUseState = useState(null);
  const [visible, setFormVisible] = useState(false);
  const draggingBoardUseState= useState(false)

  return (
    <>
      <ManagementPanel 
        setState={setMode} 
        setFormVisible={setFormVisible} 
        setShowInvisibleColumns={setShowInvisibleColumns}
        selectedCardUseState={selectedCardUseState}
        setCards={(data)=> {
          let kanban = new Kanban();            
          kanban.cards = data.cards.map(cardData => {
              const card = new Card();
              Object.assign(card, cardData);
              return card;
          });
          setKanban({ cards: kanban.cards });
        }}
        draggingBoardUseState={draggingBoardUseState}
      />

      <KanbanС 
        kanban={kanban}

        showInvisibleColumns={showInvisibleColumns} 

        selectedCardUseState={selectedCardUseState}
        draggingBoardUseState={draggingBoardUseState}
        />
      <CreateCardDialog mode={mode} 
        visible={visible} 
        setFormVisible={setFormVisible}/>
    </>
  )
}

export default App
