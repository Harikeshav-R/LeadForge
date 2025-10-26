import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
<<<<<<< HEAD
import { ThemeProvider } from './components/theme-provider'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ThemeProvider defaultTheme="dark" storageKey="leadforge-ui-theme">
      <App />
    </ThemeProvider>
=======

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
>>>>>>> main-holder
  </StrictMode>,
)
