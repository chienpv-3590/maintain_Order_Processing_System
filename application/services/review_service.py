"""Review Service - handles product reviews"""

import json
from datetime import datetime
from typing import List
from decimal import Decimal

from domain.interfaces.review_repository import IReviewRepository
from domain.interfaces.user_repository import IUserRepository
from domain.interfaces.order_repository import IOrderRepository
from application.dtos.review_dtos import (
    CreateReviewDto,
    UpdateReviewDto,
    ReviewDto,
    ProductReviewsDto
)
from application.exceptions.resource_not_found_exception import ResourceNotFoundException
from application.exceptions.validation_exception import ValidationException
from application.exceptions.unauthorized_exception import UnauthorizedException
from infrastructure.logging.logger import ILogger


class ReviewService:
    """
    Application service for review operations.
    
    Responsibilities:
    - Create and manage reviews
    - Validate review eligibility
    - Calculate average ratings
    """
    
    def __init__(
        self,
        review_repository: IReviewRepository,
        user_repository: IUserRepository,
        order_repository: IOrderRepository,
        logger: ILogger
    ):
        """
        Initialize ReviewService.
        
        Args:
            review_repository: Repository for review persistence
            user_repository: Repository for user data
            order_repository: Repository for order data
            logger: Logger for audit trail
        """
        self._review_repository = review_repository
        self._user_repository = user_repository
        self._order_repository = order_repository
        self._logger = logger
    
    def create_review(self, dto: CreateReviewDto) -> ReviewDto:
        """
        Create a product review.
        
        Args:
            dto: CreateReviewDto with review details
        
        Returns:
            ReviewDto
        
        Raises:
            ValidationException: If validation fails
            UnauthorizedException: If user hasn't purchased product
            ResourceNotFoundException: If user not found
        """
        # Validate rating
        if dto.rating < 1 or dto.rating > 5:
            raise ValidationException("Rating must be between 1 and 5")
        
        # Validate comment
        if not dto.comment or dto.comment.strip() == "":
            raise ValidationException("Review comment is required")
        
        # Get user
        user = self._user_repository.find_by_id(dto.user_id)
        if not user:
            raise ResourceNotFoundException("User", dto.user_id)
        
        # Check if user already reviewed this product
        existing_review = self._review_repository.find_by_user_and_product(
            dto.user_id, dto.product_id
        )
        if existing_review:
            raise ValidationException("You have already reviewed this product")
        
        # Check if user purchased this product
        if not self._has_purchased_product(dto.user_id, dto.product_id):
            raise UnauthorizedException(
                "You must purchase the product before reviewing it"
            )
        
        # Create review
        review_data = {
            'product_id': dto.product_id,
            'user_id': dto.user_id,
            'rating': dto.rating,
            'comment': dto.comment,
            'created_at': datetime.now().isoformat()
        }
        
        review_id = self._review_repository.save(review_data)
        
        self._logger.info(
            f"Review created for product {dto.product_id}",
            {"review_id": review_id, "product_id": dto.product_id, "user_id": dto.user_id}
        )
        
        return ReviewDto(
            id=review_id,
            product_id=dto.product_id,
            user_id=dto.user_id,
            user_name=user['name'],
            rating=dto.rating,
            comment=dto.comment,
            created_at=review_data['created_at']
        )
    
    def get_product_reviews(self, product_id: int) -> ProductReviewsDto:
        """
        Get all reviews for a product with average rating.
        
        Args:
            product_id: Product ID
        
        Returns:
            ProductReviewsDto with reviews and statistics
        """
        review_records = self._review_repository.find_by_product_id(product_id)
        
        reviews = []
        total_rating = 0
        
        for record in review_records:
            # Get user name
            user = self._user_repository.find_by_id(record['user_id'])
            user_name = user['name'] if user else "Unknown"
            
            review_dto = ReviewDto(
                id=record['id'],
                product_id=record['product_id'],
                user_id=record['user_id'],
                user_name=user_name,
                rating=record['rating'],
                comment=record['comment'],
                created_at=record['created_at']
            )
            reviews.append(review_dto)
            total_rating += record['rating']
        
        # Calculate average
        average_rating = total_rating / len(reviews) if reviews else 0.0
        
        return ProductReviewsDto(
            product_id=product_id,
            average_rating=round(average_rating, 2),
            total_reviews=len(reviews),
            reviews=reviews
        )
    
    def update_review(self, dto: UpdateReviewDto, user_id: int) -> ReviewDto:
        """
        Update a review (only by owner).
        
        Args:
            dto: UpdateReviewDto
            user_id: User ID performing the update
        
        Returns:
            Updated ReviewDto
        
        Raises:
            ResourceNotFoundException: If review not found
            UnauthorizedException: If user doesn't own the review
            ValidationException: If validation fails
        """
        # Get review
        review = self._review_repository.find_by_id(dto.review_id)
        if not review:
            raise ResourceNotFoundException("Review", dto.review_id)
        
        # Check ownership
        if review['user_id'] != user_id:
            raise UnauthorizedException("You can only update your own reviews")
        
        # Validate
        if dto.rating < 1 or dto.rating > 5:
            raise ValidationException("Rating must be between 1 and 5")
        
        if not dto.comment or dto.comment.strip() == "":
            raise ValidationException("Review comment is required")
        
        # Update
        self._review_repository.update(dto.review_id, dto.rating, dto.comment)
        
        # Get user
        user = self._user_repository.find_by_id(user_id)
        
        self._logger.info(
            f"Review updated: {dto.review_id}",
            {"review_id": dto.review_id, "user_id": user_id}
        )
        
        return ReviewDto(
            id=dto.review_id,
            product_id=review['product_id'],
            user_id=user_id,
            user_name=user['name'] if user else "Unknown",
            rating=dto.rating,
            comment=dto.comment,
            created_at=review['created_at']
        )
    
    def delete_review(self, review_id: int, user_id: int, is_admin: bool = False) -> None:
        """
        Delete a review (owner or admin).
        
        Args:
            review_id: Review ID
            user_id: User ID performing deletion
            is_admin: Whether user is admin
        
        Raises:
            ResourceNotFoundException: If review not found
            UnauthorizedException: If not authorized
        """
        review = self._review_repository.find_by_id(review_id)
        if not review:
            raise ResourceNotFoundException("Review", review_id)
        
        # Check authorization
        if not is_admin and review['user_id'] != user_id:
            raise UnauthorizedException("You can only delete your own reviews")
        
        self._review_repository.delete(review_id)
        
        self._logger.info(
            f"Review deleted: {review_id}",
            {"review_id": review_id, "deleted_by": user_id}
        )
    
    def _has_purchased_product(self, user_id: int, product_id: int) -> bool:
        """Check if user has purchased a product"""
        user_orders = self._order_repository.find_by_user_id(user_id)
        
        for order in user_orders:
            # Skip cancelled orders
            if order.get('status') == 'cancelled':
                continue
            
            # Parse order items
            items = json.loads(order['items'])
            
            for item in items:
                if item['product_id'] == product_id:
                    return True
        
        return False
