import { useState, useEffect, useRef } from 'react'
import { STATE_CREATE_CARD, STATE_UPDATE_CARD } from './App';
import { getUrl } from './requests';
const ManagementPanel = ({setState, setFormVisible, setShowInvisibleColumns, setCards, selectedCard}) => {
  const kanban_invisible = useRef(null);

  const handleCreateCard = () => {
    console.log("Create card action triggered");
    setState(STATE_CREATE_CARD)
    setFormVisible(true)
  };

  const handleEditCard = () => {
    console.log("Edit card action triggered");
    setState(STATE_UPDATE_CARD)
    setFormVisible(true)
  };

  const handleDelete = () => {
    console.log("Delete action triggered");
//    if (draggableBoard.selectedCard!== null){
//        this.model.cards.splice( draggableBoard.selectedID, 1 );
//        this.push();
//        this.sync();
//    }
  };

  const handleDuplicate = () => {
    console.log("Duplicate action triggered");

//    if (draggableBoard.selectedCard !== null){
//        this.model.cards.splice(draggableBoard.selectedID, 0, draggableBoard.selectedCardModel);
//        this.push();
//        this.sync();
//    }
  };

  // useEffect(() => {
  //   if (data) {
  //     console.log("datka:" +data);
  //     setCards(data);
  //   }
  // }, [data,setData]);

  const handleSync = () => {
    console.log("Sync action triggered");
    getUrl('http://127.0.0.1:5000/kanban_pull')
    .then(data => {
      console.log('Fetched data:', data);
      setCards(data);
    })
    // .catch(error => {
    //   console.error('Error fetching data:', error.message);
    // });
  }

  const handlePush = () => {
    console.log("Duplicate action triggered");

  }

  const handleToggleInvisibleColumns = () => {
    setShowInvisibleColumns((prev) => !prev);
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
      <button id="kanban_push" onClick={handlePush}>
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

      <a href="/kanban_pull" style={{ marginTop: "10px", textDecoration: "none" }}>
        <button onClick={handleExport}>Export</button>
      </a>



    </div>
  );
};

export default ManagementPanel;