"""Review Data Transfer Objects"""

from dataclasses import dataclass
from typing import List


@dataclass
class CreateReviewDto:
    """DTO for creating a review"""
    product_id: int
    user_id: int
    rating: int  # 1-5
    comment: str


@dataclass
class UpdateReviewDto:
    """DTO for updating a review"""
    review_id: int
    rating: int
    comment: str


@dataclass
class ReviewDto:
    """DTO for review response"""
    id: int
    product_id: int
    user_id: int
    user_name: str
    rating: int
    comment: str
    created_at: str


@dataclass
class ProductReviewsDto:
    """DTO for product reviews with average"""
    product_id: int
    average_rating: float
    total_reviews: int
    reviews: List[ReviewDto]
