import React from "react";

const ContextMenuItem = ({ label, onClick }) => {
  return <li onClick={onClick}>{label}</li>;
};

export default ContextMenuItem;
