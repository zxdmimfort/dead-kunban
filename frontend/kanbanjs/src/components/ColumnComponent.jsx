import { useState, useEffect, useRef } from "react";

import { CardComponent } from "./CardComponent.jsx";

export default function ColumnComponent(data) {
  const { cards, selectedCardUseState, translateCard, setTranslateCard } = data;
  const ref = useRef(null);

  const hoverUseState = useState(false);
  const [hover, setHover] = hoverUseState;

  useEffect(() => {
    const handleCardOver = (event) => {
      setHover(true);
    };
    const handleCardLeave = (event) => {
      setHover(false);
    };
    if (ref.current) {
      ref.current.addEventListener("card-over", handleCardOver);
      ref.current.addEventListener("card-leave", handleCardLeave);
    }

    const mouseup = () => {
      setHover(false);
    };
    document.addEventListener("mouseup", mouseup);

    return () => {
      if (ref.current) {
        ref.current.removeEventListener("card-over", handleCardOver);
        ref.current.addEventListener("card-leave", handleCardLeave);
      }
    };
  }, []);

  const { status, title } = data;

  return (
    <>
      <div ref={ref} className={`column ${hover ? "card-hover" : ""}`}>
        <h3>{title}</h3>
        {cards.map((el) => (
          <CardComponent key={el.id} {...data} el={el} />
        ))}
      </div>
    </>
  );
}
