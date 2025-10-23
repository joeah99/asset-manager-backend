CREATE TABLE IF NOT EXISTS User (
    user_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    username VARCHAR(100) NOT NULL UNIQUE,
    hashed_password TEXT NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    company VARCHAR(255),
    created_at DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS UserPreferences (
    preference_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    column_preferences TEXT NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES User(user_id)
);

CREATE TABLE IF NOT EXISTS ForgotPasswordToken (
    token_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    token_hash TEXT NOT NULL,
    email VARCHAR(255) NOT NULL,
    created_at DATETIME NOT NULL,
    FOREIGN KEY (email) REFERENCES User(email)
);

CREATE TABLE IF NOT EXISTS Asset (
    asset_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    asset_type VARCHAR(50) NOT NULL,
    initial_book_value DECIMAL(18,2) NOT NULL,
    manufacturer VARCHAR(255) NOT NULL,
    model VARCHAR(255) NOT NULL,
    model_year VARCHAR(4) NOT NULL,
    `usage` INT NOT NULL,
    `condition` VARCHAR(50) NOT NULL,
    country VARCHAR(100) NOT NULL,
    state_us VARCHAR(50),
    deleted BOOLEAN NOT NULL DEFAULT 0,
    depreciation_method VARCHAR(50),
    salvage_value DECIMAL(18,2),
    useful_life INT,
    depreciation_rate DECIMAL(18,2),
    total_expected_units_production INT,
    units_produced_in_year INT,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES User(user_id)
);

CREATE TABLE IF NOT EXISTS AssetDepreciationSchedule (
    asset_depreciation_schedule_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    asset_id BIGINT NOT NULL,
    depreciation_date VARCHAR(10) NOT NULL,
    new_book_value DECIMAL(18,2) NOT NULL,
    created_at DATETIME NOT NULL,
    FOREIGN KEY (asset_id) REFERENCES Asset(asset_id)
);

CREATE TABLE IF NOT EXISTS LoanInformation (
    loan_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    asset_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    lender_name VARCHAR(255) NOT NULL,
    loan_amount DECIMAL(18,2) NOT NULL,
    interest_rate DECIMAL(5,2) NOT NULL,
    loan_term_years INT NOT NULL,
    remaining_balance DECIMAL(18,2) NOT NULL,
    monthly_payment DECIMAL(18,2) NOT NULL,
    payment_frequency VARCHAR(50) NOT NULL,
    loan_status VARCHAR(50) NOT NULL,
    last_payment_date VARCHAR(10),
    last_payment_amount DECIMAL(18,2),
    next_payment_date VARCHAR(10),
    loan_start_date VARCHAR(10) NOT NULL,
    loan_end_date VARCHAR(10) NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (asset_id) REFERENCES Asset(asset_id),
    FOREIGN KEY (user_id) REFERENCES User(user_id)
);

CREATE TABLE IF NOT EXISTS LoanProjectedPayments (
    loan_projected_payment_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    loan_id BIGINT NOT NULL,
    loan_payment_date VARCHAR(10) NOT NULL,
    new_remaining_value DECIMAL(18,2) NOT NULL,
    created_at DATETIME NOT NULL,
    FOREIGN KEY (loan_id) REFERENCES LoanInformation(loan_id)
);

CREATE TABLE IF NOT EXISTS EquipmentValuationLog (
    log_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    asset_id BIGINT NOT NULL,
    valuation_date DATETIME NOT NULL,
    unadjusted_fair_market_value DECIMAL(18,2),
    unadjusted_orderly_liquidation_value DECIMAL(18,2),
    unadjusted_forced_liquidation_value DECIMAL(18,2),
    adjusted_fair_market_value DECIMAL(18,2),
    adjusted_orderly_liquidation_value DECIMAL(18,2),
    adjusted_forced_liquidation_value DECIMAL(18,2),
    salvage DECIMAL(18,2),
    FOREIGN KEY (asset_id) REFERENCES Asset(asset_id)
);

CREATE TABLE IF NOT EXISTS VehicleValuationLog (
    log_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    asset_id BIGINT NOT NULL,
    valuation_date DATETIME NOT NULL,
    unadjusted_low DECIMAL(18,2),
    unadjusted_high DECIMAL(18,2),
    unadjusted_finance DECIMAL(18,2),
    unadjusted_retail DECIMAL(18,2),
    unadjusted_wholesale DECIMAL(18,2),
    unadjusted_trade_in DECIMAL(18,2),
    adjusted_low DECIMAL(18,2),
    adjusted_high DECIMAL(18,2),
    adjusted_finance DECIMAL(18,2),
    adjusted_retail DECIMAL(18,2),
    adjusted_wholesale DECIMAL(18,2),
    adjusted_trade_in DECIMAL(18,2),
    FOREIGN KEY (asset_id) REFERENCES Asset(asset_id)
);
