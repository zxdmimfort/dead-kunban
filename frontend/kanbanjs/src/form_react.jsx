import { hideGently, showGently, STATE_CREATE_CARD as MODE_CREATE_CARD } from './App';
import './card.css';

import { useState, useEffect, useRef } from 'react'




const DialogContainer = ({ children, display, opacity }) => {

    const existingStyle = {
      
      position: "fixed",
      width: "350px",
      maxWidth: "90%",
      background: "#fff",
      border: "1px solid #ccc",
      boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
      borderRadius: "8px",
      overflow: "hidden",
      zIndex: 1000,
      top: 0,
      left: 0
  };

  const containerStyle = {
    opacity: opacity,
    display: display,
    transition: 'opacity 0.5s',
  };
  return (
    <div className="dialog-container draggable" style={{ ...existingStyle, ...containerStyle }}>
      {children}
    </div>
  );
};

const DialogHeader = ({ title }) => {
  return <div className="dialog-header">{title}</div>;
};


const CardForm = ({ onSubmit }) => {
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    assignee: "",
    status: "todo",
    dueDate: "",
    period: -1,
    priority: "normal",
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handleSubmit = (e) => {
    // e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="dialog-body">
    <form id="cardForm" onSubmit={handleSubmit}>
      <label htmlFor="title">Title:</label>
      <input
        type="text"
        id="title"
        name="title"
        required
        value={formData.title}
        onChange={handleChange}
      />

      <label htmlFor="description">Description:</label>
      <textarea
        id="description"
        name="description"
        rows="3"
        value={formData.description}
        onChange={handleChange}
      ></textarea>

      <label htmlFor="assignee">Assignee:</label>
      <input
        type="text"
        id="assignee"
        name="assignee"
        value={formData.assignee}
        onChange={handleChange}
      />

      <label htmlFor="status">Status:</label>
      <select
        id="status"
        name="status"
        value={formData.status}
        onChange={handleChange}
      >
        <option value="todo">To Do</option>
        <option value="inprogress">In Progress</option>
        <option value="done">Done</option>
      </select>

      <label htmlFor="dueDate">Due Date:</label>
      <input
        type="date"
        id="dueDate"
        name="dueDate"
        value={formData.dueDate}
        onChange={handleChange}
      />

      <label htmlFor="period">Schedule every (days):</label>
      <input
        type="number"
        id="period"
        name="period"
        value={formData.period}
        onChange={handleChange}
      />

      <label htmlFor="priority">Priority:</label>
      <select
        id="priority"
        name="priority"
        value={formData.priority}
        onChange={handleChange}
      >
        <option value="low">Low</option>
        <option value="normal" selected>
          Normal
        </option>
        <option value="high">High</option>
      </select>
    </form>  
    </div>
    );
};


const DialogFooter = ({ onCancel, onCreate, onUpdate, mode, visible }) => {
  const butt = () => {
    if ( { visible } ){
      // console.log('MODE:',  mode  == MODE_CREATE_CARD);      
      // console.log('MODE:',  mode );      
      return ( mode  == MODE_CREATE_CARD)? (<button className="create" onClick={onCreate}>Create</button>) : 
        (<button className="update" onClick={onUpdate}>Update</button>)

    }
    else {
      return (<></>)
    }
  }
  return (
    <div className="dialog-footer">
      <button className="cancel" onClick={onCancel}>
        Cancel
      </button>
        { butt() }
    </div>
  );
};

const CreateCardDialog = ({mode, visible, setFormVisible}) => {
  const [opacity, setOpacity] = useState(1);
  const [display, setDisplay] = useState('inline');
  

  const handleCreate = (data) => {
    console.log("Creating card with data:", data);
  };

  const handleUpdate = (data) => {
    console.log("Updating card with data:", data);
    setFormVisible(true);
  };

  const handleCancel = () => {
    console.log("cancel")
    setFormVisible(false);
  };
  
  useEffect(() => {
    if (visible) {
      setDisplay('');
      setOpacity(0);
      setTimeout(() => {
        setDisplay('inline');
        setOpacity(1);
      }, 10);
    } else {      
      setDisplay('');
      setOpacity(1);
      setTimeout(() => {
        setDisplay('none');
        setOpacity(0);
      }, 10);
    }
  }, [visible]);

  return(
    <DialogContainer display={display} opacity={opacity} >
      <DialogHeader title="Create Card" />
      <CardForm onSubmit={handleCreate} style={{  padding: "20px",maxHeight: "300px",overflowY: "auto"}} />
      <DialogFooter
        mode={mode} 
        visible={visible}
        onCancel={handleCancel}
        onCreate={handleCreate}
        onUpdate={handleUpdate}
      />
    </DialogContainer>
  );
};

export default CreateCardDialog;