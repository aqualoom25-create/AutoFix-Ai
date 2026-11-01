-- AutoFix AI — Database Schema (PostgreSQL / SQLite Compatible Foundation)
-- Target Vehicle Platform: 2013 Maruti Suzuki Alto 800 (0.8L F8D MPFI Petrol)

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT DEFAULT 'Alto 800 Owner',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS vehicles (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    brand TEXT NOT NULL,
    model TEXT NOT NULL,
    year INTEGER NOT NULL,
    engine TEXT,
    variant TEXT,
    fuel_type TEXT,
    vin TEXT,
    registration_number TEXT,
    odometer_km INTEGER DEFAULT 68500,
    obd_protocol TEXT DEFAULT 'ISO 14230-4 KWP2000 (Fast Init) / ISO 15765-4 CAN',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS diagnostic_sessions (
    id UUID PRIMARY KEY,
    vehicle_id UUID REFERENCES vehicles(id),
    symptoms JSONB,
    dtc_codes JSONB,
    live_telemetry JSONB,
    qa_responses JSONB,
    diagnosis JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS repair_records (
    id UUID PRIMARY KEY,
    vehicle_id UUID REFERENCES vehicles(id),
    diagnosis_id UUID REFERENCES diagnostic_sessions(id),
    repair_description TEXT,
    replaced_parts JSONB,
    before_test JSONB,
    after_test JSONB,
    verified BOOLEAN DEFAULT FALSE,
    verification_report JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
