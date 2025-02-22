import { hideGently, showGently, STATE_CREATE_CARD as MODE_CREATE_CARD, STATE_CREATE_CARD, STATE_UPDATE_CARD as MODE_UPDATE_CARD } from './App';
import './card.css';

import { useState, useEffect, useRef } from 'react'
import { postUrl, putUrl } from './requests';



const DialogContainer = (props) => {
    const { children, display, opacity, translate } = props;
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
    <div className="dialog-container draggable" style={{ ...existingStyle, ...containerStyle,
      top: translate.y,
      left: translate.x
     }}>
      {children}
    </div>
  );
};

const DialogHeader = (props) => {
  const {isDraggingForm, setTranslate, translate, lastPos, setLastPos} = props;
  const delta = useRef({ 'x': 0, 'y':0 });

  return <div className="dialog-header" 

    onMouseUp={(e)=>{    
      isDraggingForm.current = false;
    }}

    onMouseDown={(e)=> { 
        e.preventDefault()
        isDraggingForm.current = true;   

        setLastPos({x: e.clientX, y: e.clientY})
    }}      
    
    onMouseMove={(e)=>{
      if (isDraggingForm.current){
          e.preventDefault();
          const deltaX = e.clientX - lastPos.x;
          const deltaY = e.clientY - lastPos.y;

          setTranslate((prevTranslate) => ({
            x: prevTranslate.x + deltaX,
            y: prevTranslate.y + deltaY,
          }));

          setLastPos({ x: e.clientX, y: e.clientY });
      }
    }
  }
  >{props.title}</div>;
};


const CardForm = ({ onSubmit, formDataUseState }) => {
  const [formData, setFormData] = formDataUseState;


  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };



  return (
    <div className="dialog-body">
    <form id="cardForm" onSubmit={onSubmit}>
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
        defaultValue="todo"
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
        defaultValue="low"
        value={formData.priority}
        onChange={handleChange}
      >
        <option value="low">Low</option>
        <option value="normal">
          Normal
        </option>
        <option value="high">High</option>
      </select>
    </form>  
    </div>
    );
};


const DialogFooter = ({ onSubmit, onCancel, mode, visible }) => {
  const butt = () => {
    if ( { visible } ){
      return ( mode  == MODE_CREATE_CARD)? (<button className="create" onClick={onSubmit}>Create</button>) : 
        (<button className="update" onClick={onSubmit}>Update</button>)

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

const CreateCardDialog = (props) => {
  const {mode, visible, setFormVisible, formDataUseState, selectedCardUseState} = props
  const [opacity, setOpacity] = useState(1);
  const [display, setDisplay] = useState('inline');
  const [selected, setSelected] = selectedCardUseState;

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

  const isDraggingForm = useRef(false)
  const [lastPos, setLastPos] = useState({'x': 0, 'y': 0});
  const translateUseState = useState({'x': 0, 'y': 0})
  const [translate, setTranslate] = translateUseState;


const handleSubmit = (e) => {
  // console.log(formData)
  if (mode==MODE_CREATE_CARD)
    postUrl('http://127.0.0.1:8000/api/cards', formData)

  if (mode== MODE_UPDATE_CARD){
    putUrl(`http://127.0.0.1:8000/api/cards/${selected.id}`, formData)
    }


};
const [formData, setFormData] = formDataUseState;

return(
  <DialogContainer display={display} opacity={opacity} 
  translate={translate} 
  lastPos={lastPos} 
  isDraggingForm={isDraggingForm}>
    <DialogHeader title="Create Card"
    translate={translate} 
    setTranslate={setTranslate} 
    setLastPos={setLastPos} 
    lastPos={lastPos} 
    isDraggingForm={isDraggingForm}
    />
    <CardForm formDataUseState={formDataUseState} style={{  padding: "20px",maxHeight: "300px",overflowY: "auto"}} />
    <DialogFooter
      mode={mode} 
      visible={visible}
      onCancel={() => {
        setFormVisible(false);
      }}
      onSubmit={handleSubmit}
    />
  </DialogContainer>
);
};

export default CreateCardDialog;