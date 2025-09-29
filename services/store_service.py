"""
Store service layer

This module provides business logic for store management including CRUD operations,
search, filtering, and business status management.
"""
from typing import Optional, Tuple, List, Dict, Any
from datetime import date, datetime

from sqlalchemy import or_, and_, desc, asc, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from models import db, Store


class StoreService:
    """
    Service class for store-related business logic

    Handles all store operations including CRUD, search, filtering,
    and business status management with proper error handling and validation.
    """

    @staticmethod
    def get_stores_with_pagination(page: int = 1, per_page: Optional[int] = None,
                                 search: Optional[str] = None,
                                 status: Optional[str] = None,
                                 prefecture: Optional[str] = None,
                                 city: Optional[str] = None,
                                 sort_by: str = 'name',
                                 sort_order: str = 'asc'):
        """
        Get stores with pagination, search, and filtering

        Args:
            page: Page number (1-based)
            per_page: Items per page
            search: Search term for name/address
            status: Filter by business status
            prefecture: Filter by prefecture
            city: Filter by city
            sort_by: Field to sort by
            sort_order: Sort order (asc/desc)

        Returns:
            Tuple of (pagination_object, total_count)
        """
        # Default pagination settings
        if per_page is None:
            per_page = 20

        # Build base query
        query = Store.query

        # Apply search filter
        if search:
            search_pattern = f'%{search}%'
            query = query.filter(
                or_(
                    Store.name.ilike(search_pattern),
                    Store.address.ilike(search_pattern),
                    Store.location_prefecture.ilike(search_pattern),
                    Store.location_city.ilike(search_pattern)
                )
            )

        # Apply status filter
        if status:
            query = query.filter(Store.status == status)

        # Apply location filters
        if prefecture:
            query = query.filter(Store.location_prefecture == prefecture)
        if city:
            query = query.filter(Store.location_city == city)

        # Apply sorting
        sort_column = getattr(Store, sort_by, Store.name)
        if sort_order.lower() == 'desc':
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        # Add secondary sort by ID for consistency
        query = query.order_by(Store.id)

        # Get total count before pagination
        total_count = query.count()

        # Apply pagination
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        return pagination, total_count

    @staticmethod
    def get_store_by_id(store_id: int) -> Optional[Store]:
        """
        Get store by ID

        Args:
            store_id: Store ID

        Returns:
            Store instance or None if not found
        """
        try:
            return Store.query.get(store_id)
        except Exception:
            return None

    @staticmethod
    def create_store(name: str, address: str, phone: Optional[str] = None,
                    email: Optional[str] = None, business_hours: Optional[Dict] = None,
                    closed_days: str = '', status: str = 'active',
                    location_prefecture: Optional[str] = None,
                    location_city: Optional[str] = None,
                    establishment_date: Optional[date] = None) -> Tuple[bool, Store, str]:
        """
        Create new store

        Args:
            name: Store name
            address: Store address
            phone: Contact phone number
            email: Contact email address
            business_hours: Operating hours dictionary
            closed_days: Closed days string
            status: Business status
            location_prefecture: Prefecture
            location_city: City
            establishment_date: Establishment date

        Returns:
            Tuple of (success, store_instance, message)
        """
        try:
            # Validate required fields
            if not name or not name.strip():
                return False, None, "店舗名は必須です"

            if not address or not address.strip():
                return False, None, "住所は必須です"

            # Check for duplicate name
            existing_store = Store.query.filter(
                func.lower(Store.name) == func.lower(name.strip())
            ).first()

            if existing_store:
                return False, None, f"店舗名 '{name}' は既に存在します"

            # Validate status
            valid_statuses = ['active', 'inactive', 'temporarily_closed']
            if status not in valid_statuses:
                status = 'active'

            # Create store instance
            store = Store(
                name=name.strip(),
                address=address.strip(),
                phone=phone.strip() if phone else None,
                email=email.strip() if email else None,
                business_hours=business_hours,
                closed_days=closed_days,
                status=status,
                location_prefecture=location_prefecture.strip() if location_prefecture else None,
                location_city=location_city.strip() if location_city else None,
                establishment_date=establishment_date
            )

            # Save to database
            db.session.add(store)
            db.session.commit()

            return True, store, "店舗が正常に作成されました"

        except IntegrityError as e:
            db.session.rollback()
            return False, None, "データの整合性エラーが発生しました"

        except Exception as e:
            db.session.rollback()
            return False, None, f"店舗作成中にエラーが発生しました: {str(e)}"

    @staticmethod
    def update_store(store_id: int, name: Optional[str] = None,
                    address: Optional[str] = None, phone: Optional[str] = None,
                    email: Optional[str] = None, business_hours: Optional[Dict] = None,
                    closed_days: Optional[str] = None, status: Optional[str] = None,
                    location_prefecture: Optional[str] = None,
                    location_city: Optional[str] = None,
                    establishment_date: Optional[date] = None) -> Tuple[bool, Store, str]:
        """
        Update existing store

        Args:
            store_id: Store ID to update
            name: New store name
            address: New store address
            phone: New phone number
            email: New email address
            business_hours: New business hours
            closed_days: New closed days
            status: New business status
            location_prefecture: New prefecture
            location_city: New city
            establishment_date: New establishment date

        Returns:
            Tuple of (success, store_instance, message)
        """
        try:
            store = Store.query.get(store_id)
            if not store:
                return False, None, "店舗が見つかりません"

            # Validate name if provided
            if name is not None:
                name = name.strip()
                if not name:
                    return False, None, "店舗名は必須です"

                # Check for duplicate name (excluding current store)
                existing_store = Store.query.filter(
                    and_(
                        func.lower(Store.name) == func.lower(name),
                        Store.id != store_id
                    )
                ).first()

                if existing_store:
                    return False, None, f"店舗名 '{name}' は既に存在します"

                store.name = name

            # Validate address if provided
            if address is not None:
                address = address.strip()
                if not address:
                    return False, None, "住所は必須です"
                store.address = address

            # Update other fields if provided
            if phone is not None:
                store.phone = phone.strip() if phone else None

            if email is not None:
                store.email = email.strip() if email else None

            if business_hours is not None:
                store.business_hours = business_hours

            if closed_days is not None:
                store.closed_days = closed_days

            if status is not None:
                valid_statuses = ['active', 'inactive', 'temporarily_closed']
                if status in valid_statuses:
                    store.status = status

            if location_prefecture is not None:
                store.location_prefecture = location_prefecture.strip() if location_prefecture else None

            if location_city is not None:
                store.location_city = location_city.strip() if location_city else None

            if establishment_date is not None:
                store.establishment_date = establishment_date

            # Update timestamp
            store.updated_at = datetime.utcnow()

            # Save changes
            db.session.commit()

            return True, store, "店舗情報が正常に更新されました"

        except IntegrityError:
            db.session.rollback()
            return False, None, "データの整合性エラーが発生しました"

        except Exception as e:
            db.session.rollback()
            return False, None, f"店舗更新中にエラーが発生しました: {str(e)}"

    @staticmethod
    def delete_store(store_id: int) -> Tuple[bool, str]:
        """
        Delete store

        Args:
            store_id: Store ID to delete

        Returns:
            Tuple of (success, message)
        """
        try:
            store = Store.query.get(store_id)
            if not store:
                return False, "店舗が見つかりません"

            store_name = store.name

            # Check for dependencies (implement if needed)
            # For example, check if store has employees or other related records

            # Delete store
            db.session.delete(store)
            db.session.commit()

            return True, f"店舗 '{store_name}' が正常に削除されました"

        except Exception as e:
            db.session.rollback()
            return False, f"店舗削除中にエラーが発生しました: {str(e)}"

    @staticmethod
    def get_stores_by_status(status: str) -> List[Store]:
        """
        Get stores by business status

        Args:
            status: Business status to filter by

        Returns:
            List of stores with specified status
        """
        try:
            return Store.query.filter(Store.status == status).all()
        except Exception:
            return []

    @staticmethod
    def get_active_stores() -> List[Store]:
        """
        Get all active stores

        Returns:
            List of active stores
        """
        return StoreService.get_stores_by_status('active')

    @staticmethod
    def get_stores_by_location(prefecture: Optional[str] = None,
                             city: Optional[str] = None) -> List[Store]:
        """
        Get stores by location

        Args:
            prefecture: Prefecture to filter by
            city: City to filter by

        Returns:
            List of stores in specified location
        """
        try:
            query = Store.query

            if prefecture:
                query = query.filter(Store.location_prefecture == prefecture)
            if city:
                query = query.filter(Store.location_city == city)

            return query.all()
        except Exception:
            return []

    @staticmethod
    def search_stores(search_term: str) -> List[Store]:
        """
        Search stores by name or address

        Args:
            search_term: Term to search for

        Returns:
            List of matching stores
        """
        try:
            if not search_term:
                return []

            return Store.search(search_term).all()
        except Exception:
            return []

    @staticmethod
    def get_statistics() -> Dict[str, Any]:
        """
        Get store statistics

        Returns:
            Dictionary containing various statistics
        """
        try:
            # Basic counts
            total_stores = Store.query.count()
            active_stores = Store.query.filter(Store.status == 'active').count()
            inactive_stores = Store.query.filter(Store.status == 'inactive').count()
            temp_closed_stores = Store.query.filter(Store.status == 'temporarily_closed').count()

            # Location statistics
            prefecture_stats = db.session.query(
                Store.location_prefecture,
                func.count(Store.id).label('count')
            ).filter(Store.location_prefecture.isnot(None)).group_by(
                Store.location_prefecture
            ).order_by(desc('count')).all()

            # Business years statistics
            avg_business_years = db.session.query(
                func.avg(func.julianday('now') - func.julianday(Store.establishment_date))
            ).filter(Store.establishment_date.isnot(None)).scalar()

            if avg_business_years:
                avg_business_years = round(avg_business_years / 365.25, 1)
            else:
                avg_business_years = 0.0

            return {
                'total_stores': total_stores,
                'active_stores': active_stores,
                'inactive_stores': inactive_stores,
                'temporarily_closed_stores': temp_closed_stores,
                'prefecture_distribution': [
                    {'prefecture': pref, 'count': count}
                    for pref, count in prefecture_stats
                ],
                'average_business_years': avg_business_years
            }

        except Exception as e:
            return {
                'total_stores': 0,
                'active_stores': 0,
                'inactive_stores': 0,
                'temporarily_closed_stores': 0,
                'prefecture_distribution': [],
                'average_business_years': 0.0,
                'error': str(e)
            }

    @staticmethod
    def get_prefectures() -> List[str]:
        """
        Get list of unique prefectures

        Returns:
            List of prefecture names
        """
        try:
            result = db.session.query(Store.location_prefecture).filter(
                Store.location_prefecture.isnot(None)
            ).distinct().order_by(Store.location_prefecture).all()

            return [pref[0] for pref in result if pref[0]]
        except Exception:
            return []

    @staticmethod
    def get_cities_by_prefecture(prefecture: str) -> List[str]:
        """
        Get list of cities in specified prefecture

        Args:
            prefecture: Prefecture name

        Returns:
            List of city names
        """
        try:
            result = db.session.query(Store.location_city).filter(
                and_(
                    Store.location_prefecture == prefecture,
                    Store.location_city.isnot(None)
                )
            ).distinct().order_by(Store.location_city).all()

            return [city[0] for city in result if city[0]]
        except Exception:
            return []