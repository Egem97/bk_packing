"""
Pydantic schemas for API request/response models
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class DataResponse(BaseModel):
    """Response model for pipeline data"""
    id: str
    source_file: str
    data_type: str
    created_at: datetime
    updated_at: datetime
    raw_data: Optional[Dict[str, Any]] = None
    processed_data: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

class StatisticsResponse(BaseModel):
    """Response model for statistics"""
    total_records: int
    total_files: int
    data_type_stats: List[Dict[str, Any]]
    calculated_at: datetime
    
    class Config:
        from_attributes = True

class EmployeeData(BaseModel):
    """Response model for employee data"""
    id: str
    source_file: str
    created_at: datetime
    employee_id: str
    name: str
    department: str
    salary: float
    
    class Config:
        from_attributes = True

class SalesData(BaseModel):
    """Response model for sales data"""
    id: str
    source_file: str
    created_at: datetime
    sale_id: str
    product: str
    amount: float
    sale_date: datetime
    
    class Config:
        from_attributes = True

class ProductionData(BaseModel):
    """Response model for production data"""
    id: str
    source_file: str
    created_at: datetime
    production_id: str
    product: str
    quantity: int
    production_date: datetime
    
    class Config:
        from_attributes = True

class QueryParams(BaseModel):
    """Query parameters model"""
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
    data_type: Optional[str] = None
    source_file: Optional[str] = None

class EmployeeQueryParams(QueryParams):
    """Employee query parameters"""
    department: Optional[str] = None
    min_salary: Optional[float] = Field(None, ge=0)
    max_salary: Optional[float] = Field(None, ge=0)

class SalesQueryParams(QueryParams):
    """Sales query parameters"""
    product: Optional[str] = None
    min_amount: Optional[float] = Field(None, ge=0)
    max_amount: Optional[float] = Field(None, ge=0)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class ProductionQueryParams(QueryParams):
    """Production query parameters"""
    product: Optional[str] = None
    min_quantity: Optional[int] = Field(None, ge=0)
    max_quantity: Optional[int] = Field(None, ge=0)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class SearchQueryParams(QueryParams):
    """Search query parameters"""
    query: str
    data_type: Optional[str] = None

class AnalyticsSummary(BaseModel):
    """Analytics summary response"""
    total_records: int
    data_types: Dict[str, int]
    date_range: Dict[str, datetime]
    top_products: List[Dict[str, Any]]
    top_departments: List[Dict[str, Any]]
    total_sales: float
    total_production: int
    
    class Config:
        from_attributes = True

class CalidadProductoTerminado(BaseModel):
    """Response model for calidad producto terminado data"""
    id: str
    source_file: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    processed_data: Dict[str, Any] # Only processed data
    
    class Config:
        from_attributes = True

class CalidadProductoTerminadoRequest(BaseModel):
    """Request model for calidad producto terminado queries"""
    limit: Optional[int] = None
    offset: Optional[int] = 0
    filters: Optional[Dict[str, Any]] = None

class CalidadProductoTerminadoEmpresaRequest(BaseModel):
    """Request model for filtering calidad producto terminado by empresa"""
    empresa: str = Field(..., description="Nombre de la empresa para filtrar los datos")
    limit: Optional[int] = None
    offset: Optional[int] = 0

class UserLogin(BaseModel):
    """User login model"""
    username: str
    password: str

class Token(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Token data model"""
    username: Optional[str] = None

class CalidadProductoTerminadoQueryParams(QueryParams):
    """Calidad producto terminado query parameters"""
    # Add specific filters based on your Excel columns
    # Example: fecha: Optional[str] = None
    # Example: producto: Optional[str] = None
    pass
