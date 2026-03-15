-- =====================================================
-- Скрипт создания таблиц для Telegram Delivery Bot
-- Запуск: psql -U postgres -d delivery_bot -f create_tables.sql
-- =====================================================

-- Удаление существующих таблиц (если нужно пересоздать)
-- Будьте осторожны: это удалит все данные!
DROP TABLE IF EXISTS order_history CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS courier_status_history CASCADE;
DROP TABLE IF EXISTS user_cities CASCADE;
DROP TABLE IF EXISTS cities CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS broadcast_messages CASCADE;
DROP TABLE IF EXISTS logs CASCADE;

-- =====================================================
-- 1. Таблица пользователей (users)
-- =====================================================
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    username VARCHAR(255),
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    role VARCHAR(50) NOT NULL DEFAULT 'customer',
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    city VARCHAR(100),
    city_id INTEGER,
    partner_id BIGINT,
    is_blocked BOOLEAN DEFAULT FALSE,
    language_code VARCHAR(10) DEFAULT 'ru',
    last_activity TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Индексы для быстрого поиска
    CONSTRAINT valid_role CHECK (role IN ('admin', 'partner', 'manager', 'courier', 'customer')),
    CONSTRAINT valid_status CHECK (status IN ('active', 'inactive', 'blocked', 'free', 'busy', 'on_order'))
);

-- Индексы для users
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_city ON users(city);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_last_activity ON users(last_activity);
CREATE INDEX idx_users_username ON users(username);

-- Комментарии к таблице users
COMMENT ON TABLE users IS 'Пользователи бота';
COMMENT ON COLUMN users.user_id IS 'Telegram ID пользователя';
COMMENT ON COLUMN users.role IS 'Роль: admin, partner, manager, courier, customer';
COMMENT ON COLUMN users.status IS 'Статус: active, inactive, blocked, free, busy, on_order';

