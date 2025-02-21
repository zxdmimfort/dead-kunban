import { useState, useEffect, useRef } from 'react'
import Card from './App';
import ColumnC from './ColumnC';
const KanbanС = (props) => {
  const {  
    showInvisibleColumns, 
    selectedCardUseState,
    draggingBoardUseState
  } = props

  const {kanban} = props



  const [draggingEnabled, setEnableDragging] = draggingBoardUseState;
  const [isDraggingBoard, setIsDraggingBoard] = useState(false);

  const [scale, setScale] = useState(1);
  const [lastPos, setLastPos] = useState({'x': 0, 'y': 0});
  const [translate, setTranslate] = useState({'x': 0, 'y': 0});

  const [translateCard, setTranslateCard] = useState({'x': 0, 'y': 0});

  const handleZoomIn = () => {
    setScale((prevScale) => Math.min(prevScale + 0.1, 2));
  };

  const handleZoomOut = () => {
    setScale((prevScale) => Math.max(prevScale - 0.1, 0.1));
  };

  const populate = (kanban) => {
    function constructColumns() {
      const data = {
        selectedCardUseState: selectedCardUseState,
        translate: translateCard ,
        scale: scale,
        setTranslate: setTranslateCard,

        kanban: kanban
      }
      const colDict = {
        'todo': 'To Do',
        'inprogress': 'In Progress',
        'done': 'Done'
      };
      return Object.entries(colDict).map(([key, value]) => (
        <ColumnC {...data} status={key} title={value} kanban={kanban}/>
      ));
    }
    return (constructColumns());
  };

  
  return (
    <div
      className="kanban-container"
      id="kanbanContainer"

      style={{ 
        position: "relative",
        width: "100vw",
        height: "100vh",
        overflow: "hidden",
        touchAction: "none"
       }}

      onMouseUp={(e)=>{        
        setIsDraggingBoard(false)
        setLastPos({x:e.clientX, y:e.clientY})
      }} 

      onMouseDown={(e)=> {  
        if (e.button == 1) {
          e.preventDefault()
          setIsDraggingBoard(true);    
          setLastPos({x:e.clientX, y:e.clientY})    
        }
      }}

      onMouseMove={(e)=>{
        if (isDraggingBoard){
          const dx = e.clientX - lastPos.x;
          const dy = e.clientY - lastPos.y;
          const currentTransform = window.getComputedStyle(document.querySelector('#kanbanBoard')).transform;
          const matrix = new DOMMatrix(currentTransform);
          const translateX = (matrix.e || 0) + 2 * dx;
          const translateY = (matrix.f || 0) + 5 * dy;
          setTranslate({
            x: translateX,
            y: translateY
          });
          
          setLastPos({x:e.clientX, y:e.clientY})
        }

        setTranslateCard({
          x: e.clientX,
          y: e.clientY
        });
      }}

      onWheel={(e) => {
        e.preventDefault();
        if (e.deltaY < 0) {
          handleZoomIn();
        } else {
          handleZoomOut();
        }
      }}
    >
      <div className="zoom-controls">
        <button onClick={handleZoomOut}>-</button>
        <button onClick={handleZoomIn}>+</button>
      </div>

      <div className="kanban-board" id="kanbanBoard" style={{
          position: "absolute",
          top: 0,
          left: 0,
          transformOrigin: "top left",
          transition: "transform 0.1s ease-out",
          display: "flex",
          flexDirection: "row",
          width:"100%", 
          transform:  (draggingEnabled)? `translate(${translate.x}px, ${translate.y}px) scale(${scale})` : `translate(${0}px, ${0}px) scale(${1})`
      }}>
        { populate(kanban) }
      </div>
    </div>
  );
};

export default KanbanС

