# Complete Simulator Dashboard Feature Specification

## Document Purpose
This document outlines the complete envisioned feature set for the Simulator Dashboard. The minimal dashboard (Phase 1) implements a subset of these features. Future phases will add the remaining capabilities.

---

## 1. Simulation Status & Configuration Panel

### Display Elements:
- **Current Status**
  - Running/Stopped/Paused/Error states
  - Status indicator with color coding
  - Status change history/timeline

- **Timing Information**
  - Simulation start time
  - Elapsed duration (formatted: "2h 35m")
  - Current EPANET simulation time (from EPS)
  - Last monitoring cycle time
  - Next cycle scheduled time (if running)

- **Network Configuration**
  - Network name/ID
  - File path
  - Network topology summary:
    - Total junctions, pipes, tanks
    - Reservoirs count
    - Pumps/valves count

- **Monitoring Settings**
  - Monitoring interval (e.g., "5 minutes")
  - Pattern timestep (1 hour)
  - Hydraulic timestep (1 minute)
  - Enable/disable settings (if configurable)

---

## 2. Current Hydraulic Analysis Values (Expected from EPANET)

### Display Sections:

**Simulation State:**
- Current EPS time step (e.g., "3h 42m")
- Current hour of day (0-23)
- Active demand pattern multiplier (e.g., "1.4x" for morning peak)
- Pattern applied to junction demands

**Sample Expected Values:**
- **Pressures:**
  - Average pressure across all junctions
  - Minimum pressure (with location)
  - Maximum pressure (with location)
  - Pressure distribution summary (buckets)

- **Flows:**
  - Average flow across all pipes
  - Minimum flow (with pipe ID)
  - Maximum flow (with pipe ID)
  - Flow direction indicators

- **Tank Levels:**
  - Current level for each tank
  - Percent capacity for each tank
  - Inflow/outflow rates
  - Elevation + water height

**Value Summary Cards:**
- Total sensors expected: X
- Average expected pressure: Y psi
- Average expected flow: Z L/s

---

## 3. SCADA Sensor Readings (Actual Values)

### Display Sections:

**Sensor Summary:**
- Total active sensors
- Sensors by type:
  - Pressure sensors: count, avg, min, max
  - Flow sensors: count, avg, min, max
  - Level sensors: count, avg, min, max

**Latest Readings:**
- Last update timestamp
- Readings received count
- Readings per sensor type breakdown
- Data freshness indicator

**Sample Reading Display:**
- Quick view of latest readings from key sensors
- Selected sensor detail view (optional)
- Sensor location mapping

**Statistics:**
- Value ranges across all sensors
- Distribution summary
- Outlier indicators

---

## 4. Anomaly Detection Summary

### Dashboard Cards:

**Anomaly Statistics:**
- Total anomalies detected (session/all-time)
- Anomalies in current monitoring cycle
- Anomalies by severity:
  - Critical: X (red badge)
  - High: Y (orange badge)
  - Medium: Z (yellow badge)

**Anomaly Rate:**
- Percentage of readings with anomalies
- Trend over time (increasing/decreasing)
- Average deviations

**Recent Anomalies Table:**
- Last 20-50 detected anomalies
- Columns:
  - Timestamp (with relative time)
  - Sensor ID (clickable for details)
  - Sensor Type (pressure/flow/level)
  - Location ID
  - Expected Value
  - Actual Value
  - Deviation Percentage
  - Severity Badge
  - Actions (view details, acknowledge)

**Anomaly Details Modal (future):**
- Full anomaly information
- Historical context (sensor readings over time)
- Expected vs Actual graph
- Related anomalies
- Action buttons (resolve, ignore, escalate)

---

## 5. Comparison Statistics

### Metrics Display:

**Comparison Overview:**
- Total comparisons performed
- Comparisons per cycle
- Average comparisons per hour

**Anomaly Detection Rate:**
- Current rate (% of readings)
- Historical rate (last hour, last day)
- Rate by sensor type
- Rate by location (which junctions/pipes have most)

**Pattern Analysis:**
- Most frequent anomaly type
- Most problematic locations (top 10)
- Time-of-day patterns (when anomalies occur most)
- Correlation analysis (multiple anomalies at once)

**Location-Based Analysis:**
- Map/table of locations with anomalies
- Anomaly count per junction/pipe
- Severity distribution per location
- Location health score

---

## 6. Real-time Visualizations

### Chart Types:

**1. Time-Series Charts:**
- **Expected vs Actual Comparison:**
  - Line chart showing expected (EPANET) vs actual (SCADA) for selected sensors
  - Multiple sensors overlay option
  - Zoom/pan capability
  - Anomaly markers on timeline
  - Time range selector (last hour, last 6 hours, last 24 hours)

- **Anomaly Timeline:**
  - Timeline chart showing anomaly occurrences
  - Color-coded by severity
  - Density visualization
  - Click to view anomaly details

