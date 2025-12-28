import { useState } from 'react'
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Grid,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Divider,
  Link,
} from '@mui/material'
import { Search as SearchIcon } from '@mui/icons-material'
import { eventApi } from '../services/api'

export default function EventMonitor() {
  const [events, setEvents] = useState<any[]>([])
  const [topActors, setTopActors] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [filters, setFilters] = useState({
    event_types: '',
    min_confidence: 0.5,
    limit: 50,
  })

  const handleSearch = async () => {
    try {
      setLoading(true)
      const eventTypesArray = filters.event_types
        ? filters.event_types.split(',').map(t => t.trim())
        : undefined

      const [eventsRes, actorsRes] = await Promise.all([
        eventApi.getEvents({
          event_types: eventTypesArray,
          min_confidence: filters.min_confidence,
          limit: filters.limit,
        }),
        eventApi.getTopActors({ limit: 10 }),
      ])

      setEvents(eventsRes.data)
      setTopActors(actorsRes.data)
    } catch (error) {
      console.error('Error fetching events:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Event Monitor
      </Typography>

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Event Types (comma-separated)"
              placeholder="Conflict, Diplomacy, etc."
              value={filters.event_types}
              onChange={(e) => setFilters({ ...filters, event_types: e.target.value })}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              type="number"
              label="Min Confidence"
              value={filters.min_confidence}
              onChange={(e) => setFilters({ ...filters, min_confidence: parseFloat(e.target.value) })}
              inputProps={{ min: 0, max: 1, step: 0.1 }}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              type="number"
              label="Limit"
              value={filters.limit}
              onChange={(e) => setFilters({ ...filters, limit: parseInt(e.target.value) })}
            />
          </Grid>
          <Grid item xs={12} md={2}>
            <Button
              fullWidth
              variant="contained"
              startIcon={<SearchIcon />}
              onClick={handleSearch}
              disabled={loading}
            >
              Search
            </Button>
          </Grid>
        </Grid>
      </Paper>

      <Grid container spacing={3}>
        {/* Top Actors */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Top Actors
            </Typography>
            <Divider sx={{ mb: 2 }} />
            {topActors.map((actor, index) => (
              <Card key={index} sx={{ mb: 1 }}>
                <CardContent sx={{ py: 1, '&:last-child': { pb: 1 } }}>
                  <Typography variant="subtitle2">
                    {actor.text}
                  </Typography>
                  <Box display="flex" alignItems="center" gap={1} mt={0.5}>
                    <Chip label={actor.label} size="small" />
                    <Typography variant="caption" color="textSecondary">
                      {actor.event_count} events
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            ))}
          </Paper>
        </Grid>

        {/* Events List */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Events ({events.length})
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            {loading ? (
              <Box display="flex" justifyContent="center" p={4}>
                <CircularProgress />
              </Box>
            ) : (
              <Box sx={{ maxHeight: '600px', overflow: 'auto' }}>
                {events.map((event, index) => (
                  <Card key={index} sx={{ mb: 2 }}>
                    <CardContent>
                      <Box display="flex" justifyContent="space-between" alignItems="start">
                        <Box flex={1}>
                          <Typography variant="h6" gutterBottom>
                            {event.article_title || 'Untitled'}
                          </Typography>
                          <Box display="flex" gap={1} mb={1}>
                            <Chip label={event.type} color="primary" size="small" />
                            <Chip label={`Confidence: ${event.confidence.toFixed(2)}`} size="small" />
                            <Chip label={event.trigger_word} variant="outlined" size="small" />
                          </Box>
                          <Typography variant="body2" color="textSecondary">
                            {event.published_date ? new Date(event.published_date).toLocaleString() : 'N/A'}
                          </Typography>
                          {event.entities && event.entities.length > 0 && (
                            <Box mt={1}>
                              <Typography variant="caption" color="textSecondary">
                                Entities:
                              </Typography>
                              <Box display="flex" gap={0.5} mt={0.5} flexWrap="wrap">
                                {event.entities.map((entity: string, i: number) => (
                                  <Chip key={i} label={entity} size="small" variant="outlined" />
                                ))}
                              </Box>
                            </Box>
                          )}
                        </Box>
                      </Box>
                    </CardContent>
                  </Card>
                ))}
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}

