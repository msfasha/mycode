"""Database connection and operations."""
import asyncpg
from typing import List, Dict, Optional
from datetime import datetime
import os
import uuid as uuid_lib

# Database connection pool
_pool: Optional[asyncpg.Pool] = None

async def get_pool() -> asyncpg.Pool:
    """Get or create database connection pool."""
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 5432)),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'postgres'),
            database=os.getenv('DB_NAME', 'rtdwms'),
            min_size=2,
            max_size=10
        )
    return _pool

async def init_db():
    """Initialize database tables and TimescaleDB hypertable."""
    pool = await get_pool()
    
    async with pool.acquire() as conn:
        # Create networks table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS networks (
                network_id UUID PRIMARY KEY,
                name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT NOW()
            )
        ''')
        
        # Create baselines table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS baselines (
                network_id UUID PRIMARY KEY,
                pressures JSONB NOT NULL,
                flows JSONB NOT NULL,
                tank_levels JSONB NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT NOW()
            )
        ''')
        
        # Create scada_readings table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS scada_readings (
                id BIGSERIAL PRIMARY KEY,
                network_id UUID NOT NULL,
                timestamp TIMESTAMPTZ NOT NULL,
                sensor_id TEXT NOT NULL,
                sensor_type TEXT NOT NULL,
                value REAL NOT NULL,
                location_id TEXT NOT NULL
            )
        ''')
        
        # Create index for faster queries
        await conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_scada_network_timestamp 
            ON scada_readings(network_id, timestamp DESC)
        ''')
        
        # Create anomalies table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS anomalies (
                id BIGSERIAL PRIMARY KEY,
                network_id UUID NOT NULL,
                timestamp TIMESTAMPTZ NOT NULL,
                sensor_id TEXT NOT NULL,
                sensor_type TEXT NOT NULL,
                location_id TEXT NOT NULL,
                actual_value REAL NOT NULL,
                expected_value REAL NOT NULL,
                deviation_percent REAL NOT NULL,
                threshold REAL NOT NULL,
                severity TEXT NOT NULL
            )
        ''')
        
        # Create index for faster anomaly queries
        await conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_anomalies_network_timestamp 
            ON anomalies(network_id, timestamp DESC)
        ''')
        
        await conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_anomalies_severity 
            ON anomalies(severity, timestamp DESC)
        ''')
        
        # Try to create TimescaleDB hypertable (optional, falls back to regular table)
        try:
            await conn.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE")
            # Check if already hypertable
            result = await conn.fetchval('''
                SELECT EXISTS (
                    SELECT 1 FROM timescaledb_information.hypertables 
                    WHERE hypertable_name = 'scada_readings'
                )
            ''')
            if not result:
                await conn.execute('''
                    SELECT create_hypertable('scada_readings', 'timestamp', 
                                           if_not_exists => TRUE)
                ''')
                print("TimescaleDB hypertable created successfully")
        except Exception as e:
            print(f"Using regular PostgreSQL table (TimescaleDB not available): {e}")

async def store_network(network_id: str, name: str, file_path: str):
    """Store network metadata."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        # Convert string UUID to UUID type
        network_uuid = uuid_lib.UUID(network_id)
        await conn.execute('''
            INSERT INTO networks (network_id, name, file_path, created_at)
            VALUES ($1, $2, $3, NOW())
            ON CONFLICT (network_id) DO UPDATE
            SET name = EXCLUDED.name, file_path = EXCLUDED.file_path
        ''', network_uuid, name, file_path)

async def store_baseline(network_id: str, pressures: Dict, flows: Dict, tank_levels: Dict):
    """Store baseline data."""
    import json
    pool = await get_pool()
    async with pool.acquire() as conn:
        # Convert string UUID to UUID type
        network_uuid = uuid_lib.UUID(network_id)
        await conn.execute('''
            INSERT INTO baselines (network_id, pressures, flows, tank_levels, created_at)
            VALUES ($1, $2, $3, $4, NOW())
            ON CONFLICT (network_id) DO UPDATE
            SET pressures = EXCLUDED.pressures,
                flows = EXCLUDED.flows,
                tank_levels = EXCLUDED.tank_levels
        ''', network_uuid, json.dumps(pressures), json.dumps(flows), json.dumps(tank_levels))

async def store_scada_readings(network_id: str, readings: List[Dict]):
    """Store SCADA sensor readings in bulk."""
    if not readings:
        return
    
    pool = await get_pool()
    async with pool.acquire() as conn:
        # Convert string UUID to UUID type
        network_uuid = uuid_lib.UUID(network_id)
        await conn.executemany('''
            INSERT INTO scada_readings 
            (network_id, timestamp, sensor_id, sensor_type, value, location_id)
            VALUES ($1, $2, $3, $4, $5, $6)
        ''', [
            (
                network_uuid,
                reading['timestamp'],
                reading['sensor_id'],
                reading['sensor_type'],
                reading['value'],
                reading['location_id']
            )
            for reading in readings
        ])

async def get_scada_readings(network_id: str, start_time: datetime, end_time: datetime) -> List[Dict]:
    """Get SCADA readings for a time range."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        # Convert string UUID to UUID type
        network_uuid = uuid_lib.UUID(network_id)
        rows = await conn.fetch('''
            SELECT timestamp, sensor_id, sensor_type, value, location_id
            FROM scada_readings
            WHERE network_id = $1 AND timestamp BETWEEN $2 AND $3
            ORDER BY timestamp DESC
        ''', network_uuid, start_time, end_time)
        
        return [
            {
                'timestamp': row['timestamp'],
                'sensor_id': row['sensor_id'],
                'sensor_type': row['sensor_type'],
                'value': row['value'],
                'location_id': row['location_id']
            }
            for row in rows
        ]

async def store_anomalies(network_id: str, anomalies: List[Dict]):
    """Store anomaly detections in database."""
    if not anomalies:
        return
    
    pool = await get_pool()
    async with pool.acquire() as conn:
        network_uuid = uuid_lib.UUID(network_id)
        
        await conn.executemany('''
            INSERT INTO anomalies 
            (network_id, timestamp, sensor_id, sensor_type, location_id,
             actual_value, expected_value, deviation_percent, threshold, severity)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        ''', [
            (
                network_uuid,
                datetime.fromisoformat(anomaly['timestamp'].replace('Z', '+00:00')) if isinstance(anomaly['timestamp'], str) else anomaly['timestamp'],
                anomaly['sensor_id'],
                anomaly['sensor_type'],
                anomaly['location_id'],
                anomaly['actual_value'],
                anomaly['expected_value'],
                anomaly['deviation_percent'],
                anomaly['threshold'],
                anomaly.get('severity', 'medium')
            )
            for anomaly in anomalies
        ])

async def get_anomalies(network_id: str, start_time: datetime = None, end_time: datetime = None, severity: str = None) -> List[Dict]:
    """Get anomalies for a network, optionally filtered by time range and severity."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        network_uuid = uuid_lib.UUID(network_id)
        
        query = '''
            SELECT id, timestamp, sensor_id, sensor_type, location_id,
                   actual_value, expected_value, deviation_percent, threshold, severity
            FROM anomalies
            WHERE network_id = $1
        '''
        params = [network_uuid]
        param_idx = 2
        
        if start_time:
            query += f' AND timestamp >= ${param_idx}'
            params.append(start_time)
            param_idx += 1
        
        if end_time:
            query += f' AND timestamp <= ${param_idx}'
            params.append(end_time)
            param_idx += 1
        
        if severity:
            query += f' AND severity = ${param_idx}'
            params.append(severity)
        
        query += ' ORDER BY timestamp DESC LIMIT 1000'
        
        rows = await conn.fetch(query, *params)
        
        return [
            {
                'id': row['id'],
                'timestamp': row['timestamp'],
                'sensor_id': row['sensor_id'],
                'sensor_type': row['sensor_type'],
                'location_id': row['location_id'],
                'actual_value': row['actual_value'],
                'expected_value': row['expected_value'],
                'deviation_percent': row['deviation_percent'],
                'threshold': row['threshold'],
                'severity': row['severity']
            }
            for row in rows
        ]

async def close_db():
    """Close database pool."""
    global _pool
    if _pool:
        await _pool.close()
        _pool = None