- **Sensor Value Trends:**
  - Individual sensor history
  - Multi-sensor comparison
  - Deviation from expected over time

**2. Distribution Charts:**
- **Anomaly Severity Distribution:**
  - Pie/bar chart showing breakdown
  - Critical/High/Medium counts
  - Percentage breakdown

- **Sensor Type Distribution:**
  - Which sensor types have most anomalies
  - Pressure vs Flow vs Level anomaly rates

- **Deviation Distribution:**
  - Histogram of deviation percentages
  - Shows how far readings deviate from expected

**3. Location Heatmap/Map:**
- Network overlay showing anomaly locations
- Heatmap intensity based on anomaly count/severity
- Click location to view details
- Filter by severity or sensor type

**4. Statistics Dashboard:**
- Real-time counters (total readings, anomalies, rate)
- Trend indicators (up/down arrows)
- Mini sparkline charts for key metrics

### Chart Libraries:
- Consider: Chart.js, Recharts, or D3.js
- Priority: Start with simple line/bar charts
- Advanced: Interactive maps and heatmaps

---

## 7. Monitoring Cycle Information

### Display Sections:

**Current Cycle:**
- Cycle number (e.g., "Cycle #24")
- Cycle start time
- Cycle duration
- Status (in progress, completed)

**Cycle Summary:**
- Expected values extracted (pressures, flows, levels)
- Actual readings received (sensor count)
- Comparisons performed (number)
- Anomalies detected (count, breakdown)

**Cycle Timeline:**
- Visual timeline showing:
  - EPS step advancement
  - SCADA generation
  - Comparison execution
  - Anomaly detection
  - Database storage
- Step durations (performance metrics)

**Next Cycle:**
- Countdown to next monitoring cycle (if running)
- Estimated next cycle time
- Interval display

**Database Status:**
- SCADA readings stored count
- Anomalies stored count
- Last database update time
- Storage health indicator

---

## 8. Real-time Updates & Performance

### Update Strategies:

**Option A: Polling (Phase 1)**
- Poll API every 5-10 seconds when simulation running
- Simple to implement
- No backend WebSocket needed
- Suitable for low-frequency updates

**Option B: WebSocket (Future)**
- Real-time push updates
- Lower latency
- More efficient for high-frequency updates
- Requires WebSocket server implementation

**Option C: Hybrid**
- Polling for stats/summaries
- WebSocket for real-time anomaly alerts
- Best of both worlds

### Performance Considerations:
- Limit data transferred (pagination, filtering)
- Efficient queries (indexed database columns)
- Client-side caching
- Debouncing/throttling updates
- Progressive loading (show summary first, details later)

---

## 9. User Interactions

### Actions Available:

**Filtering:**
- Filter anomalies by severity
- Filter by sensor type
- Filter by time range
- Filter by location/junction

**Sorting:**
- Sort anomalies table by timestamp, severity, deviation
- Sort sensors by value, anomaly count

**Export:**
- Export anomalies to CSV
- Export statistics report
- Print dashboard summary

**Settings:**
- Configure refresh interval
- Show/hide specific sections
- Chart configuration
- Alert thresholds

---

## 10. Advanced Features (Future Phases)

### Anomaly Analysis:
- Anomaly patterns detection
- Predictive alerts
- Machine learning integration
- Historical trend analysis

### Reporting:
- Generate monitoring reports
- Scheduled reports (email, PDF)
- Custom report templates

### Alerts & Notifications:
- Real-time alerts for critical anomalies
- Email/SMS notifications
- Alert acknowledgment workflow
- Alert escalation rules

### Integration:
- Export to external systems
- API for third-party integrations
- Webhook support for anomaly events

---

## Implementation Phases Summary

**Phase 1 (Current): Minimal Dashboard**
- Status display
- Basic statistics
- Recent anomalies table (10-15 items)
- Polling-based updates

**Phase 2: Enhanced Display**
- Expected vs Actual value display
- Detailed statistics breakdown
- Sensor reading summaries
- Basic charts (line charts for trends)

**Phase 3: Advanced Analytics**
- Interactive charts (multiple types)
- Full anomaly history with filtering
- Comparison analytics
- Location-based visualization

**Phase 4: Real-time & Advanced**
- WebSocket real-time updates
- Advanced visualizations (maps, heatmaps)
- Machine learning integration
- Reporting and export features

---

## Technical Notes

### Data Requirements:
- Backend must provide aggregated statistics
- Efficient database queries for real-time display
- Consider caching for frequently accessed data

### UI/UX Considerations:
- Responsive design (mobile-friendly)
- Loading states for async operations
- Error handling and user feedback
- Accessibility (WCAG compliance)

### Performance Targets:
- Dashboard load time: < 2 seconds
- Update latency: < 5 seconds (polling)
- Support for networks with 1000+ sensors
- Smooth scrolling and interactions



