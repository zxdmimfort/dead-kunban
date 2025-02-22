import { useState, useEffect, useRef } from 'react'
import { STATE_CREATE_CARD, STATE_UPDATE_CARD } from './App';
import { getUrl } from './requests';

import { postUrl, deleteUrl, putUrl } from './requests';



const ManagementPanel = (props) => {

  const {setState, setFormVisible, setShowInvisibleColumns, setCards, 
    draggingBoardUseState, formDataUseState}= props

  const {selectedCardUseState} = props;
  const [selected, setSelected] = selectedCardUseState;

  const [formData, setFormData] = formDataUseState;

  const [draggingEnabled, setEnableDragging] = draggingBoardUseState // checkbox for enabling board dragging

  const kanban_invisible = useRef(null);
  const handleCreateCard = () => {
    console.log("Create card action triggered");
    setState(STATE_CREATE_CARD)
    setFormVisible(true)
  };

  const handleEditCard = () => {
    console.log("Edit card action triggered");
    setState(STATE_UPDATE_CARD)
    if (selected !=null)
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
    setFormVisible(true)
  };

  const handleDelete = () => {
    console.log("Delete action triggered");
    deleteUrl(`http://127.0.0.1:8000/api/cards/${selected.id}`, {});

  };

  const handleDuplicate = () => {
    console.log("Duplicate action triggered");
    console.log({selected});
    if (selected !=null){
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
      postUrl(`http://127.0.0.1:8000/api/cards`, formData);
    }
  };


  const handleSync = () => {
    console.log("Sync action triggered");
    getUrl('http://127.0.0.1:8000/api/cards')
    .then(data => {
      console.log('Fetched data:', data);
      setCards(data);
    })
  }

  // const handlePush = () => {
  //   console.log("Duplicate action triggered");
  // }

  const handleToggleInvisibleColumns = () => {
    setShowInvisibleColumns((prev) => !prev);
  };  
  
  const handleToggleDraggingBoard = () => {
    setEnableDragging((prev) => !prev);
  };

  const handleExport = () => {
    console.log("Export action triggered");
  };

  return (
    <div
      className="management-panel"
      style={{
        background: "#007bff",
        position: "fixed",
        zIndex: 999,
        marginRight: "5vw"
      }}
    >
      <button id="kanban_create_card" onClick={handleCreateCard}>
        Create card
      </button>
      <button id="kanban_edit_card" onClick={handleEditCard}>
        Edit card
      </button>
      <button id="kanban_delete" onClick={handleDelete}>
        Delete
      </button>
      <button id="kanban_duplicate" onClick={handleDuplicate}>
        Duplicate
      </button>
      <button id="kanban_sync" onClick={handleSync}>
        Sync
      </button>
      <button id="kanban_push">
        Push
      </button>
      <label htmlFor="kanban_invisible" style={{ marginTop: "10px", cursor: "pointer" }}>
        Show invisible columns
        <input
          type="checkbox"
          id="kanban_invisible"
          ref={kanban_invisible}
          onChange={handleToggleInvisibleColumns}
          style={{ marginLeft: "10px" }}
        />      
      </label>
        
      <label htmlFor="kanban_dragging" style={{ marginTop: "10px", cursor: "pointer" }}>
      Enable dragging columns
      <input
        type="checkbox"
        id="kanban_dragging"
        ref={kanban_invisible}
        onChange={handleToggleDraggingBoard}
        style={{ marginLeft: "10px" }}
      />
      </label>

      <a href="/kanban_pull" style={{ marginTop: "10px", textDecoration: "none" }}>
        <button onClick={handleExport}>Export</button>
      </a>
    </div>
  );
};

export default ManagementPanel;