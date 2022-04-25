import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'
import { Ion } from "cesium";

Ion.defaultAccessToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJkOGYwNzc2ZS04MzE1LTQ1OWEtYTg3Yi1jZGUyNjNlY2I5NzciLCJpZCI6OTAwNzIsImlhdCI6MTY1MDEyMzU0NX0.t7zZ89rJtPIDADlkOT8IxC8TkIL2jDc8y33Jw5uUk2E";

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
