"""Product Service - handles product catalog operations"""

from decimal import Decimal
from typing import List, Optional

from domain.interfaces.product_repository import IProductRepository
from domain.exceptions.product_exceptions import (
    ProductNotFoundException,
    InvalidPriceException,
    InvalidStockException
)
from application.dtos.product_dtos import (
    CreateProductDto,
    UpdateProductDto,
    ProductDto,
    ProductSearchDto,
    UpdateStockDto
)
from application.exceptions.validation_exception import ValidationException
from application.exceptions.unauthorized_exception import UnauthorizedException
from infrastructure.logging.logger import ILogger


class ProductService:
    """
    Application service for product operations.
    
    Responsibilities:
    - Product catalog management
    - Stock management
    - Product search
    """
    
    def __init__(
        self,
        product_repository: IProductRepository,
        logger: ILogger
    ):
        """
        Initialize ProductService with dependencies.
        
        Args:
            product_repository: Repository for product persistence
            logger: Logger for audit trail
        """
        self._product_repository = product_repository
        self._logger = logger
    
    def create_product(self, dto: CreateProductDto, admin_id: int) -> ProductDto:
        """
        Create a new product (admin only).
        
        Args:
            dto: CreateProductDto with product details
            admin_id: Admin user ID creating the product
        
        Returns:
            ProductDto with created product
        
        Raises:
            ValidationException: If validation fails
            InvalidPriceException: If price is invalid
            InvalidStockException: If stock is invalid
        """
        # Validate input
        self._validate_product_input(dto.name, dto.price, dto.stock)
        
        # Create product data
        product_data = {
            'name': dto.name,
            'price': float(dto.price),
            'stock': dto.stock,
            'category': dto.category
        }
        
        # Save product
        product_id = self._product_repository.save(product_data)
        
        # Log action
        self._logger.info(
            f"Product created: {dto.name}",
            {"product_id": product_id, "admin_id": admin_id}
        )
        
        # Return DTO
        return ProductDto(
            id=product_id,
            name=dto.name,
            price=dto.price,
            stock=dto.stock,
            category=dto.category
        )
    
    def get_product_by_id(self, product_id: int) -> ProductDto:
        """
        Get product by ID.
        
        Args:
            product_id: Product ID
        
        Returns:
            ProductDto
        
        Raises:
            ProductNotFoundException: If product not found
        """
        product = self._product_repository.find_by_id(product_id)
        
        if not product:
            raise ProductNotFoundException(product_id)
        
        return self._map_to_dto(product)
    
    def get_all_products(self) -> List[ProductDto]:
        """
        Get all products.
        
        Returns:
            List of ProductDto
        """
        products = self._product_repository.find_all()
        return [self._map_to_dto(p) for p in products]
    
    def search_products(self, dto: ProductSearchDto) -> List[ProductDto]:
        """
        Search products by name or category.
        
        Args:
            dto: ProductSearchDto with search query
        
        Returns:
            List of matching ProductDto
        """
        all_products = self._product_repository.find_all()
        
        # Simple in-memory filtering
        results = []
        query_lower = dto.query.lower()
        
        for product in all_products:
            name_match = query_lower in product['name'].lower()
            category_match = query_lower in product['category'].lower()
            
            if name_match or category_match:
                results.append(self._map_to_dto(product))
        
        return results
    
    def update_product(self, dto: UpdateProductDto, admin_id: int) -> ProductDto:
        """
        Update product (admin only).
        
        Args:
            dto: UpdateProductDto with updated fields
            admin_id: Admin user ID performing update
        
        Returns:
            Updated ProductDto
        
        Raises:
            ProductNotFoundException: If product not found
            ValidationException: If validation fails
        """
        # Get existing product
        product = self._product_repository.find_by_id(dto.product_id)
        if not product:
            raise ProductNotFoundException(dto.product_id)
        
        # Update fields if provided
        if dto.name is not None:
            if not dto.name or dto.name.strip() == "":
                raise ValidationException("Product name cannot be empty")
            product['name'] = dto.name
        
        if dto.price is not None:
            if dto.price <= 0:
                raise InvalidPriceException()
            product['price'] = float(dto.price)
        
        if dto.stock is not None:
            if dto.stock < 0:
                raise InvalidStockException()
            product['stock'] = dto.stock
        
        if dto.category is not None:
            product['category'] = dto.category
        
        # Note: Repository update method would be needed
        # For now, this is conceptual
        
        self._logger.info(
            f"Product updated: {dto.product_id}",
            {"product_id": dto.product_id, "admin_id": admin_id}
        )
        
        return self._map_to_dto(product)
    
    def update_stock(self, dto: UpdateStockDto, admin_id: int) -> ProductDto:
        """
        Update product stock (admin only).
        
        Args:
            dto: UpdateStockDto with stock change
            admin_id: Admin user ID
        
        Returns:
            Updated ProductDto
        
        Raises:
            ProductNotFoundException: If product not found
        """
        product = self._product_repository.find_by_id(dto.product_id)
        if not product:
            raise ProductNotFoundException(dto.product_id)
        
        # Update stock
        self._product_repository.update_stock(dto.product_id, dto.quantity)
        
        # Get updated product
        updated_product = self._product_repository.find_by_id(dto.product_id)
        
        self._logger.info(
            f"Stock updated for product {dto.product_id}",
            {"product_id": dto.product_id, "change": dto.quantity, "admin_id": admin_id}
        )
        
        return self._map_to_dto(updated_product)
    
    def _validate_product_input(self, name: str, price: Decimal, stock: int) -> None:
        """Validate product input"""
        if not name or name.strip() == "":
            raise ValidationException("Product name is required")
        
        if price <= 0:
            raise InvalidPriceException()
        
        if stock < 0:
            raise InvalidStockException()
    
    def _map_to_dto(self, product: dict) -> ProductDto:
        """Map product dict to ProductDto"""
        return ProductDto(
            id=product['id'],
            name=product['name'],
            price=Decimal(str(product['price'])),
            stock=product['stock'],
            category=product['category']
        )
