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
  CircularProgress,
  Chip,
  Divider,
} from '@mui/material'
import { Search as SearchIcon } from '@mui/icons-material'
import { storylineApi } from '../services/api'

export default function StorylineExplorer() {
  const [pattern, setPattern] = useState('Conflict.Attack,Diplomacy.Sanction')
  const [storylines, setStorylines] = useState<any[]>([])
  const [bridgeActors, setBridgeActors] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [eventType1, setEventType1] = useState('Conflict')
  const [eventType2, setEventType2] = useState('Diplomacy')

  const handleFindStorylines = async () => {
    try {
      setLoading(true)
      const patternArray = pattern.split(',').map(p => p.trim())
      
      const response = await storylineApi.findStorylines({
        event_pattern: patternArray,
        max_days_between_events: 30,
        limit: 20,
      })
      
      setStorylines(response.data)
    } catch (error) {
      console.error('Error finding storylines:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleFindBridgeActors = async () => {
    try {
      setLoading(true)
      const response = await storylineApi.getBridgeActors({
        event_type1: eventType1,
        event_type2: eventType2,
        limit: 20,
      })
      
      setBridgeActors(response.data)
    } catch (error) {
      console.error('Error finding bridge actors:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Storyline Explorer
      </Typography>

      <Grid container spacing={3}>
        {/* Find Storylines */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Find Event Chains
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            <TextField
              fullWidth
              label="Event Pattern (comma-separated)"
              placeholder="e.g., Conflict.Attack, Diplomacy.Sanction, Diplomacy.Meeting"
              value={pattern}
              onChange={(e) => setPattern(e.target.value)}
              sx={{ mb: 2 }}
              multiline
              rows={2}
            />
            
            <Button
              fullWidth
              variant="contained"
              startIcon={<SearchIcon />}
              onClick={handleFindStorylines}
              disabled={loading}
            >
              Find Storylines
            </Button>

            {storylines.length > 0 && (
              <Box mt={3}>
                <Typography variant="subtitle1" gutterBottom>
                  Found {storylines.length} storyline(s)
                </Typography>
                <Box sx={{ maxHeight: '400px', overflow: 'auto' }}>
                  {storylines.map((storyline, index) => (
                    <Card key={index} sx={{ mb: 2 }}>
                      <CardContent>
                        <Box display="flex" justifyContent="space-between" mb={1}>
                          <Chip label={`Confidence: ${storyline.confidence.toFixed(2)}`} size="small" />
                          <Chip label={`${storyline.time_span_days} days`} size="small" color="primary" />
                        </Box>
                        
                        <Typography variant="subtitle2" gutterBottom>
                          Events:
                        </Typography>
                        {storyline.events.map((event: any, i: number) => (
                          <Box key={i} ml={2} mb={1}>
                            <Typography variant="body2">
                              {i + 1}. {event.type} - {event.trigger_word}
                            </Typography>
                            <Typography variant="caption" color="textSecondary">
                              {new Date(event.date).toLocaleDateString()}: "{event.article_title}"
                            </Typography>
                          </Box>
                        ))}
                        
                        {storyline.entities.length > 0 && (
                          <Box mt={1}>
                            <Typography variant="caption" color="textSecondary">
                              Entities:
                            </Typography>
                            <Box display="flex" gap={0.5} mt={0.5} flexWrap="wrap">
                              {storyline.entities.map((entity: string, i: number) => (
                                <Chip key={i} label={entity} size="small" variant="outlined" />
                              ))}
                            </Box>
                          </Box>
                        )}
                      </CardContent>
                    </Card>
                  ))}
                </Box>
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Bridge Actors */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Find Bridge Actors
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            <TextField
              fullWidth
              label="Event Type 1"
              value={eventType1}
              onChange={(e) => setEventType1(e.target.value)}
              sx={{ mb: 2 }}
            />
            
            <TextField
              fullWidth
              label="Event Type 2"
              value={eventType2}
              onChange={(e) => setEventType2(e.target.value)}
              sx={{ mb: 2 }}
            />
            
            <Button
              fullWidth
              variant="contained"
              startIcon={<SearchIcon />}
              onClick={handleFindBridgeActors}
              disabled={loading}
            >
              Find Bridge Actors
            </Button>

            {bridgeActors.length > 0 && (
              <Box mt={3}>
                <Typography variant="subtitle1" gutterBottom>
                  Found {bridgeActors.length} bridge actor(s)
                </Typography>
                <Box sx={{ maxHeight: '400px', overflow: 'auto' }}>
                  {bridgeActors.map((actor, index) => (
                    <Card key={index} sx={{ mb: 2 }}>
                      <CardContent>
                        <Typography variant="subtitle1" gutterBottom>
                          {actor.text}
                        </Typography>
                        <Box display="flex" gap={1} mb={1}>
                          <Chip label={actor.label} size="small" />
                          <Chip label={`${actor.total_events} events`} size="small" color="primary" />
                        </Box>
                        <Typography variant="body2" color="textSecondary">
                          {eventType1}: {actor.type1_events} events
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                          {eventType2}: {actor.type2_events} events
                        </Typography>
                      </CardContent>
                    </Card>
                  ))}
                </Box>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>

      {loading && (
        <Box display="flex" justifyContent="center" mt={4}>
          <CircularProgress />
        </Box>
      )}
    </Box>
  )
}

