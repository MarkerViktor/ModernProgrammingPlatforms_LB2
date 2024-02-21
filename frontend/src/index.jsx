import React from 'react'
import ReactDOMClient from 'react-dom/client'
import { App } from './App'
import './main.css'
import { BrowserRouter } from 'react-router-dom'


const root = document.getElementById('root')
ReactDOMClient.createRoot(root).render(
    <React.StrictMode>
        <BrowserRouter>
            <App />
        </BrowserRouter>
    </React.StrictMode>
)