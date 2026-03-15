import asyncpg
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date
from dataclasses import dataclass
from enum import Enum


class UserRole(str, Enum):
    """Роли пользователей"""
    ADMIN = "admin"
    PARTNER = "partner"
    MANAGER = "manager"
    COURIER = "courier"
    CUSTOMER = "customer"


class UserStatus(str, Enum):
    """Статусы пользователей"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    BLOCKED = "blocked"
    FREE = "free"
    BUSY = "busy"
    ON_ORDER = "on_order"


class OrderStatus(str, Enum):
    """Статусы заказов"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    ASSIGNED = "assigned"
    PICKING_UP = "picking_up"
    DELIVERING = "delivering"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"


class PaymentMethod(str, Enum):
    """Способы оплаты"""
    CASH = "cash"
    CARD = "card"
    ONLINE = "online"


class PaymentStatus(str, Enum):
    """Статусы оплаты"""
    UNPAID = "unpaid"
    PAID = "paid"
    REFUNDED = "refunded"


@dataclass
class User:
    """Модель пользователя"""
    user_id: int
    username: Optional[str]
    full_name: str
    phone: Optional[str]
    role: UserRole
    status: UserStatus
    city: Optional[str]
    city_id: Optional[int]
    partner_id: Optional[int]
    is_blocked: bool
    language_code: str
    last_activity: datetime
    created_at: datetime
    updated_at: datetime


@dataclass
class Order:
    """Модель заказа"""
    id: int
    order_number: str
    customer_id: int
    courier_id: Optional[int]
    manager_id: Optional[int]
    city_id: Optional[int]
    pickup_address: str
    pickup_location: Optional[str]
    pickup_comment: Optional[str]
    delivery_address: str
    delivery_location: Optional[str]
    delivery_comment: Optional[str]
    description: Optional[str]
    parcel_type: Optional[str]
    parcel_weight: Optional[float]
    parcel_dimensions: Optional[str]
    price: float
    delivery_price: float
    commission: float
    payment_method: PaymentMethod
    status: OrderStatus
    payment_status: PaymentStatus
    created_at: datetime
    updated_at: datetime
    confirmed_at: Optional[datetime]
    assigned_at: Optional[datetime]
    picked_up_at: Optional[datetime]
    delivered_at: Optional[datetime]
    cancelled_at: Optional[datetime]
    cancelled_reason: Optional[str]
    customer_rating: Optional[int]
    customer_review: Optional[str]
    courier_rating: Optional[int]
    courier_review: Optional[str]


@dataclass
class City:
    """Модель города"""
    id: int
    name: str
    partner_id: Optional[int]
    is_active: bool
    delivery_price: float
    min_order_price: float
    working_hours_start: str
    working_hours_end: str
    created_at: datetime
    updated_at: datetime


class Repository:
    """Базовый класс репозитория"""

    def __init__(self, conn: asyncpg.Connection):
        self.conn = conn

    async def fetch(self, query: str, *args) -> List[Dict[str, Any]]:
        """Выполнить запрос и вернуть список записей"""
        return await self.conn.fetch(query, *args)

    async def fetchrow(self, query: str, *args) -> Optional[Dict[str, Any]]:
        """Выполнить запрос и вернуть одну запись"""
        return await self.conn.fetchrow(query, *args)

    async def fetchval(self, query: str, *args) -> Any:
        """Выполнить запрос и вернуть одно значение"""
        return await self.conn.fetchval(query, *args)

    async def execute(self, query: str, *args) -> str:
        """Выполнить запрос без возврата данных"""
        return await self.conn.execute(query, *args)

    def transaction(self):
        """Создать транзакцию"""
        return self.conn.transaction()


