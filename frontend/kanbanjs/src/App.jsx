import { useState, useRef, useEffect } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import ManagementPanel from './kanban_management_menu_react.jsx'
import './App.css'
import './card.css'
import KanbanContainer from './kanban_container_react.jsx'
import CreateCardDialog from './form_react.jsx'
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
      this.id = id; // Unique identifier for the card
      this.title = title; // Title of the card
      this.description = description || ''; // Optional description
      this.assignee = assignee; // Person responsible for the task
      this.status = status; // Current status (e.g., 'To Do', 'In Progress', 'Done')
      this.dueDate = dueDate; // Due date for the task
      this.priority = priority; // Priority level (e.g., 'low', 'normal', 'high')
      this.createdAt = createdAt; // Timestamp when the card was created
      this.period = period; // regularity
//        this.regular = ;
//        this.comments = []; // Array to store comments
//        this.attachments = []; // Array to store attachments
      this.history = [{ status: this.status, timestamp: this.createdAt }]; // Track status changes
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
  
  const [state, setState] = useState(STATE_CREATE_CARD)
  const [showInvisibleColumns, setShowInvisibleColumns] = useState(false)
  const [kanban, setKanban] = useState({'columns': [], 'cards': []});
  const [selectedCard, setSelectedCard] = useState(null);
  const [visible, setFormVisible] = useState(false);
  const [isDraggingBoard, setIsDraggingBoard] = useState(false);
  // const [cardPosition, setCardPosition] = useState({'x': 0, 'y':0});

  
  return (
    <>
      <ManagementPanel 
        setState={setState} 
        setFormVisible={setFormVisible} 
        setShowInvisibleColumns={setShowInvisibleColumns}
        selectedCard={selectedCard}
        setCards={(data)=> {
          let kanban = new Kanban();            
          kanban.cards = data.cards.map(cardData => {
              const card = new Card();
              Object.assign(card, cardData);
              return card;
          });
          setKanban({ columns: kanban.columns, cards: kanban.cards});
        }}
        />
      <KanbanContainer 
        showInvisibleColumns={showInvisibleColumns} 
        kanban={kanban}
        setSelected={setSelectedCard}
        selected={selectedCard}
        isDraggingBoard={isDraggingBoard}
        setIsDraggingBoard={setIsDraggingBoard}
        />
      <CreateCardDialog mode={state} 
        visible={visible} 
        setFormVisible={setFormVisible}/>
    </>
  )
}

export default App
