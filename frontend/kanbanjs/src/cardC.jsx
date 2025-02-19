
import { useState, useEffect, useRef } from 'react'


function next_job({hours_till_todo, days_till_todo, cooldown}){
  if (days_till_todo > 0 ) {
      return (<>Следующее задание: {cooldown} (через {days_till_todo} дней )</>) ;
  } else if (hours_till_todo !=-1) {
      return (<>Следующее задание: {cooldown} (через {hours_till_todo} часа)</>) ;
  } else return ""
} 

export default function CardC({i, el, selectedCard, setSelectedCard, setHighlightColumns, translate, scale
}) {

  const [hasSelectedStyle, setSelectedStyle] = useState(false);
  const drag = useRef(false);
  const clientX=useRef(0.)
  const clientY=useRef(0.)

  useEffect(()=> {
    if (selectedCard !== el)
      setSelectedStyle(false);
    else
      setSelectedStyle(true);
    }, [mouseDown])

  function mouseDown(e) {
    e.preventDefault();
    if (e.button == 0) {
      setSelectedCard(el);
      setSelectedStyle(true);
      clientX.current = e.clientX;
      clientY.current = e.clientY;
      drag.current = true;
    }
  }

  
  function mouseUp(e) {
    const statuses = ["todo", "inprogress", "done", "rest", "archived"];

    drag.current = false;
    document.querySelectorAll('.column').forEach((el, i) => {
      const rect = el.getBoundingClientRect();
      
      function inRect(e, rect) {
        return e.clientX >= rect.left &&
          e.clientX <= rect.right &&
          e.clientY >= rect.top &&
          e.clientY <= rect.bottom;
      }

      if (inRect(e, rect)) {
        if (selectedCard.status==statuses[i]) {
          // остались где были. 
        } else {
          selectedCard.status = statuses[i];
          setSelectedCard(null);
        }
      }
    });
  }

  
  return (
  <div className={`card ${hasSelectedStyle ? 'selected' : ''}`}
    onMouseDown={mouseDown}
    onMouseUp={mouseUp}
    style = {{
      transform:(selectedCard!=null && selectedCard == el && drag.current)? `translate(${(translate.x - clientX.current)/scale}px, ${(translate.y - clientY.current)/scale}px)` : ''
    }}
    >
      <h5>{el.title}</h5> {el.description} 
      <span style={{fontSize: "10px"}}>
        Период оборота: 
        </span>
      <span style={{fontSize: "7px", fontWeight: 700}}> {el.period}</span> дней {next_job(el)} 
      Последний статус: {el.history_as_string}  
    </div>
  );  
} 


