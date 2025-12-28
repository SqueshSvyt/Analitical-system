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
  Divider,
  Chip,
  Tabs,
  Tab,
} from '@mui/material'
import { Search as SearchIcon } from '@mui/icons-material'
import { entityApi } from '../services/api'

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props
  return (
    <div hidden={value !== index} {...other}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  )
}

export default function EntityIntelligence() {
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<any[]>([])
  const [selectedEntity, setSelectedEntity] = useState<any>(null)
  const [entityOverview, setEntityOverview] = useState<any>(null)
  const [entityTimeline, setEntityTimeline] = useState<any[]>([])
  const [entityNetwork, setEntityNetwork] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [tabValue, setTabValue] = useState(0)

  const handleSearch = async () => {
    try {
      setLoading(true)
      const response = await entityApi.searchEntities({
        query: searchQuery,
        limit: 20,
      })
      setSearchResults(response.data)
    } catch (error) {
      console.error('Error searching entities:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSelectEntity = async (entity: any) => {
    try {
      setLoading(true)
      setSelectedEntity(entity)
      
      const [overviewRes, timelineRes, networkRes] = await Promise.all([
        entityApi.getEntityOverview(entity.entity_id),
        entityApi.getEntityTimeline(entity.entity_id, { limit: 50 }),
        entityApi.getEntityNetwork(entity.entity_id, { k_hops: 1, limit: 20 }),
      ])

      setEntityOverview(overviewRes.data)
      setEntityTimeline(timelineRes.data)
      setEntityNetwork(networkRes.data)
    } catch (error) {
      console.error('Error fetching entity details:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Entity Intelligence
      </Typography>

      {/* Search */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={10}>
            <TextField
              fullWidth
              label="Search Entities"
              placeholder="Enter entity name..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
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

        {/* Search Results */}
        {searchResults.length > 0 && (
          <Box mt={2}>
            <Typography variant="subtitle2" gutterBottom>
              Search Results ({searchResults.length})
            </Typography>
            <Box display="flex" gap={1} flexWrap="wrap">
              {searchResults.map((entity, index) => (
                <Chip
                  key={index}
                  label={`${entity.text} (${entity.label}) - ${entity.event_count} events`}
                  onClick={() => handleSelectEntity(entity)}
                  color={selectedEntity?.entity_id === entity.entity_id ? 'primary' : 'default'}
                />
              ))}
            </Box>
          </Box>
        )}
      </Paper>

      {/* Entity Details */}
      {selectedEntity && (
        <Paper>
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs value={tabValue} onChange={(_, newValue) => setTabValue(newValue)}>
              <Tab label="Overview" />
              <Tab label="Timeline" />
              <Tab label="Network" />
            </Tabs>
          </Box>

          <TabPanel value={tabValue} index={0}>
            {loading ? (
              <Box display="flex" justifyContent="center" p={4}>
                <CircularProgress />
              </Box>
            ) : entityOverview && (
              <Box>
                <Typography variant="h5" gutterBottom>
                  {entityOverview.text}
                </Typography>
                <Chip label={entityOverview.label} color="primary" sx={{ mb: 2 }} />
                
                <Grid container spacing={2} sx={{ mb: 3 }}>
                  <Grid item xs={12} md={4}>
                    <Card>
                      <CardContent>
                        <Typography color="textSecondary" gutterBottom>
                          Total Events
                        </Typography>
                        <Typography variant="h4">
                          {entityOverview.total_events}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <Card>
                      <CardContent>
                        <Typography color="textSecondary" gutterBottom>
                          First Seen
                        </Typography>
                        <Typography variant="h6">
                          {entityOverview.first_seen ? 
                            new Date(entityOverview.first_seen).toLocaleDateString() : 
                            'N/A'}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <Card>
                      <CardContent>
                        <Typography color="textSecondary" gutterBottom>
                          Last Seen
                        </Typography>
                        <Typography variant="h6">
                          {entityOverview.last_seen ? 
                            new Date(entityOverview.last_seen).toLocaleDateString() : 
                            'N/A'}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>

                <Typography variant="h6" gutterBottom>
                  Event Distribution
                </Typography>
                <Box>
                  {Object.entries(entityOverview.event_distribution || {}).map(([type, count]: [string, any]) => (
                    <Box key={type} display="flex" justifyContent="space-between" mb={1}>
                      <Typography>{type}</Typography>
                      <Chip label={count} size="small" />
                    </Box>
                  ))}
                </Box>
              </Box>
            )}
          </TabPanel>

          <TabPanel value={tabValue} index={1}>
            {loading ? (
              <Box display="flex" justifyContent="center" p={4}>
                <CircularProgress />
              </Box>
            ) : (
              <Box sx={{ maxHeight: '500px', overflow: 'auto' }}>
                {entityTimeline.map((event, index) => (
                  <Card key={index} sx={{ mb: 2 }}>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        {event.article_title}
                      </Typography>
                      <Box display="flex" gap={1} mb={1}>
                        <Chip label={event.event_type} color="primary" size="small" />
                        <Chip label={`Confidence: ${event.confidence.toFixed(2)}`} size="small" />
                      </Box>
                      <Typography variant="body2" color="textSecondary">
                        {new Date(event.date).toLocaleString()}
                      </Typography>
                    </CardContent>
                  </Card>
                ))}
              </Box>
            )}
          </TabPanel>

          <TabPanel value={tabValue} index={2}>
            {loading ? (
              <Box display="flex" justifyContent="center" p={4}>
                <CircularProgress />
              </Box>
            ) : entityNetwork && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  Connected Entities ({entityNetwork.nodes.length})
                </Typography>
                <Grid container spacing={2}>
                  {entityNetwork.nodes.map((node: any, index: number) => (
                    <Grid item xs={12} md={6} key={index}>
                      <Card>
                        <CardContent>
                          <Typography variant="subtitle1">
                            {node.text}
                          </Typography>
                          <Box display="flex" gap={1} mt={1}>
                            <Chip label={node.label} size="small" />
                            <Chip label={`${node.connection_count} connections`} size="small" variant="outlined" />
                          </Box>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              </Box>
            )}
          </TabPanel>
        </Paper>
      )}
    </Box>
  )
}

