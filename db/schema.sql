CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    alert_data JSONB NOT NULL,
    quantity INTEGER,
    strategy VARCHAR(50),
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
