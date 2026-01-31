/**
 * @fileoverview Entry point for TechNova Support Portal React application.
 * Initializes the React app and renders it to the DOM using React 18's createRoot API.
 * @author TechNova Solutions
 * @version 1.0.0
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

/**
 * Create root React element and render the application.
 * Uses React 18's createRoot API for concurrent rendering features.
 * StrictMode is enabled to highlight potential problems in development.
 */
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
