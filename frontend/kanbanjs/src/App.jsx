import { useState, useRef, useEffect } from 'react'
import ManagementPanel from './ManagementMenu.jsx'
import './App.css'
import './card.css'
import KanbanС from './Kanban.jsx'
import CreateCardDialog from './Dialog.jsx'
class Kanban {
  constructor() {
      this.columns = []
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



export class Card {
  constructor(id=0, title="", description="", assignee="", status="", dueDate="", priority = "normal", period="-1", createdAt = new Date()) {
      this.id = id;
      this.title = title;
      this.description = description || '';
      this.assignee = assignee;
      this.status = status;
      this.dueDate = dueDate;
      this.priority = priority;
      this.createdAt = createdAt; 
      this.period = period; // regularity
//        this.regular = ;
//        this.comments = [];
//        this.attachments = [];
      this.history = [{ status: this.status, timestamp: this.createdAt }];
  }

  update({ title, description, assignee, status, dueDate, priority, period }) {
      if (title !== undefined) this.title = title;
      if (description !== undefined) this.description = description;
      if (assignee !== undefined) this.assignee = assignee;
      if (status !== undefined) {
          this.setStatus(status);
      }
      if (dueDate !== undefined) this.dueDate = dueDate;
      if (priority !== undefined) this.priority = priority;
      if (period !== undefined) this.period= period;
  }
  setStatus(newStatus) {
      if (newStatus !== this.status) {
          this.history.push({ status: newStatus, timestamp: new Date() });
          this.status = newStatus;
      }
  }
  addComment(comment) {
      this.comments.push({ text: comment, timestamp: new Date() });
  }
  addAttachment(file) {
      this.attachments.push(file);
  }
  isOverdue() {
      return new Date() > this.dueDate && this.status !== 'Done';
  }
};

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
        selectedCard={selectedCardUseState}
        setCards={(data)=> {
          let kanban = new Kanban();            
          kanban.cards = data.cards.map(cardData => {
              const card = new Card();
              Object.assign(card, cardData);
              return card;
          });
          setKanban({ columns: kanban.columns, cards: kanban.cards});
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
