# HydroTwinJS Troubleshooting Guide

## 🚨 Common Issues and Solutions

### 1. Import Errors (React Icons)

**Error:** `export 'FiBarChart3' was not found in 'react-icons/fi'`

**Solution:** ✅ **FIXED** - Updated imports to use correct icon names:
- `FiBarChart3` → `FiBarChart2`
- Added missing `FiCheckCircle` import

### 2. Proxy Connection Errors

**Error:** `Proxy error: Could not proxy request from localhost:3000 to http://localhost:3001`

**Solution:**
1. **Start the backend server first:**
   ```bash
   cd /media/me/Active/mywork/coding/mycode/experiments/epanet/wateranalytics.org-github/HydroTwinJS
   npm run server
   ```

2. **Then start the frontend in a new terminal:**
   ```bash
   cd client
   npm start
   ```

3. **Or use the development script:**
   ```bash
   ./start-dev.sh
   ```

### 3. Missing Dependencies

**Error:** `Module not found` or `Cannot resolve module`

**Solution:**
```bash
# Install server dependencies
npm install

# Install client dependencies
cd client
npm install
cd ..
```

### 4. Database Connection Issues

**Error:** `Failed to initialize data service`

**Solution:**
1. **Create data directory:**
   ```bash
   mkdir -p data models logs
   ```

2. **Check file permissions:**
   ```bash
   chmod 755 data models logs
   ```

### 5. EPANET Model Issues

**Error:** `Model file not found` or `Failed to initialize simulation engine`

**Solution:**
1. **The system will create a sample model automatically**
2. **For custom models, place your .inp file in the models/ directory**
3. **Update MODEL_INP_PATH in your environment configuration**

### 6. WebSocket Connection Issues

**Error:** `WebSocket connection failed`

**Solution:**
1. **Check if WebSocket port is available:**
   ```bash
   netstat -tulpn | grep :3002
   ```

2. **Verify firewall settings:**
   ```bash
   sudo ufw allow 3002
   ```

### 7. Port Already in Use

**Error:** `EADDRINUSE: address already in use`

**Solution:**
1. **Find and kill the process:**
   ```bash
   lsof -ti:3001 | xargs kill -9
   lsof -ti:3002 | xargs kill -9
   lsof -ti:3000 | xargs kill -9
   ```

2. **Or use different ports:**
   ```bash
   PORT=3003 npm run server
   ```

### 8. Build Issues

**Error:** `npm run build` fails

**Solution:**
1. **Clear cache:**
   ```bash
   npm cache clean --force
   rm -rf node_modules client/node_modules
   ```

2. **Reinstall dependencies:**
   ```bash
   npm install
   cd client && npm install && cd ..
   ```

3. **Try building again:**
   ```bash
   npm run build
   ```

## 🔧 Development Workflow

### Recommended Development Setup

1. **Terminal 1 - Backend:**
   ```bash
   cd HydroTwinJS
   npm run server
   ```

2. **Terminal 2 - Frontend:**
   ```bash
   cd HydroTwinJS/client
   npm start
   ```

3. **Terminal 3 - Database/Logs (Optional):**
   ```bash
   # Monitor database
   sqlite3 data/simulation.db ".tables"
   
   # Monitor logs
   tail -f logs/app.log
   ```

### Environment Variables

Create a `.env` file in the root directory:

```env
NODE_ENV=development
PORT=3001
WS_PORT=3002
DB_PATH=./data/simulation.db
MODEL_INP_PATH=./models/network.inp
SENSOR_API_URL=http://localhost:3001/api/sensors
SENSOR_UPDATE_INTERVAL=30000
```

## 🐛 Debugging Tips

### 1. Enable Debug Logging

```bash
DEBUG=hydrotwinjs:* npm run server
```

### 2. Check Server Status

```bash
curl http://localhost:3001/api/simulation/status
```

### 3. Test WebSocket Connection

```javascript
// In browser console
const ws = new WebSocket('ws://localhost:3002/ws');
ws.onopen = () => console.log('Connected');
ws.onmessage = (e) => console.log('Message:', e.data);
```

### 4. Database Inspection

```bash
sqlite3 data/simulation.db
.tables
.schema simulation_results
SELECT * FROM simulation_summary LIMIT 5;
```

## 📊 Performance Optimization

### 1. Reduce Simulation Frequency

```env
SENSOR_UPDATE_INTERVAL=60000  # 1 minute instead of 30 seconds
```

### 2. Limit Historical Data

```javascript
// In DataService.js
const limit = 50; // Instead of 100
```

### 3. Optimize Database Queries

```sql
-- Add indexes for better performance
CREATE INDEX idx_simulation_timestamp ON simulation_results(timestamp);
CREATE INDEX idx_alerts_status ON alerts(status);
```

## 🚀 Production Deployment

### 1. Build for Production

```bash
npm run build
```

### 2. Use PM2 for Process Management

```bash
npm install -g pm2
pm2 start server/index.js --name hydrotwinjs
pm2 startup
pm2 save
```

### 3. Use Nginx for Reverse Proxy

```bash
# Copy nginx configuration
sudo cp nginx.conf /etc/nginx/sites-available/hydrotwinjs
sudo ln -s /etc/nginx/sites-available/hydrotwinjs /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 📞 Getting Help

If you're still experiencing issues:

1. **Check the logs:**
   ```bash
   tail -f logs/app.log
   ```

2. **Verify all services are running:**
   ```bash
   ps aux | grep node
   netstat -tulpn | grep -E ':(3000|3001|3002)'
   ```

3. **Test individual components:**
   ```bash
   # Test API
   curl http://localhost:3001/api/simulation/status
   
   # Test WebSocket
   wscat -c ws://localhost:3002/ws
   ```

4. **Reset everything:**
   ```bash
   # Stop all processes
   pkill -f node
   
   # Clean and restart
   rm -rf node_modules client/node_modules data/*.db
   npm install
   cd client && npm install && cd ..
   ./start-dev.sh
   ```

---

**Still having issues?** Check the [GitHub Issues](https://github.com/your-org/HydroTwinJS/issues) or create a new issue with:
- Your operating system
- Node.js version
- Error messages
- Steps to reproduce


