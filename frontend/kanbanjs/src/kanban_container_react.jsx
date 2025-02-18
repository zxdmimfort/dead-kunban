import { useState, useEffect, useRef } from 'react'
import Card from './App';
import CardC from './cardC';



const KanbanContainer = ({
  showInvisibleColumns, 
  kanban, 
  setSelected,  
  selected,
  isDraggingBoard, 
  setIsDraggingBoard
}) => {

  const [scale, setScale] = useState(1);
  const [lastPos, setLastPos] = useState({'x': 0, 'y': 0});
  const [translate, setTranslate] = useState({'x': 0, 'y': 0});
  const [highlightColumnWhenCardDragged, setHighlightColumnWhenCardDragged] = useState("");
  const [hightlightColumns, setHighlightColumns] = useState(false);
  const [translateCard, setTranslateCard] = useState({'x': 0, 'y': 0});

  useEffect(()=>{
    if (selected!= null)
      setHighlightColumnWhenCardDragged(selected.status)
  }, [selected])

  const handleZoomIn = () => {
    setScale((prevScale) => Math.min(prevScale + 0.1, 2));
  };

  const handleZoomOut = () => {
    setScale((prevScale) => Math.max(prevScale - 0.1, 0.1));
  };

  const populate = (kanban) => {
    const statuses = ["todo", "inprogress", "done", "rest", "archived"];

    function droppingCardInColumn(e, status){
        if (selected!=null && selected.status != status){
          selected.status = status;
        }
    }

    function cardsForColumn(status) {
      return (kanban.cards
            .filter(el => el.status == status)
            .map((el, i) => (
              <CardC
                scale={scale}
                i={i} 
                el={el} 
                selectedCard={selected} 
                setSelectedCard={setSelected}
                setHighlightColumns={setHighlightColumns} translate={translateCard} setTranslate={setTranslateCard}
              />
            )))
    }

    return (
      <>
        <div 
        className={`column ${highlightColumnWhenCardDragged=="todo" && hightlightColumns ? 'highlighted' : ''}`} 
        >
          <h3>To Do</h3>
          {cardsForColumn(statuses[0])}
        </div>

        <div 
        className={`column ${highlightColumnWhenCardDragged=="inprogress"&& hightlightColumns ? 'highlighted' : ''}`} 
        >
          <h3>In Progress</h3>
          {cardsForColumn(statuses[1])}
        </div>

        <div 
        className={`column ${highlightColumnWhenCardDragged=="done"&& hightlightColumns ? 'highlighted' : ''}`} 
        >
          <h3>Done</h3>
          {cardsForColumn(statuses[2])}
        </div>
      </>
    );
  };

  // useEffect(()=>{
  //   console.log(translate)
  // }, [isDraggingBoard])

  
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
          // e.preventDefault()
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
        // e.preventDefault();
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
          transform: `translate(${translate.x}px, ${translate.y}px) scale(${scale})`
      }}>
        { populate(kanban) }
      </div>
    </div>
  );
};

export default KanbanContainer