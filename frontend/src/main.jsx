import React from "react";
import { createRoot } from "react-dom/client";

import App from "./App";
import "./styles.css";

// Initialize the root element and render the main application
const rootElement = document.getElementById("root");
const root = createRoot(rootElement);

// Render the application within React's StrictMode for additional checks
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);