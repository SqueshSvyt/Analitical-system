import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from 'react-query'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'

import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import EventMonitor from './pages/EventMonitor'
import EntityIntelligence from './pages/EntityIntelligence'
import StorylineExplorer from './pages/StorylineExplorer'
import AlertsPage from './pages/AlertsPage'
import QAPage from './pages/QAPage'

const queryClient = new QueryClient()

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Router>
          <Layout>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/events" element={<EventMonitor />} />
              <Route path="/entities" element={<EntityIntelligence />} />
              <Route path="/storylines" element={<StorylineExplorer />} />
              <Route path="/alerts" element={<AlertsPage />} />
              <Route path="/qa" element={<QAPage />} />
            </Routes>
          </Layout>
        </Router>
      </ThemeProvider>
    </QueryClientProvider>
  )
}

export default App

