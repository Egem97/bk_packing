"""
FastAPI Microservice for Pipeline Data API
Provides REST endpoints for querying processed data from PostgreSQL
Optimized for high concurrency (30+ requests/minute)
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import psycopg2
from psycopg2 import pool
import json
from datetime import datetime, timedelta
import os
from contextlib import contextmanager
from typing import Optional, Dict, Any, List

# Import our modules
from .schemas import CalidadProductoTerminado, CalidadProductoTerminadoRequest, CalidadProductoTerminadoEmpresaRequest, UserLogin, Token
from .auth import authenticate_user, create_access_token, get_current_active_user, ACCESS_TOKEN_EXPIRE_MINUTES
from .services import DataService

app = FastAPI(
    title="Pipeline APG Air API",
    description="Data Pipeline API for OneDrive to PostgreSQL - High Concurrency Optimized",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection pool for high concurrency
connection_pool = None

def init_db_pool():
    """Initialize database connection pool"""
    global connection_pool
    try:
        connection_pool = psycopg2.pool.SimpleConnectionPool(
            minconn=5,      # Minimum connections
            maxconn=50,     # Maximum connections (for 30 req/min)
            host="pipeline-postgres",
            database="pipeline_db",
            user="pipeline_user",
            password="pipeline_pass"
        )
        print("Database connection pool initialized successfully")
    except Exception as e:
        print(f"Failed to initialize connection pool: {e}")
        connection_pool = None

@contextmanager
def get_db_connection():
    """Get database connection from pool with automatic cleanup"""
    conn = None
    try:
        if connection_pool:
            conn = connection_pool.getconn()
            yield conn
        else:
            # Fallback to direct connection if pool fails
            conn = psycopg2.connect(
                host="pipeline-postgres",
                database="pipeline_db",
                user="pipeline_user",
                password="pipeline_pass"
            )
            yield conn
    except Exception as e:
        print(f"Database connection error: {e}")
        raise
    finally:
        if conn and connection_pool:
            connection_pool.putconn(conn)
        elif conn:
            conn.close()

@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup"""
    init_db_pool()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on shutdown"""
    global connection_pool
    if connection_pool:
        connection_pool.closeall()
        print("Database connection pool closed")

@app.get("/")
async def root():
    return {"message": "Pipeline APG Air API is running! (High Concurrency Optimized)"}

@app.post("/api/v1/auth/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """Login endpoint to get JWT token"""
    user = authenticate_user(user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/v1/auth/me")
async def get_current_user_info(current_user = Depends(get_current_active_user)):
    """Get current user information"""
    return {
        "username": current_user["username"],
        "full_name": current_user["full_name"],
        "email": current_user["email"]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint with connection pool status"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            
        pool_status = "healthy" if connection_pool else "fallback"
        return {
            "status": "healthy", 
            "database": "connected", 
            "connection_pool": pool_status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy", 
            "error": str(e), 
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/v1/data/employees")
async def get_employees():
    """Get employee data"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM pipeline.employee_data LIMIT 100")
            rows = cursor.fetchall()
            
            # Convert to list of dictionaries
            employees = []
            for row in rows:
                employees.append({
                    "id": row[0],
                    "source_file": row[1],
                    "created_at": row[2].isoformat() if row[2] else None,
                    "raw_data": row[3],
                    "processed_data": row[4]
                })
            
            cursor.close()
            return {"employees": employees, "count": len(employees)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving employee data: {str(e)}")

@app.get("/api/v1/data/sales")
async def get_sales():
    """Get sales data"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM pipeline.sales_data LIMIT 100")
            rows = cursor.fetchall()
            
            # Convert to list of dictionaries
            sales = []
            for row in rows:
                sales.append({
                    "id": row[0],
                    "source_file": row[1],
                    "created_at": row[2].isoformat() if row[2] else None,
                    "raw_data": row[3],
                    "processed_data": row[4]
                })
            
            cursor.close()
            return {"sales": sales, "count": len(sales)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving sales data: {str(e)}")

@app.get("/api/v1/data/production")
async def get_production():
    """Get production data"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM pipeline.production_data LIMIT 100")
            rows = cursor.fetchall()
            
            # Convert to list of dictionaries
            production = []
            for row in rows:
                production.append({
                    "id": row[0],
                    "source_file": row[1],
                    "created_at": row[2].isoformat() if row[2] else None,
                    "raw_data": row[3],
                    "processed_data": row[4]
                })
            
            cursor.close()
            return {"production": production, "count": len(production)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving production data: {str(e)}")

@app.get("/api/v1/data/statistics")
async def get_statistics():
    """Get data statistics"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM pipeline.data_statistics")
            rows = cursor.fetchall()
            
            # Convert to list of dictionaries
            statistics = []
            for row in rows:
                statistics.append({
                    "id": row[0],
                    "data_type": row[1],
                    "record_count": row[2],
                    "file_count": row[3],
                    "earliest_record": row[4].isoformat() if row[4] else None,
                    "latest_record": row[5].isoformat() if row[5] else None,
                    "calculated_at": row[6].isoformat() if row[6] else None
                })
            
            cursor.close()
            return {"statistics": statistics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving statistics: {str(e)}")

@app.post("/api/v1/data/calidad-producto-terminado", response_model=List[CalidadProductoTerminado])
async def get_calidad_producto_terminado(
    request: CalidadProductoTerminadoRequest,
    current_user = Depends(get_current_active_user)
):
    """Get calidad producto terminado data with POST method and JWT authentication"""
    try:
        service = DataService()
        
        # Use the service to get data
        with get_db_connection() as conn:
            data = service.get_calidad_producto_terminado(
                db=conn,
                limit=request.limit,
                offset=request.offset,
                filters=request.filters
            )
        
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving calidad producto terminado data: {str(e)}")

@app.post("/api/v1/data/calidad-producto-terminado/", response_model=List[CalidadProductoTerminado])
async def get_calidad_producto_terminado_by_empresa(
    request: CalidadProductoTerminadoEmpresaRequest,
    current_user = Depends(get_current_active_user)
):
    """Get calidad producto terminado data filtered by empresa with POST method and JWT authentication"""
    try:
        service = DataService()
        
        # Use the service to get data filtered by empresa
        with get_db_connection() as conn:
            data = service.get_calidad_producto_terminado_by_empresa(
                db=conn,
                empresa=request.empresa,
                limit=request.limit,
                offset=request.offset
            )
        
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving calidad producto terminado data by empresa: {str(e)}")

@app.get("/api/v1/data/calidad-producto-terminado/stats")
async def get_calidad_producto_terminado_stats():
    """Get calidad producto terminado statistics"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get total count
            cursor.execute("""
                SELECT COUNT(*) as total_count
                FROM pipeline.pipeline_data
                WHERE data_type = 'calidad_producto_terminado'
            """)
            total_count = cursor.fetchone()[0]
            
            # Get latest record
            cursor.execute("""
                SELECT created_at
                FROM pipeline.pipeline_data
                WHERE data_type = 'calidad_producto_terminado'
                ORDER BY created_at DESC
                LIMIT 1
            """)
            latest_record = cursor.fetchone()
            latest_update = latest_record[0].isoformat() if latest_record else None
            
            cursor.close()
            return {
                "total_records": total_count,
                "latest_update": latest_update,
                "data_type": "calidad_producto_terminado"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving calidad producto terminado stats: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
