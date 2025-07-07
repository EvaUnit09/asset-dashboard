import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { BrowserRouter, Routes, Route } from 'react-router'
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
const qc = new QueryClient;
createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
    <QueryClientProvider client={qc}>
    <Routes>
        <Route path="/*" element={<App />} />
    </Routes>
    </QueryClientProvider>
    </BrowserRouter>
  </StrictMode>,
)
