import React from "react";

const ContextMenu = ({ hidden, position, children }) => {
  return (
    <div
      id="management-panel"
      className={`${hidden ? "context-menu hidden" : "context-menu"}`}
      style={{
        left: `${position.x}px`,
        top: `${position.y}px`,
      }}
    >
      <ul>{children}</ul>
    </div>
  );
};

export default ContextMenu;
