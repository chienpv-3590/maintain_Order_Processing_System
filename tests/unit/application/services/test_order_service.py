"""Simplified unit tests for OrderService"""

import pytest
from decimal import Decimal
from unittest.mock import Mock

from application.services.order_service import OrderService
from application.dtos.order_dtos import (
    CreateOrderDto,
    OrderItemDto,
    OrderSummaryDto
)
from domain.exceptions.order_exceptions import (
    EmptyOrderException,
    InvalidShippingAddressException,
    InsufficientStockException
)
from domain.exceptions.product_exceptions import ProductNotFoundException
from application.exceptions.resource_not_found_exception import (
    CouponNotFoundException,
    CouponExpiredException
)


class TestOrderServiceCreateOrder:
    """Test cases for create_order method"""
    
    @pytest.fixture
    def mock_repositories(self):
        """Create mock repositories"""
        return {
            'order_repo': Mock(),
            'product_repo': Mock(),
            'coupon_repo': Mock(),
            'user_repo': Mock()
        }
    
    @pytest.fixture
    def order_service(self, mock_repositories):
        """Create OrderService instance with mocks"""
        return OrderService(
            order_repository=mock_repositories['order_repo'],
            product_repository=mock_repositories['product_repo'],
            coupon_repository=mock_repositories['coupon_repo'],
            user_repository=mock_repositories['user_repo']
        )
    
    def test_create_order_happy_path_without_coupon(
        self, 
        order_service, 
        mock_repositories
    ):
        """Test creating order successfully without coupon"""
        # Arrange
        user_id = 1
        dto = CreateOrderDto(
            user_id=user_id,
            items=[
                OrderItemDto(product_id=1, quantity=2),
                OrderItemDto(product_id=2, quantity=1)
            ],
            shipping_address="123 Test St",
            coupon_code=None
        )
        
        # Mock user
        mock_repositories['user_repo'].find_by_id.return_value = {
            'id': user_id,
            'name': 'Test User',
            'role': 'customer'
        }
        
        # Mock products exist and have stock
        mock_repositories['product_repo'].find_by_id.side_effect = [
            {'id': 1, 'name': 'Product 1', 'price': 10.0, 'stock': 10},
            {'id': 2, 'name': 'Product 2', 'price': 20.0, 'stock': 5}
        ]
        
        # Mock order save
        mock_repositories['order_repo'].save.return_value = 123
        
        # Act
        result = order_service.create_order(dto)
        
        # Assert
        assert isinstance(result, OrderSummaryDto)
        assert result.order_id == 123
        assert result.success == True
        assert result.status == 'pending_payment'
        # Total is (2*10 + 1*20) * 1.1 tax = 44.0
        assert result.total == Decimal('44.0')
        
        # Verify stock was reduced
        assert mock_repositories['product_repo'].update_stock.call_count == 2
        mock_repositories['product_repo'].update_stock.assert_any_call(1, -2)
        mock_repositories['product_repo'].update_stock.assert_any_call(2, -1)
    
    def test_create_order_with_valid_coupon(
        self,
        order_service,
        mock_repositories
    ):
        """Test creating order with valid coupon code"""
        # Arrange
        user_id = 1
        dto = CreateOrderDto(
            user_id=user_id,
            items=[OrderItemDto(product_id=1, quantity=1)],
            shipping_address="456 Test Ave",
            coupon_code='DISCOUNT20'
        )
        
        # Mock user
        mock_repositories['user_repo'].find_by_id.return_value = {
            'id': user_id,
            'name': 'Test User',
            'role': 'customer'
        }
        
        mock_repositories['product_repo'].find_by_id.return_value = {
            'id': 1, 'name': 'Product 1', 'price': 100.0, 'stock': 10
        }
        
        # Mock valid coupon
        mock_repositories['coupon_repo'].find_by_code.return_value = {
            'code': 'DISCOUNT20',
            'discount': 20,
            'used': 5,
            'max_uses': 100
        }
        
        mock_repositories['order_repo'].save.return_value = 124
        
        # Act
        result = order_service.create_order(dto)
        
        # Assert
        # Total is (100 - 20%) * 1.1 tax = 88.0
        assert result.total == Decimal('88.0')
        
        # Verify coupon usage was incremented
        mock_repositories['coupon_repo'].increment_usage.assert_called_once_with('DISCOUNT20')
    
    def test_create_order_empty_items_raises_error(self, order_service):
        """Test that empty order items raise EmptyOrderException"""
        # Arrange
        dto = CreateOrderDto(
            user_id=1,
            items=[],
            shipping_address="123 Test St",
            coupon_code=None
        )
        
        # Act & Assert
        with pytest.raises(EmptyOrderException):
            order_service.create_order(dto)
    
    def test_create_order_missing_shipping_address_raises_error(self, order_service):
        """Test that missing shipping address raises error"""
        # Arrange
        dto = CreateOrderDto(
            user_id=1,
            items=[OrderItemDto(product_id=1, quantity=1)],
            shipping_address="",
            coupon_code=None
        )
        
        # Act & Assert
        with pytest.raises(InvalidShippingAddressException):
            order_service.create_order(dto)
    
    def test_create_order_product_not_found(
        self,
        order_service,
        mock_repositories
    ):
        """Test that non-existent product raises ProductNotFoundException"""
        # Arrange
        mock_repositories['product_repo'].find_by_id.return_value = None
        
        dto = CreateOrderDto(
            user_id=1,
            items=[OrderItemDto(product_id=999, quantity=1)],
            shipping_address="123 Test St",
            coupon_code=None
        )
        
        # Act & Assert
        with pytest.raises(ProductNotFoundException):
            order_service.create_order(dto)
    
    def test_create_order_insufficient_stock(
        self,
        order_service,
        mock_repositories
    ):
        """Test that insufficient stock raises InsufficientStockException"""
        # Arrange
        # Product has only 3 items in stock
        mock_repositories['product_repo'].find_by_id.return_value = {
            'id': 1,
            'name': 'Product 1',
            'price': 10.0,
            'stock': 3
        }
        
        # User tries to order 5 items
        dto = CreateOrderDto(
            user_id=1,
            items=[OrderItemDto(product_id=1, quantity=5)],
            shipping_address="123 Test St",
            coupon_code=None
        )
        
        # Act & Assert
        with pytest.raises(InsufficientStockException):
            order_service.create_order(dto)
    
    def test_create_order_expired_coupon(
        self,
        order_service,
        mock_repositories
    ):
        """Test that expired coupon raises CouponExpiredException"""
        # Arrange
        mock_repositories['product_repo'].find_by_id.return_value = {
            'id': 1, 'name': 'Product 1', 'price': 100.0, 'stock': 10
        }
        
        # Coupon is fully used
        mock_repositories['coupon_repo'].find_by_code.return_value = {
            'code': 'EXPIRED',
            'discount': 10,
            'used': 100,
            'max_uses': 100
        }
        
        dto = CreateOrderDto(
            user_id=1,
            items=[OrderItemDto(product_id=1, quantity=1)],
            shipping_address="123 Test St",
            coupon_code='EXPIRED'
        )
        
        # Act & Assert
        with pytest.raises(CouponExpiredException):
            order_service.create_order(dto)
    
    def test_create_order_invalid_coupon_code(
        self,
        order_service,
        mock_repositories
    ):
        """Test that invalid coupon raises CouponNotFoundException"""
        # Arrange
        mock_repositories['product_repo'].find_by_id.return_value = {
            'id': 1, 'name': 'Product 1', 'price': 100.0, 'stock': 10
        }
        
        mock_repositories['coupon_repo'].find_by_code.return_value = None
        
        dto = CreateOrderDto(
            user_id=1,
            items=[OrderItemDto(product_id=1, quantity=1)],
            shipping_address="123 Test St",
            coupon_code='INVALID'
        )
        
        # Act & Assert
        with pytest.raises(CouponNotFoundException):
            order_service.create_order(dto)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
