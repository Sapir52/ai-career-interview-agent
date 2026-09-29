// React application bootstrap. Mounts the root App component into index.html.
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles.css';
// StrictMode helps surface unsafe React patterns during development.
ReactDOM.createRoot(document.getElementById('root')!).render(<React.StrictMode><App/></React.StrictMode>);
