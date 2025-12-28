import { useEffect, useState } from 'react'
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material'
import {
  ExpandMore,
  Warning,
  Error,
  Info,
  TrendingUp,
} from '@mui/icons-material'
import { alertsApi } from '../services/api'

const severityIcons: any = {
  high: <Error color="error" />,
  medium: <Warning color="warning" />,
  low: <Info color="info" />,
}

const severityColors: any = {
  high: 'error',
  medium: 'warning',
  low: 'info',
}

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [filterType, setFilterType] = useState<string>('all')

  useEffect(() => {
    loadAlerts()
  }, [filterType])

  const loadAlerts = async () => {
    try {
      setLoading(true)
      const params = filterType === 'all' ? {} : { alert_type: filterType }
      const response = await alertsApi.getAlerts(params)
      setAlerts(response.data)
    } catch (error) {
      console.error('Error loading alerts:', error)
    } finally {
      setLoading(false)
    }
  }

  const getAlertIcon = (type: string) => {
    switch (type) {
      case 'spike': return <TrendingUp />
      case 'escalation': return <Warning />
      case 'novelty': return <Info />
      case 'evidence': return <Error />
      default: return <Info />
    }
  }

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">
          Alerts & Early Warning System
        </Typography>
        
        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel>Filter by Type</InputLabel>
          <Select
            value={filterType}
            label="Filter by Type"
            onChange={(e) => setFilterType(e.target.value)}
          >
            <MenuItem value="all">All Alerts</MenuItem>
            <MenuItem value="spike">Spike Alerts</MenuItem>
            <MenuItem value="escalation">Escalation Alerts</MenuItem>
            <MenuItem value="novelty">Novelty Alerts</MenuItem>
            <MenuItem value="evidence">Evidence Alerts</MenuItem>
          </Select>
        </FormControl>
      </Box>

      {/* Alert Summary */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        {['high', 'medium', 'low'].map((severity) => {
          const count = alerts.filter(a => a.severity === severity).length
          return (
            <Grid item xs={12} md={4} key={severity}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" justifyContent="space-between">
                    <Box>
                      <Typography color="textSecondary" variant="body2">
                        {severity.toUpperCase()} Severity
                      </Typography>
                      <Typography variant="h4">
                        {count}
                      </Typography>
                    </Box>
                    <Box sx={{ fontSize: 40 }}>
                      {severityIcons[severity]}
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          )
        })}
      </Grid>

      {/* Alerts List */}
      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          Active Alerts ({alerts.length})
        </Typography>

        {alerts.length === 0 ? (
          <Alert severity="success">
            No alerts detected in the current time period.
          </Alert>
        ) : (
          <Box>
            {alerts.map((alert, index) => (
              <Accordion key={index}>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Box display="flex" alignItems="center" gap={2} width="100%">
                    {getAlertIcon(alert.alert_type)}
                    <Box flex={1}>
                      <Typography variant="subtitle1">
                        {alert.title}
                      </Typography>
                      <Box display="flex" gap={1} mt={0.5}>
                        <Chip 
                          label={alert.alert_type} 
                          size="small" 
                          variant="outlined"
                        />
                        <Chip 
                          label={alert.severity} 
                          size="small" 
                          color={severityColors[alert.severity]}
                        />
                        <Chip 
                          label={new Date(alert.triggered_at).toLocaleString()} 
                          size="small" 
                          variant="outlined"
                        />
                      </Box>
                    </Box>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Typography variant="body1" paragraph>
                    {alert.description}
                  </Typography>

                  {alert.related_entities.length > 0 && (
                    <Box mb={2}>
                      <Typography variant="subtitle2" gutterBottom>
                        Related Entities:
                      </Typography>
                      <Box display="flex" gap={0.5} flexWrap="wrap">
                        {alert.related_entities.map((entity: string, i: number) => (
                          <Chip key={i} label={entity} size="small" />
                        ))}
                      </Box>
                    </Box>
                  )}

                  {alert.related_events.length > 0 && (
                    <Box mb={2}>
                      <Typography variant="subtitle2" gutterBottom>
                        Related Events: {alert.related_events.length}
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        Event IDs: {alert.related_events.slice(0, 5).join(', ')}
                        {alert.related_events.length > 5 && '...'}
                      </Typography>
                    </Box>
                  )}

                  {alert.supporting_articles.length > 0 && (
                    <Box>
                      <Typography variant="subtitle2" gutterBottom>
                        Supporting Articles: {alert.supporting_articles.length}
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        Article IDs: {alert.supporting_articles.slice(0, 5).join(', ')}
                        {alert.supporting_articles.length > 5 && '...'}
                      </Typography>
                    </Box>
                  )}
                </AccordionDetails>
              </Accordion>
            ))}
          </Box>
        )}
      </Paper>
    </Box>
  )
}

