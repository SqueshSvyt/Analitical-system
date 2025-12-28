import { useState } from 'react'
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  CircularProgress,
  Card,
  CardContent,
  Chip,
  Divider,
  Alert,
} from '@mui/material'
import { Send as SendIcon } from '@mui/icons-material'
import { qaApi } from '../services/api'

export default function QAPage() {
  const [query, setQuery] = useState('')
  const [response, setResponse] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [history, setHistory] = useState<any[]>([])

  const exampleQueries = [
    "What events involve Russia?",
    "How many Conflict events occurred last month?",
    "Show me escalation patterns involving China",
    "Who are the top actors in Diplomacy events?",
    "What are the relationships between USA and Iran?",
  ]

  const handleAskQuestion = async () => {
    if (!query.trim()) return

    try {
      setLoading(true)
      const result = await qaApi.askQuestion({ query })
      
      setResponse(result.data)
      setHistory([result.data, ...history])
      setQuery('')
    } catch (error) {
      console.error('Error asking question:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Fact-backed News Q&A
      </Typography>

      {/* Query Input */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Ask a Question
        </Typography>
        <TextField
          fullWidth
          multiline
          rows={3}
          label="Your Question"
          placeholder="Ask anything about events, entities, or relationships..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              handleAskQuestion()
            }
          }}
          sx={{ mb: 2 }}
        />
        
        <Button
          variant="contained"
          startIcon={<SendIcon />}
          onClick={handleAskQuestion}
          disabled={loading || !query.trim()}
        >
          Ask Question
        </Button>

        {/* Example Queries */}
        <Box mt={2}>
          <Typography variant="caption" color="textSecondary" gutterBottom>
            Example questions:
          </Typography>
          <Box display="flex" gap={1} flexWrap="wrap" mt={1}>
            {exampleQueries.map((example, index) => (
              <Chip
                key={index}
                label={example}
                size="small"
                onClick={() => setQuery(example)}
                variant="outlined"
              />
            ))}
          </Box>
        </Box>
      </Paper>

      {/* Loading */}
      {loading && (
        <Box display="flex" justifyContent="center" p={4}>
          <CircularProgress />
        </Box>
      )}

      {/* Current Response */}
      {response && !loading && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Answer
          </Typography>
          <Divider sx={{ mb: 2 }} />
          
          <Typography variant="body1" paragraph style={{ whiteSpace: 'pre-line' }}>
            {response.answer}
          </Typography>

          {/* Related Entities */}
          {response.related_entities && response.related_entities.length > 0 && (
            <Box mb={2}>
              <Typography variant="subtitle2" gutterBottom>
                Related Entities ({response.related_entities.length}):
              </Typography>
              <Box display="flex" gap={0.5} flexWrap="wrap">
                {response.related_entities.slice(0, 10).map((entity: string, i: number) => (
                  <Chip key={i} label={entity} size="small" color="primary" />
                ))}
                {response.related_entities.length > 10 && (
                  <Chip label={`+${response.related_entities.length - 10} more`} size="small" />
                )}
              </Box>
            </Box>
          )}

          {/* Related Events */}
          {response.related_events && response.related_events.length > 0 && (
            <Box mb={2}>
              <Typography variant="subtitle2" gutterBottom>
                Related Events: {response.related_events.length}
              </Typography>
              <Typography variant="caption" color="textSecondary">
                {response.related_events.slice(0, 5).join(', ')}
                {response.related_events.length > 5 && '...'}
              </Typography>
            </Box>
          )}

          {/* Evidence */}
          {response.evidence && response.evidence.length > 0 && (
            <Box mt={3}>
              <Typography variant="h6" gutterBottom>
                Evidence ({response.evidence.length} items)
              </Typography>
              <Box sx={{ maxHeight: '400px', overflow: 'auto' }}>
                {response.evidence.slice(0, 5).map((evidence: any, index: number) => (
                  <Card key={index} sx={{ mb: 2 }}>
                    <CardContent>
                      {evidence.event_id && (
                        <>
                          <Box display="flex" gap={1} mb={1}>
                            <Chip label={evidence.event_type} size="small" color="primary" />
                            {evidence.confidence && (
                              <Chip label={`Confidence: ${evidence.confidence.toFixed(2)}`} size="small" />
                            )}
                          </Box>
                          {evidence.article && (
                            <>
                              <Typography variant="subtitle2" gutterBottom>
                                {evidence.article.title}
                              </Typography>
                              <Typography variant="caption" color="textSecondary">
                                {evidence.article.source} - {new Date(evidence.article.published_date).toLocaleDateString()}
                              </Typography>
                            </>
                          )}
                        </>
                      )}
                      
                      {evidence.entity_text && (
                        <>
                          <Typography variant="subtitle2">
                            {evidence.entity_text} ({evidence.entity_label})
                          </Typography>
                          <Typography variant="body2" color="textSecondary">
                            {evidence.event_count} events
                          </Typography>
                        </>
                      )}
                    </CardContent>
                  </Card>
                ))}
                {response.evidence.length > 5 && (
                  <Alert severity="info">
                    Showing 5 of {response.evidence.length} evidence items
                  </Alert>
                )}
              </Box>
            </Box>
          )}
        </Paper>
      )}

      {/* Query History */}
      {history.length > 1 && (
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Previous Questions
          </Typography>
          <Divider sx={{ mb: 2 }} />
          {history.slice(1, 4).map((item, index) => (
            <Card key={index} sx={{ mb: 2 }}>
              <CardContent>
                <Typography variant="subtitle2" gutterBottom>
                  Q: {item.query}
                </Typography>
                <Typography variant="body2" color="textSecondary" style={{ whiteSpace: 'pre-line' }}>
                  A: {item.answer.substring(0, 200)}...
                </Typography>
              </CardContent>
            </Card>
          ))}
        </Paper>
      )}
    </Box>
  )
}