class UserRepository(Repository):
    """Репозиторий для работы с пользователями"""

    async def create_user(
        self,
        user_id: int,
        username: Optional[str],
        full_name: str,
        phone: Optional[str] = None,
        role: UserRole = UserRole.CUSTOMER,
        city: Optional[str] = None,
        language_code: str = "ru"
    ) -> Dict[str, Any]:
        """Создать нового пользователя или обновить существующего"""
        return await self.fetchrow(
            """
            INSERT INTO users (
                user_id, username, full_name, phone, role, status,
                city, language_code, last_activity, created_at, updated_at
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW(), NOW(), NOW())
            ON CONFLICT (user_id) DO UPDATE
            SET username = EXCLUDED.username,
                full_name = EXCLUDED.full_name,
                phone = COALESCE(EXCLUDED.phone, users.phone),
                updated_at = NOW()
            RETURNING *
            """,
            user_id, username, full_name, phone, role.value, UserStatus.ACTIVE.value,
            city, language_code
        )

    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получить пользователя по ID"""
        return await self.fetchrow(
            "SELECT * FROM users WHERE user_id = $1",
            user_id
        )

    async def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Получить пользователя по username"""
        return await self.fetchrow(
            "SELECT * FROM users WHERE username = $1",
            username.lstrip('@')
        )

    async def update_user(
        self,
        user_id: int,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Обновить данные пользователя"""
        allowed_fields = {'full_name', 'phone', 'city', 'language_code'}
        updates = []
        values = []
        param_index = 1

        for field, value in kwargs.items():
            if field in allowed_fields:
                updates.append(f"{field} = ${param_index}")
                values.append(value)
                param_index += 1

        if not updates:
            return await self.get_user(user_id)

        updates.append("updated_at = NOW()")
        values.append(user_id)

        query = f"""
            UPDATE users 
            SET {', '.join(updates)}
            WHERE user_id = ${param_index}
            RETURNING *
        """

        return await self.fetchrow(query, *values)

    async def update_role(self, user_id: int, role: UserRole) -> bool:
        """Обновить роль пользователя"""
        result = await self.execute(
            "UPDATE users SET role = $1, updated_at = NOW() WHERE user_id = $2",
            role.value, user_id
        )
        return "UPDATE 1" in result

    async def update_status(self, user_id: int, status: UserStatus) -> bool:
        """Обновить статус пользователя"""
        result = await self.execute(
            "UPDATE users SET status = $1, updated_at = NOW() WHERE user_id = $2",
            status.value, user_id
        )
        return "UPDATE 1" in result

    async def update_last_activity(self, user_id: int) -> None:
        """Обновить время последней активности"""
        await self.execute(
            "UPDATE users SET last_activity = NOW() WHERE user_id = $1",
            user_id
        )

    async def block_user(self, user_id: int) -> bool:
        """Заблокировать пользователя"""
        result = await self.execute(
            "UPDATE users SET is_blocked = TRUE, status = $1, updated_at = NOW() "
            "WHERE user_id = $2",
            UserStatus.BLOCKED.value, user_id
        )
        return "UPDATE 1" in result

    async def unblock_user(self, user_id: int) -> bool:
        """Разблокировать пользователя"""
        result = await self.execute(
            "UPDATE users SET is_blocked = FALSE, status = $1, updated_at = NOW() "
            "WHERE user_id = $2",
            UserStatus.ACTIVE.value, user_id
        )
        return "UPDATE 1" in result

    async def get_all_users(
        self,
        limit: int = 1000,
        offset: int = 0,
        only_active: bool = True
    ) -> List[Dict[str, Any]]:
        """Получить всех пользователей"""
        query = """
            SELECT user_id, username, full_name, phone, role, status,
                   city, language_code, last_activity, created_at
            FROM users
            WHERE ($1::boolean IS FALSE OR is_blocked = FALSE)
            ORDER BY created_at DESC
            LIMIT $2 OFFSET $3
        """
        return await self.fetch(query, only_active, limit, offset)

    async def get_total_users(self, only_active: bool = True) -> int:
        """Получить общее количество пользователей"""
        query = """
            SELECT COUNT(*)
            FROM users
            WHERE ($1::boolean IS FALSE OR is_blocked = FALSE)
        """
        return await self.fetchval(query, only_active) or 0

    async def get_users_by_role(self) -> Dict[str, int]:
        """Получить статистику пользователей по ролям"""
        rows = await self.fetch(
            "SELECT role, COUNT(*) as count "
            "FROM users WHERE is_blocked = FALSE "
            "GROUP BY role"
        )
        return {row['role']: row['count'] for row in rows}

    async def get_users_by_city(self, city_id: int) -> List[Dict[str, Any]]:
        """Получить пользователей города"""
        return await self.fetch(
            """
            SELECT u.* FROM users u
            JOIN user_cities uc ON u.user_id = uc.user_id
            WHERE uc.city_id = $1 AND u.is_blocked = FALSE
            """,
            city_id
        )

    async def get_users_count_by_date(
        self,
        start_date: Union[datetime, date],
        end_date: Union[datetime, date]
    ) -> int:
        """Получить количество новых пользователей за период"""
        return await self.fetchval(
            """
            SELECT COUNT(*) FROM users
            WHERE created_at BETWEEN $1 AND $2
            AND is_blocked = FALSE
            """,
            start_date, end_date
        ) or 0

    async def get_admins(self) -> List[Dict[str, Any]]:
        """Получить всех администраторов"""
        return await self.fetch(
            "SELECT user_id, username, full_name FROM users WHERE role = $1",
            UserRole.ADMIN.value
        )

    async def get_couriers(
        self,
        city_id: Optional[int] = None,
        status: Optional[UserStatus] = None
    ) -> List[Dict[str, Any]]:
        """Получить курьеров"""
        query = """
            SELECT u.* FROM users u
            WHERE u.role = $1 AND u.is_blocked = FALSE
        """
        params = [UserRole.COURIER.value]

        if city_id:
            query += " AND u.city_id = $2"
            params.append(city_id)

        if status:
            if city_id:
                query += " AND u.status = $3"
            else:
                query += " AND u.status = $2"
            params.append(status.value)

        query += " ORDER BY u.last_activity DESC"

        return await self.fetch(query, *params)

    async def get_inactive_couriers(self, hours: int = 6) -> List[Dict[str, Any]]:
        """Получить курьеров, которые давно не обновляли статус"""
        return await self.fetch(
            """
            SELECT user_id, username, full_name, status, last_activity
            FROM users
            WHERE role = $1
            AND status IN ($2, $3)
            AND last_activity < NOW() - $4::interval
            """,
            UserRole.COURIER.value,
            UserStatus.FREE.value,
            UserStatus.BUSY.value,
            f"{hours} hours"
        )

    async def update_courier_status(
        self,
        user_id: int,
        status: UserStatus,
        order_id: Optional[int] = None
    ) -> bool:
        """Обновить статус курьера"""
        async with self.transaction():
            # Обновляем статус
            result = await self.execute(
                """
                UPDATE users
                SET status = $1, last_activity = NOW(), updated_at = NOW()
                WHERE user_id = $2 AND role = $3
                """,
                status.value, user_id, UserRole.COURIER.value
            )

            # Логируем изменение статуса
            if order_id:
                await self.execute(
                    """
                    INSERT INTO courier_status_history
                    (courier_id, new_status, order_id, changed_at)
                    VALUES ($1, $2, $3, NOW())
                    """,
                    user_id, status.value, order_id
                )

        return "UPDATE 1" in result

    async def assign_to_city(self, user_id: int, city_id: int, assigned_by: int) -> bool:
        """Назначить пользователя в город"""
        try:
            await self.execute(
                """
                INSERT INTO user_cities (user_id, city_id, assigned_by, assigned_at)
                VALUES ($1, $2, $3, NOW())
                ON CONFLICT (user_id, city_id) DO NOTHING
                """,
                user_id, city_id, assigned_by
            )
            return True
        except Exception:
            return False

    async def remove_from_city(self, user_id: int, city_id: int) -> bool:
        """Удалить пользователя из города"""
        result = await self.execute(
            "DELETE FROM user_cities WHERE user_id = $1 AND city_id = $2",
            user_id, city_id
        )
        return "DELETE 1" in result


class OrderRepository(Repository):
    """Репозиторий для работы с заказами"""

    async def create_order(
        self,
        customer_id: int,
        pickup_address: str,
        delivery_address: str,
        description: Optional[str] = None,
        city_id: Optional[int] = None,
        parcel_type: Optional[str] = None,
        parcel_weight: Optional[float] = None,
        price: float = 0,
        delivery_price: float = 0,
        payment_method: PaymentMethod = PaymentMethod.CASH
    ) -> Dict[str, Any]:
        """Создать новый заказ"""
        return await self.fetchrow(
            """
            INSERT INTO orders (
                customer_id, city_id, pickup_address, delivery_address,
                description, parcel_type, parcel_weight, price,
                delivery_price, payment_method, status, payment_status,
                created_at, updated_at
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, NOW(), NOW())
            RETURNING *
            """,
            customer_id, city_id, pickup_address, delivery_address,
            description, parcel_type, parcel_weight, price,
            delivery_price, payment_method.value, OrderStatus.PENDING.value,
            PaymentStatus.UNPAID.value
        )

    async def get_order(self, order_id: int) -> Optional[Dict[str, Any]]:
        """Получить заказ по ID"""
        return await self.fetchrow(
            "SELECT * FROM orders WHERE id = $1",
            order_id
        )

    async def get_order_full(self, order_id: int) -> Optional[Dict[str, Any]]:
        """Получить полную информацию о заказе"""
        return await self.fetchrow(
            """
            SELECT o.*,
                   c.full_name as customer_name,
                   c.username as customer_username,
                   c.phone as customer_phone,
                   cou.full_name as courier_name,
                   cou.phone as courier_phone,
                   cit.name as city_name
            FROM orders o
            LEFT JOIN users c ON o.customer_id = c.user_id
            LEFT JOIN users cou ON o.courier_id = cou.user_id
            LEFT JOIN cities cit ON o.city_id = cit.id
            WHERE o.id = $1
            """,
            order_id
        )

    async def get_order_by_number(self, order_number: str) -> Optional[Dict[str, Any]]:
        """Получить заказ по номеру"""
        return await self.fetchrow(
            "SELECT * FROM orders WHERE order_number = $1",
            order_number
        )

    async def update_order_status(
        self,
        order_id: int,
        status: OrderStatus,
        user_id: Optional[int] = None
    ) -> bool:
        """Обновить статус заказа"""
        # Определяем поле для временной метки в зависимости от статуса
        time_field = {
            OrderStatus.CONFIRMED: "confirmed_at",
            OrderStatus.ASSIGNED: "assigned_at",
            OrderStatus.PICKING_UP: "picked_up_at",
            OrderStatus.DELIVERED: "delivered_at",
            OrderStatus.CANCELLED: "cancelled_at"
        }.get(status)

        query = "UPDATE orders SET status = $1, updated_at = NOW()"
        params = [status.value]

        if time_field:
            query += f", {time_field} = NOW()"
            if status == OrderStatus.CANCELLED:
                query += ", cancelled_reason = $3"
                params.append("Отменен пользователем")

        query += " WHERE id = $" + str(len(params) + 1)
        params.append(order_id)

        result = await self.execute(query, *params)

        # Логируем изменение статуса
        await self.execute(
            """
            INSERT INTO order_history (order_id, user_id, new_status, created_at)
            VALUES ($1, $2, $3, NOW())
            """,
            order_id, user_id, status.value
        )

        return "UPDATE 1" in result

    async def assign_courier(
        self,
        order_id: int,
        courier_id: int,
        manager_id: Optional[int] = None
    ) -> bool:
        """Назначить курьера на заказ"""
        async with self.transaction():
            result = await self.execute(
                """
                UPDATE orders
                SET courier_id = $1, status = $2, assigned_at = NOW(), updated_at = NOW()
                WHERE id = $3
                """,
                courier_id, OrderStatus.ASSIGNED.value, order_id
            )

            # Обновляем статус курьера
            user_repo = UserRepository(self.conn)
            await user_repo.update_courier_status(
                courier_id,
                UserStatus.ON_ORDER,
                order_id
            )

        return "UPDATE 1" in result

    async def get_user_orders(
        self,
        user_id: int,
        role: str = "customer",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Получить заказы пользователя"""
        field = "customer_id" if role == "customer" else "courier_id"

        return await self.fetch(
            f"""
            SELECT o.*,
                   c.full_name as customer_name,
                   cou.full_name as courier_name
            FROM orders o
            LEFT JOIN users c ON o.customer_id = c.user_id
            LEFT JOIN users cou ON o.courier_id = cou.user_id
            WHERE o.{field} = $1
            ORDER BY o.created_at DESC
            LIMIT $2
            """,
            user_id, limit
        )

    async def get_available_orders(
        self,
        city_id: Optional[int] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Получить доступные для взятия заказы"""
        query = """
            SELECT o.*,
                   c.full_name as customer_name,
                   c.phone as customer_phone,
                   cit.name as city_name
            FROM orders o
            LEFT JOIN users c ON o.customer_id = c.user_id
            LEFT JOIN cities cit ON o.city_id = cit.id
            WHERE o.status = $1
        """
        params = [OrderStatus.PENDING.value]

        if city_id:
            query += " AND o.city_id = $2"
            params.append(city_id)

        query += " ORDER BY o.created_at LIMIT $3"
        params.append(limit)

        return await self.fetch(query, *params)

    async def get_courier_orders(
        self,
        courier_id: int,
        status: Optional[OrderStatus] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Получить заказы курьера"""
        query = """
            SELECT o.*,
                   c.full_name as customer_name,
                   c.phone as customer_phone
            FROM orders o
            LEFT JOIN users c ON o.customer_id = c.user_id
            WHERE o.courier_id = $1
        """
        params = [courier_id]

        if status:
            query += " AND o.status = $2"
            params.append(status.value)

        query += " ORDER BY o.created_at DESC LIMIT $3"
        params.append(limit)

        return await self.fetch(query, *params)

    async def get_all_orders(
        self,
        status: Optional[OrderStatus] = None,
        city_id: Optional[int] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Получить все заказы"""
        query = """
            SELECT o.*,
                   c.full_name as customer_name,
                   cou.full_name as courier_name,
                   cit.name as city_name
            FROM orders o
            LEFT JOIN users c ON o.customer_id = c.user_id
            LEFT JOIN users cou ON o.courier_id = cou.user_id
            LEFT JOIN cities cit ON o.city_id = cit.id
            WHERE 1=1
        """
        params = []

        if status:
            query += f" AND o.status = ${len(params) + 1}"
            params.append(status.value)

        if city_id:
            query += f" AND o.city_id = ${len(params) + 1}"
            params.append(city_id)

        query += f" ORDER BY o.created_at DESC LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}"
        params.extend([limit, offset])

        return await self.fetch(query, *params)

    async def get_orders_count(
        self,
        status: Optional[OrderStatus] = None,
        city_id: Optional[int] = None
    ) -> int:
        """Получить количество заказов"""
        query = "SELECT COUNT(*) FROM orders WHERE 1=1"
        params = []

        if status:
            query += f" AND status = ${len(params) + 1}"
            params.append(status.value)

        if city_id:
            query += f" AND city_id = ${len(params) + 1}"
            params.append(city_id)

        return await self.fetchval(query, *params) or 0

    async def get_orders_stats(
        self,
        start_date: Union[datetime, date],
        end_date: Union[datetime, date]
    ) -> Dict[str, Any]:
        """Получить статистику заказов за период"""
        stats = await self.fetchrow(
            """
            SELECT
                COUNT(*) as total,
                COUNT(CASE WHEN status = 'delivered' THEN 1 END) as completed,
                COUNT(CASE WHEN status = 'cancelled' THEN 1 END) as cancelled,
                COALESCE(SUM(CASE WHEN status = 'delivered' THEN price ELSE 0 END), 0) as revenue,
                COALESCE(AVG(CASE WHEN status = 'delivered' THEN price END), 0) as avg_check
            FROM orders
            WHERE created_at BETWEEN $1 AND $2
            """,
            start_date, end_date
        )

        return dict(stats) if stats else {}

    async def get_courier_stats(
        self,
        courier_id: int,
        days: int = 30
    ) -> Dict[str, Any]:
        """Получить статистику курьера"""
        stats = await self.fetchrow(
            """
            SELECT
                COUNT(*) as total_orders,
                COUNT(CASE WHEN status = 'delivered' THEN 1 END) as completed_orders,
                COUNT(CASE WHEN status = 'cancelled' THEN 1 END) as cancelled_orders,
                COALESCE(SUM(CASE WHEN status = 'delivered' THEN delivery_price ELSE 0 END), 0) as total_earnings,
                COALESCE(AVG(courier_rating), 0) as avg_rating
            FROM orders
            WHERE courier_id = $1
            AND created_at > NOW() - $2::interval
            """,
            courier_id, f"{days} days"
        )

        return dict(stats) if stats else {}

    async def rate_order(
        self,
        order_id: int,
        rating: int,
        review: Optional[str] = None,
        as_customer: bool = True
    ) -> bool:
        """Оценить заказ"""
        field = "customer_rating" if as_customer else "courier_rating"
        review_field = "customer_review" if as_customer else "courier_review"

        result = await self.execute(
            f"""
            UPDATE orders
            SET {field} = $1, {review_field} = $2, updated_at = NOW()
            WHERE id = $3 AND status = 'delivered'
            """,
            rating, review, order_id
        )

        return "UPDATE 1" in result


class CityRepository(Repository):
    """Репозиторий для работы с городами"""

    async def create_city(
        self,
        name: str,
        partner_id: Optional[int] = None,
        delivery_price: float = 0,
        min_order_price: float = 0,
        working_hours_start: str = "09:00",
        working_hours_end: str = "21:00"
    ) -> Dict[str, Any]:
        """Создать новый город"""
        return await self.fetchrow(
            """
            INSERT INTO cities (
                name, partner_id, delivery_price, min_order_price,
                working_hours_start, working_hours_end, created_at, updated_at
            )
            VALUES ($1, $2, $3, $4, $5, $6, NOW(), NOW())
            RETURNING *
            """,
            name, partner_id, delivery_price, min_order_price,
            working_hours_start, working_hours_end
        )

    async def get_city(self, city_id: int) -> Optional[Dict[str, Any]]:
        """Получить город по ID"""
        return await self.fetchrow(
            "SELECT * FROM cities WHERE id = $1",
            city_id
        )

    async def get_city_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Получить город по названию"""
        return await self.fetchrow(
            "SELECT * FROM cities WHERE name = $1",
            name
        )

    async def get_all_cities(self, only_active: bool = True) -> List[Dict[str, Any]]:
        """Получить все города"""
        query = "SELECT * FROM cities"
        if only_active:
            query += " WHERE is_active = TRUE"
        query += " ORDER BY name"

        return await self.fetch(query)

    async def update_city(self, city_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """Обновить данные города"""
        allowed_fields = {
            'name', 'partner_id', 'is_active', 'delivery_price',
            'min_order_price', 'working_hours_start', 'working_hours_end'
        }

        updates = []
        values = []
        param_index = 1

        for field, value in kwargs.items():
            if field in allowed_fields:
                updates.append(f"{field} = ${param_index}")
                values.append(value)
                param_index += 1

        if not updates:
            return await self.get_city(city_id)

        updates.append("updated_at = NOW()")
        values.append(city_id)

        query = f"""
            UPDATE cities
            SET {', '.join(updates)}
            WHERE id = ${param_index}
            RETURNING *
        """

        return await self.fetchrow(query, *values)

    async def delete_city(self, city_id: int) -> bool:
        """Удалить город (мягкое удаление)"""
        result = await self.execute(
            "UPDATE cities SET is_active = FALSE, updated_at = NOW() WHERE id = $1",
            city_id
        )
        return "UPDATE 1" in result

    async def get_city_stats(self, city_id: int) -> Dict[str, Any]:
        """Получить статистику по городу"""
        stats = await self.fetchrow(
            """
            SELECT
                (SELECT COUNT(*) FROM users u
                 JOIN user_cities uc ON u.user_id = uc.user_id
                 WHERE uc.city_id = $1) as total_users,
                (SELECT COUNT(*) FROM users u
                 JOIN user_cities uc ON u.user_id = uc.user_id
                 WHERE uc.city_id = $1 AND u.role = 'courier') as total_couriers,
                (SELECT COUNT(*) FROM orders WHERE city_id = $1) as total_orders,
                (SELECT COUNT(*) FROM orders WHERE city_id = $1 AND status = 'delivered') as completed_orders,
                (SELECT COALESCE(SUM(price), 0) FROM orders WHERE city_id = $1 AND status = 'delivered') as total_revenue
            """,
            city_id
        )

        return dict(stats) if stats else {}