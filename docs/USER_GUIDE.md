# User Guide

## Getting Started

Welcome to the Analytical Subsystem! This guide will help you navigate and use the platform effectively.

## Table of Contents

1. [Dashboard](#dashboard)
2. [Event Monitor](#event-monitor)
3. [Entity Intelligence](#entity-intelligence)
4. [Storyline Explorer](#storyline-explorer)
5. [Alerts](#alerts)
6. [Q&A System](#qa-system)
7. [Tips & Best Practices](#tips--best-practices)

---

## Dashboard

The Dashboard provides an overview of your knowledge graph and recent activity.

### What You'll See

- **Statistics Cards**: Total articles, events, entities, and date range
- **Event Type Distribution**: Bar chart showing counts by event type
- **Event Trends**: Line chart showing event activity over time

### Quick Actions

- View overall system health
- Identify trending event types
- Monitor recent activity patterns

---

## Event Monitor

Monitor and analyze events in your knowledge graph.

### Search Events

1. **Navigate** to Event Monitor from the sidebar
2. **Set Filters:**
   - Event Types: Enter comma-separated types (e.g., "Conflict, Diplomacy")
   - Min Confidence: Adjust slider (0.0 - 1.0)
   - Limit: Number of results to return
3. **Click Search** to view results

### Understanding Results

Each event card shows:
- **Title**: Article headline
- **Event Type**: Classification (e.g., Conflict.Attack)
- **Confidence Score**: Event extraction confidence
- **Trigger Word**: Key word that identified the event
- **Date**: When the article was published
- **Entities**: People, organizations, locations involved

### Top Actors

The sidebar shows entities most frequently involved in events:
- Entity name and type
- Total event count
- Click to explore in Entity Intelligence

### Use Cases

- **Monitor breaking events**: Set low confidence threshold for early detection
- **Track specific topics**: Filter by event type (e.g., "Diplomacy.Sanction")
- **Identify key players**: Review Top Actors for stakeholder analysis

---

## Entity Intelligence

Comprehensive profiles and analysis of entities (people, organizations, locations).

### Search Entities

1. **Enter search query** (e.g., "Russia", "United Nations")
2. **Click Search**
3. **Select entity** from results to view details

### Entity Profile Tabs

#### Overview
- **Total Events**: Number of events involving this entity
- **First/Last Seen**: Temporal activity range
- **Event Distribution**: Breakdown by event type

#### Timeline
- **Chronological view** of all events involving the entity
- Filter by date range
- See article titles and event types
- Identify activity patterns over time

#### Network
- **Connected entities** that share events with this entity
- Connection strength (number of shared events)
- Entity types and labels
- Useful for understanding relationships

### Use Cases

- **Background Research**: Get comprehensive entity profile
- **Relationship Mapping**: Discover connected entities
- **Activity Tracking**: Monitor entity involvement over time
- **Source Analysis**: See which news sources cover the entity

---

## Storyline Explorer

Discover multi-step event chains and patterns.

### Find Event Chains

1. **Enter Event Pattern**:
   - Comma-separated event types
   - Example: "Conflict.Attack, Diplomacy.Sanction, Diplomacy.Meeting"
2. **Click "Find Storylines"**
3. **Review Results**:
   - Each storyline shows the sequence of events
   - Dates and time spans
   - Involved entities
   - Confidence scores

### Understanding Storylines

Each storyline represents a sequence of connected events involving shared entities:
- **Events List**: Chronological sequence
- **Time Span**: Days between first and last event
- **Confidence**: Average confidence of events in chain
- **Entities**: People/orgs/locations involved

### Find Bridge Actors

1. **Enter two event types** (e.g., "Conflict" and "Diplomacy")
2. **Click "Find Bridge Actors"**
3. **View entities** involved in both event types

Bridge actors are important because they:
- Connect different types of events
- May indicate escalation or mediation
- Represent key stakeholders

### Use Cases

- **Identify Escalation Patterns**: Look for diplomatic → conflict chains
- **Find De-escalation**: Track conflict → diplomatic sequences
- **Discover Mediators**: Identify bridge actors between opposing sides
- **Understand Event Sequences**: See how events lead to other events

---

## Alerts

Automated detection of important or anomalous situations.

### Alert Types

#### 🔥 Spike Alerts (High Priority)
- **What**: Sudden increase in event frequency
- **Why Important**: May indicate breaking news or crisis
- **Action**: Investigate recent events of that type

#### ⚠️ Escalation Alerts (High Priority)
- **What**: Transition from diplomatic to conflict events
- **Why Important**: Indicates worsening situation
- **Action**: Review involved entities and timeline

#### 💡 Novelty Alerts (Medium Priority)
- **What**: New actor appearing in event cluster
- **Why Important**: New player entering situation
- **Action**: Research the new entity's background

#### 📋 Evidence Alerts (Medium Priority)
- **What**: High-confidence event with limited sources
- **Why Important**: May need verification
- **Action**: Check supporting sources

### Using Alerts

1. **View All Alerts** on the Alerts page
2. **Filter by Type** using the dropdown
3. **Click an alert** to expand details
4. **Review**:
   - Description and explanation
   - Related entities and events
   - Supporting articles

### Best Practices

- Check alerts daily for situational awareness
- Investigate high-severity alerts immediately
- Compare evidence from multiple sources
- Use alerts as starting points for deeper analysis

---

## Q&A System

Ask questions about the knowledge graph in natural language.

### How to Use

1. **Type your question** in the text box
2. **Press Enter** or click "Ask Question"
3. **Review the answer** and evidence

### Supported Question Types

#### Events by Entity
- "What events involve Russia?"
- "Show me Conflict events involving Ukraine"
- "What has happened with China recently?"

#### Event Counts
- "How many Diplomacy events occurred last month?"
- "Count events by type"
- "How many events involve both USA and Iran?"

#### Relationships
- "What is the relationship between Russia and Ukraine?"
- "Who is connected to the United Nations?"
- "Show entities related to NATO"

#### Escalation
- "Show me escalation patterns"
- "What tensions have increased?"
- "Has situation with [entity] escalated?"

#### Top Actors
- "Who are the top actors in Conflict events?"
- "Most frequent entities in Diplomacy?"
- "Main players in recent events"

### Understanding Answers

Each answer includes:
- **Natural language response** with key findings
- **Evidence items**: Supporting events and articles
- **Related entities**: Relevant people/orgs/locations
- **Related events**: Event IDs for further investigation

### Tips for Better Questions

- Be specific: Include entity names, event types, or dates
- Use quotes for exact entity names: "United States"
- Ask one thing at a time
- Try example questions first to understand format

---

## Tips & Best Practices

### General Tips

1. **Start Broad, Then Narrow**
   - Begin with Dashboard overview
   - Use Event Monitor to identify interesting events
   - Dig deeper with Entity Intelligence

2. **Follow the Evidence**
   - Always check supporting articles
   - Compare multiple sources
   - Verify high-impact claims

3. **Use Date Filters**
   - Focus on relevant time periods
   - Compare different time ranges
   - Track changes over time

4. **Combine Tools**
   - Find events → Identify entities → Explore relationships
   - Check alerts → Use Q&A for details → Review storylines

### Analysis Workflows

#### Monitoring Workflow
1. Check Dashboard for overview
2. Review Alerts for anomalies
3. Use Event Monitor for recent activity
4. Ask Q&A system for specific questions

#### Research Workflow
1. Search entity in Entity Intelligence
2. Review entity timeline and network
3. Find storylines involving the entity
4. Check alerts related to the entity

#### Investigation Workflow
1. Start with Q&A system question
2. Follow evidence to specific events
3. Explore entities involved
4. Trace storylines and patterns

### Performance Tips

- **Use filters** to limit result sizes
- **Set appropriate limits** (50-100 for most queries)
- **Filter by date range** for recent data
- **Use confidence thresholds** to filter low-quality events

### Keyboard Shortcuts

- **Q&A**: Press Enter to submit question
- **Search**: Press Enter in search boxes
- **Navigation**: Use sidebar to switch pages

---

## Troubleshooting

### No Results Found

- Check filter settings (especially date range)
- Lower confidence threshold
- Broaden search terms
- Verify data exists in database

### Slow Performance

- Reduce result limit
- Narrow date range
- Use more specific filters
- Check system resources

### Unclear Results

- Use Q&A system to ask for clarification
- Check event evidence for context
- Review entity profiles for background
- Look at related storylines

---

## Getting Help

### Resources

- **API Documentation**: http://localhost:8000/docs
- **GitHub Issues**: Report bugs and request features
- **README**: Technical documentation

### Support

For questions or issues:
1. Check this user guide
2. Review API documentation
3. Check existing GitHub issues
4. Open a new issue with details

---

## Glossary

**Event**: A classified action or occurrence extracted from news articles

**Entity**: A person, organization, location, or other named entity

**Event Type**: Classification category (e.g., Conflict.Attack, Diplomacy.Sanction)

**Confidence**: Score (0.0-1.0) indicating extraction quality

**Storyline**: Sequence of connected events involving shared entities

**Bridge Actor**: Entity involved in multiple event types

**Spike**: Abnormal increase in event frequency

**Escalation**: Progression from lower to higher severity events

---

**Happy Analyzing! 📊**