-- =====================================================
-- 2. Таблица городов (cities)
-- =====================================================
CREATE TABLE cities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    partner_id BIGINT REFERENCES users(user_id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE,
    delivery_price DECIMAL(10,2) DEFAULT 0,
    min_order_price DECIMAL(10,2) DEFAULT 0,
    working_hours_start TIME DEFAULT '09:00',
    working_hours_end TIME DEFAULT '21:00',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Индексы для cities
CREATE INDEX idx_cities_partner ON cities(partner_id);
CREATE INDEX idx_cities_active ON cities(is_active);

-- =====================================================
-- 3. Связь пользователей с городами (user_cities)
-- =====================================================
CREATE TABLE user_cities (
    user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
    city_id INTEGER REFERENCES cities(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP DEFAULT NOW(),
    assigned_by BIGINT REFERENCES users(user_id),
    PRIMARY KEY (user_id, city_id)
);

-- =====================================================
-- 4. Таблица заказов (orders)
-- =====================================================
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    order_number VARCHAR(50) UNIQUE,
    
    -- Связи
    customer_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE SET NULL,
    courier_id BIGINT REFERENCES users(user_id) ON DELETE SET NULL,
    manager_id BIGINT REFERENCES users(user_id) ON DELETE SET NULL,
    city_id INTEGER REFERENCES cities(id) ON DELETE SET NULL,
    
    -- Адреса
    pickup_address TEXT NOT NULL,
    pickup_location POINT,
    pickup_comment TEXT,
    delivery_address TEXT NOT NULL,
    delivery_location POINT,
    delivery_comment TEXT,
    
    -- Детали заказа
    description TEXT,
    parcel_type VARCHAR(50),
    parcel_weight DECIMAL(10,2),
    parcel_dimensions VARCHAR(50),
    
    -- Финансы
    price DECIMAL(10,2) NOT NULL DEFAULT 0,
    delivery_price DECIMAL(10,2) NOT NULL DEFAULT 0,
    commission DECIMAL(10,2) DEFAULT 0,
    payment_method VARCHAR(50) DEFAULT 'cash',
    
    -- Статусы
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    payment_status VARCHAR(50) DEFAULT 'unpaid',
    
    -- Временные метки
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    confirmed_at TIMESTAMP,
    assigned_at TIMESTAMP,
    picked_up_at TIMESTAMP,
    delivered_at TIMESTAMP,
    cancelled_at TIMESTAMP,
    cancelled_reason TEXT,
    
    -- Рейтинг
    customer_rating INTEGER CHECK (customer_rating >= 1 AND customer_rating <= 5),
    customer_review TEXT,
    courier_rating INTEGER CHECK (courier_rating >= 1 AND courier_rating <= 5),
    courier_review TEXT,
    
    -- Ограничения
    CONSTRAINT valid_status CHECK (status IN (
        'pending', 'confirmed', 'assigned', 'picking_up', 
        'delivering', 'delivered', 'cancelled', 'disputed'
    )),
    CONSTRAINT valid_payment CHECK (payment_method IN ('cash', 'card', 'online')),
    CONSTRAINT valid_payment_status CHECK (payment_status IN ('unpaid', 'paid', 'refunded'))
);

-- Индексы для orders
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_courier ON orders(courier_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_city ON orders(city_id);
CREATE INDEX idx_orders_created ON orders(created_at);
CREATE INDEX idx_orders_order_number ON orders(order_number);

-- Генерация номера заказа
CREATE OR REPLACE FUNCTION generate_order_number()
RETURNS TRIGGER AS $$
BEGIN
    NEW.order_number = 'ORD-' || TO_CHAR(NOW(), 'YYYYMMDD') || '-' || LPAD(NEW.id::TEXT, 6, '0');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_generate_order_number
    BEFORE INSERT ON orders
    FOR EACH ROW
    EXECUTE FUNCTION generate_order_number();

-- =====================================================
-- 5. История заказов (order_history)
-- =====================================================
CREATE TABLE order_history (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    user_id BIGINT REFERENCES users(user_id) ON DELETE SET NULL,
    old_status VARCHAR(50),
    new_status VARCHAR(50),
    comment TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_order_history_order ON order_history(order_id);
CREATE INDEX idx_order_history_created ON order_history(created_at);

-- =====================================================
-- 6. История статусов курьеров (courier_status_history)
-- =====================================================
CREATE TABLE courier_status_history (
    id SERIAL PRIMARY KEY,
    courier_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    old_status VARCHAR(50),
    new_status VARCHAR(50) NOT NULL,
    order_id INTEGER REFERENCES orders(id) ON DELETE SET NULL,
    location POINT,
    changed_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_courier_status_history ON courier_status_history(courier_id, changed_at);

-- =====================================================
-- 7. Таблица для рассылок (broadcast_messages)
-- =====================================================
CREATE TABLE broadcast_messages (
    id SERIAL PRIMARY KEY,
    admin_id BIGINT REFERENCES users(user_id) ON DELETE SET NULL,
    message_text TEXT NOT NULL,
    photo_id VARCHAR(255),
    recipients_count INTEGER DEFAULT 0,
    sent_count INTEGER DEFAULT 0,
    failed_count INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'draft',
    scheduled_for TIMESTAMP,
    sent_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT valid_broadcast_status CHECK (status IN ('draft', 'scheduled', 'sending', 'completed', 'cancelled'))
);

-- =====================================================
-- 8. Таблица для логов (logs)
-- =====================================================
CREATE TABLE logs (
    id SERIAL PRIMARY KEY,
    level VARCHAR(20) NOT NULL,
    module VARCHAR(100),
    user_id BIGINT REFERENCES users(user_id) ON DELETE SET NULL,
    message TEXT NOT NULL,
    data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_logs_level ON logs(level);
CREATE INDEX idx_logs_created ON logs(created_at);
CREATE INDEX idx_logs_user ON logs(user_id);

-- =====================================================
-- 9. Функция обновления timestamp
-- =====================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Триггеры для автоматического обновления updated_at
CREATE TRIGGER trigger_update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_update_orders_updated_at
    BEFORE UPDATE ON orders
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_update_cities_updated_at
    BEFORE UPDATE ON cities
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- 10. Начальные данные
-- =====================================================

-- Добавляем тестовые города
INSERT INTO cities (name, is_active) VALUES
    ('Москва', TRUE),
    ('Санкт-Петербург', TRUE),
    ('Казань', TRUE)
ON CONFLICT (name) DO NOTHING;

-- =====================================================
-- 11. Полезные представления (views)
-- =====================================================

-- Статистика по пользователям
CREATE OR REPLACE VIEW v_user_stats AS
SELECT 
    role,
    COUNT(*) as total,
    COUNT(CASE WHEN status = 'active' THEN 1 END) as active,
    COUNT(CASE WHEN created_at > NOW() - INTERVAL '7 days' THEN 1 END) as new_this_week
FROM users
GROUP BY role;

-- Активные заказы
CREATE OR REPLACE VIEW v_active_orders AS
SELECT 
    o.*,
    c.full_name as customer_name,
    c.phone as customer_phone,
    cou.full_name as courier_name,
    cou.phone as courier_phone,
    cit.name as city_name
FROM orders o
LEFT JOIN users c ON o.customer_id = c.user_id
LEFT JOIN users cou ON o.courier_id = cou.user_id
LEFT JOIN cities cit ON o.city_id = cit.id
WHERE o.status NOT IN ('delivered', 'cancelled');

-- =====================================================
-- 12. Индексы для производительности
-- =====================================================

-- Составные индексы для частых запросов
CREATE INDEX idx_orders_customer_status ON orders(customer_id, status);
CREATE INDEX idx_orders_courier_status ON orders(courier_id, status);
CREATE INDEX idx_orders_city_status ON orders(city_id, status);
CREATE INDEX idx_orders_date_status ON orders(DATE(created_at), status);

-- Индекс для полнотекстового поиска по адресам
CREATE INDEX idx_orders_addresses ON orders USING GIN (
    to_tsvector('russian', coalesce(pickup_address, '') || ' ' || coalesce(delivery_address, ''))
);

-- =====================================================
-- 13. Функции для работы с заказами
-- =====================================================

-- Функция для получения статистики курьера
CREATE OR REPLACE FUNCTION get_courier_stats(
    p_courier_id BIGINT,
    p_start_date DATE DEFAULT NOW() - INTERVAL '30 days',
    p_end_date DATE DEFAULT NOW()
)
RETURNS TABLE (
    total_orders BIGINT,
    completed_orders BIGINT,
    cancelled_orders BIGINT,
    total_earnings DECIMAL,
    avg_rating NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::BIGINT as total_orders,
        COUNT(CASE WHEN status = 'delivered' THEN 1 END)::BIGINT as completed_orders,
        COUNT(CASE WHEN status = 'cancelled' THEN 1 END)::BIGINT as cancelled_orders,
        COALESCE(SUM(CASE WHEN status = 'delivered' THEN delivery_price ELSE 0 END), 0) as total_earnings,
        COALESCE(AVG(courier_rating), 0)::NUMERIC(3,2) as avg_rating
    FROM orders
    WHERE courier_id = p_courier_id
        AND DATE(created_at) BETWEEN p_start_date AND p_end_date;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 14. Права доступа
-- =====================================================

-- Даем права только нужному пользователю
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO delivery_bot_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO delivery_bot_user;

-- =====================================================
-- Конец скрипта
-- =====================================================