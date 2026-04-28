import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import "./styles.css";

// Render the main App component inside the root element
createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
