"""
Integration tests for API endpoints.
"""

import pytest
from unittest.mock import AsyncMock, patch


class TestPipesAPI:
    """Tests for pipes API endpoints."""
    
    def test_pipes_endpoint_exists(self):
        """Pipes router is registered."""
        from app.main import app
        
        routes = [route.path for route in app.routes]
        assert any("/api/v1/pipes" in str(route) for route in app.routes)
    
    def test_pipe_schema_valid(self):
        """Pipe schema validates correctly."""
        from app.api.schemas.pipe import PipeCreate, PipeBase
        
        # Valid pipe data
        pipe_data = {
            "dn_mm": 200,
            "pn_class": "PN6",
            "sdr": 26,
            "wall_mm": 7.7,
            "inner_diameter_mm": 184.6,
            "weight_per_meter": 4.73,
            "code": "TPE200/PN6"
        }
        
        pipe = PipeCreate(**pipe_data)
        assert pipe.dn_mm == 200
        assert pipe.code == "TPE200/PN6"


class TestTrucksAPI:
    """Tests for trucks API endpoints."""
    
    def test_trucks_endpoint_exists(self):
        """Trucks router is registered."""
        from app.main import app
        
        routes = [route.path for route in app.routes]
        assert any("/api/v1/trucks" in str(route) for route in app.routes)
    
    def test_truck_schema_valid(self):
        """Truck schema validates correctly."""
        from app.api.schemas.truck import TruckConfigResponse
        
        truck_data = {
            "id": 1,
            "name": "Standard 24t Romania",
            "max_payload_kg": 24000,
            "internal_length_mm": 13600,
            "internal_width_mm": 2480,
            "internal_height_mm": 2700,
            "max_axle_weight_kg": 11500
        }
        
        truck = TruckConfigResponse(**truck_data)
        assert truck.max_payload_kg == 24000


class TestOrdersAPI:
    """Tests for orders API endpoints."""
    
    def test_orders_endpoint_exists(self):
        """Orders router is registered."""
        from app.main import app
        
        routes = [route.path for route in app.routes]
        assert any("/api/v1/orders" in str(route) for route in app.routes)
    
    def test_order_create_schema(self):
        """Order creation schema validates."""
        from app.api.schemas.order import OrderCreate, OrderItemCreate
        
        order_data = {
            "pipe_length_m": 12.0,
            "items": [
                {"pipe_id": 1, "quantity": 5},
                {"pipe_id": 2, "quantity": 10}
            ]
        }
        
        order = OrderCreate(**order_data)
        assert len(order.items) == 2


class TestCalculationsAPI:
    """Tests for calculations API endpoints."""
    
    def test_calculations_endpoint_exists(self):
        """Calculations router is registered."""
        from app.main import app
        
        routes = [route.path for route in app.routes]
        assert any("/api/v1/calculations" in str(route) for route in app.routes)
    
    def test_calculation_schemas(self):
        """Calculation schemas are valid."""
        from app.api.schemas.calculation import (
            NestingValidation,
            NestedBundle,
            TruckLoading
        )
        
        validation = NestingValidation(
            is_valid=True,
            gap_available_mm=54.4,
            gap_required_mm=21.0,
            message="Valid nesting"
        )
        assert validation.is_valid is True


class TestReportsAPI:
    """Tests for reports API endpoints."""
    
    def test_reports_endpoint_exists(self):
        """Reports router is registered."""
        from app.main import app
        
        routes = [route.path for route in app.routes]
        assert any("/api/v1/reports" in str(route) for route in app.routes)


class TestHealthCheck:
    """Tests for health check endpoint."""
    
    def test_health_endpoint(self):
        """Health check endpoint exists."""
        from app.main import app
        
        routes = [route.path for route in app.routes]
        assert "/" in routes or any("/health" in str(r) for r in routes)


class TestCORS:
    """Tests for CORS configuration."""
    
    def test_cors_middleware_enabled(self):
        """CORS middleware is configured."""
        from app.main import app
        
        middleware_classes = [m.cls.__name__ for m in app.user_middleware]
        assert "CORSMiddleware" in middleware_classes
