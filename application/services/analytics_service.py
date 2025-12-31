"""Analytics Service - handles reporting and analytics"""

from typing import List, Dict
from decimal import Decimal
from datetime import datetime

from domain.interfaces.order_repository import IOrderRepository
from domain.interfaces.user_repository import IUserRepository
from domain.interfaces.product_repository import IProductRepository
from infrastructure.logging.logger import ILogger


class AnalyticsService:
    """
    Application service for analytics and reporting.
    
    Responsibilities:
    - Generate sales reports
    - Calculate metrics
    - Provide dashboard data
    """
    
    def __init__(
        self,
        order_repository: IOrderRepository,
        user_repository: IUserRepository,
        product_repository: IProductRepository,
        logger: ILogger
    ):
        """
        Initialize AnalyticsService.
        
        Args:
            order_repository: Repository for order data
            user_repository: Repository for user data
            product_repository: Repository for product data
            logger: Logger
        """
        self._order_repository = order_repository
        self._user_repository = user_repository
        self._product_repository = product_repository
        self._logger = logger
    
    def get_dashboard_metrics(self) -> Dict:
        """
        Get dashboard metrics for admin.
        
        Returns:
            Dict with key metrics
        """
        all_orders = self._order_repository.find_all()
        
        # Calculate metrics
        total_orders = len(all_orders)
        
        # Calculate revenue (exclude cancelled orders)
        total_revenue = Decimal("0")
        for order in all_orders:
            if order.get('status') != 'cancelled':
                total_revenue += Decimal(str(order['total']))
        
        # Count users
        # Note: Would need a count method in repository
        # For now, using placeholder
        total_users = 0  # self._user_repository.count()
        
        # Get top products (simplified)
        top_products = self._get_top_products(limit=5)
        
        metrics = {
            'total_orders': total_orders,
            'total_revenue': float(total_revenue),
            'total_users': total_users,
            'top_products': top_products,
            'generated_at': datetime.now().isoformat()
        }
        
        self._logger.info("Dashboard metrics generated", metrics)
        
        return metrics
    
    def generate_sales_report(self) -> str:
        """
        Generate sales report.
        
        Returns:
            Formatted report string
        """
        all_orders = self._order_repository.find_all()
        
        total_orders = len(all_orders)
        
        # Calculate revenue
        total_revenue = Decimal("0")
        pending_count = 0
        shipped_count = 0
        cancelled_count = 0
        
        for order in all_orders:
            if order.get('status') != 'cancelled':
                total_revenue += Decimal(str(order['total']))
            
            if order.get('status') == 'pending_payment':
                pending_count += 1
            elif order.get('status') == 'shipped':
                shipped_count += 1
            elif order.get('status') == 'cancelled':
                cancelled_count += 1
        
        report = f"""
===================== SALES REPORT =====================
Generated: {datetime.now().isoformat()}

Total Orders: {total_orders}
Total Revenue: ${total_revenue:.2f}
Pending Orders: {pending_count}
Shipped Orders: {shipped_count}
Cancelled Orders: {cancelled_count}

Average Order Value: ${(total_revenue / total_orders if total_orders > 0 else 0):.2f}

===================== END REPORT =====================
        """
        
        self._logger.info("Sales report generated", {
            "total_orders": total_orders,
            "revenue": float(total_revenue)
        })
        
        return report
    
    def _get_top_products(self, limit: int = 5) -> List[Dict]:
        """
        Get top selling products.
        
        Args:
            limit: Number of top products to return
        
        Returns:
            List of products with sales count
        """
        # Simplified implementation
        # In production, would aggregate from order items
        
        all_products = self._product_repository.find_all()
        
        # Mock data - in real implementation, calculate from orders
        top_products = []
        for i, product in enumerate(all_products[:limit]):
            top_products.append({
                'name': product['name'],
                'sold': 0,  # Would calculate from orders
                'revenue': 0.0
            })
        
        return top_products
    
    def get_revenue_by_period(self, period: str = 'daily') -> Dict:
        """
        Get revenue breakdown by time period.
        
        Args:
            period: 'daily', 'weekly', 'monthly'
        
        Returns:
            Revenue breakdown
        """
        # Simplified implementation
        # In production, would group orders by date
        
        all_orders = self._order_repository.find_all()
        
        revenue_data = {
            'period': period,
            'total_revenue': 0.0,
            'breakdown': []
        }
        
        total = Decimal("0")
        for order in all_orders:
            if order.get('status') != 'cancelled':
                total += Decimal(str(order['total']))
        
        revenue_data['total_revenue'] = float(total)
        
        return revenue_data
