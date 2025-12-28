import { useEffect, useState } from 'react'
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  CircularProgress,
} from '@mui/material'
import {
  Article as ArticleIcon,
  Event as EventIcon,
  People as PeopleIcon,
  TrendingUp,
} from '@mui/icons-material'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts'
import { statsApi, eventApi } from '../services/api'

export default function Dashboard() {
  const [stats, setStats] = useState<any>(null)
  const [eventTypes, setEventTypes] = useState<any[]>([])
  const [trends, setTrends] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      const [statsRes, eventTypesRes, trendsRes] = await Promise.all([
        statsApi.getOverview(),
        statsApi.getEventTypeDistribution(),
        eventApi.getEventTrends({ granularity: 'day' }),
      ])
      
      setStats(statsRes.data)
      setEventTypes(eventTypesRes.data.slice(0, 10))
      setTrends(trendsRes.data)
    } catch (error) {
      console.error('Error loading dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    )
  }

  const statCards = [
    {
      title: 'Total Articles',
      value: stats?.total_articles || 0,
      icon: <ArticleIcon fontSize="large" />,
      color: '#1976d2',
    },
    {
      title: 'Total Events',
      value: stats?.total_events || 0,
      icon: <EventIcon fontSize="large" />,
      color: '#dc004e',
    },
    {
      title: 'Total Entities',
      value: stats?.total_entities || 0,
      icon: <PeopleIcon fontSize="large" />,
      color: '#f57c00',
    },
    {
      title: 'Date Range',
      value: stats?.date_range?.earliest ? 
        `${new Date(stats.date_range.earliest).toLocaleDateString()} - ${new Date(stats.date_range.latest).toLocaleDateString()}` : 
        'N/A',
      icon: <TrendingUp fontSize="large" />,
      color: '#388e3c',
    },
  ]

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {statCards.map((card, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography color="textSecondary" gutterBottom variant="body2">
                      {card.title}
                    </Typography>
                    <Typography variant="h5">
                      {card.value}
                    </Typography>
                  </Box>
                  <Box sx={{ color: card.color }}>
                    {card.icon}
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Event Type Distribution */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Event Type Distribution
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={eventTypes}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="event_type" angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#1976d2" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Event Trends */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Event Trends (Last 30 Days)
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={trends.slice(-30)}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="count" stroke="#dc004e" />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}

