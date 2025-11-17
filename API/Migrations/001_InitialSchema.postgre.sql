-- This has been converted from SQL Server to PostgreSQL

-- Create User table
CREATE TABLE IF NOT EXISTS public."User" (
    user_id BIGSERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    username VARCHAR(100) NOT NULL UNIQUE,
    hashed_password TEXT NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    company VARCHAR(255),
    created_at TIMESTAMP NOT NULL
);

-- Create UserPreferences table
CREATE TABLE IF NOT EXISTS public."UserPreferences" (
    preference_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    column_preferences TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    CONSTRAINT fk_userpreferences_user
        FOREIGN KEY (user_id) REFERENCES public."User"(user_id)
        ON DELETE CASCADE
);

-- Create ForgotPasswordToken table
CREATE TABLE IF NOT EXISTS public."ForgotPasswordToken" (
    token_id BIGSERIAL PRIMARY KEY,
    token_hash TEXT NOT NULL,
    email VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    CONSTRAINT fk_forgotpasswordtoken_user
        FOREIGN KEY (email) REFERENCES public."User"(email)
        ON DELETE CASCADE
);

-- Create Asset table
CREATE TABLE IF NOT EXISTS public."Asset" (
    asset_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    asset_type VARCHAR(50) NOT NULL,
    initial_book_value NUMERIC(18,2) NOT NULL,
    manufacturer VARCHAR(255) NOT NULL,
    model VARCHAR(255) NOT NULL,
    model_year VARCHAR(4) NOT NULL,
    usage INTEGER NOT NULL,
    condition VARCHAR(50) NOT NULL,
    country VARCHAR(100) NOT NULL,
    state_us VARCHAR(50),
    deleted BOOLEAN NOT NULL DEFAULT FALSE,
    depreciation_method VARCHAR(50),
    salvage_value NUMERIC(18,2),
    useful_life INTEGER,
    depreciation_rate NUMERIC(18,2),
    total_expected_units_production INTEGER,
    units_produced_in_year INTEGER,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    CONSTRAINT fk_asset_user
        FOREIGN KEY (user_id) REFERENCES public."User"(user_id)
        ON DELETE CASCADE
);

-- Create AssetDepreciationSchedule table
CREATE TABLE IF NOT EXISTS public."AssetDepreciationSchedule" (
    asset_depreciation_schedule_id BIGSERIAL PRIMARY KEY,
    asset_id BIGINT NOT NULL,
    depreciation_date VARCHAR(10) NOT NULL,
    new_book_value NUMERIC(18,2) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    CONSTRAINT fk_assetdepreciationschedule_asset
        FOREIGN KEY (asset_id) REFERENCES public."Asset"(asset_id)
        ON DELETE CASCADE
);

-- Create LoanInformation table
CREATE TABLE IF NOT EXISTS public."LoanInformation" (
    loan_id BIGSERIAL PRIMARY KEY,
    asset_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    lender_name VARCHAR(255) NOT NULL,
    loan_amount NUMERIC(18,2) NOT NULL,
    interest_rate NUMERIC(5,2) NOT NULL,
    loan_term_years INTEGER NOT NULL,
    remaining_balance NUMERIC(18,2) NOT NULL,
    monthly_payment NUMERIC(18,2) NOT NULL,
    payment_frequency VARCHAR(50) NOT NULL,
    loan_status VARCHAR(50) NOT NULL,
    last_payment_date VARCHAR(10),
    last_payment_amount NUMERIC(18,2),
    next_payment_date VARCHAR(10),
    loan_start_date VARCHAR(10) NOT NULL,
    loan_end_date VARCHAR(10) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    CONSTRAINT fk_loaninformation_asset
        FOREIGN KEY (asset_id) REFERENCES public."Asset"(asset_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_loaninformation_user
        FOREIGN KEY (user_id) REFERENCES public."User"(user_id)
        ON DELETE CASCADE
);

-- Create LoanProjectedPayments table
CREATE TABLE IF NOT EXISTS public."LoanProjectedPayments" (
    loan_projected_payment_id BIGSERIAL PRIMARY KEY,
    loan_id BIGINT NOT NULL,
    loan_payment_date VARCHAR(10) NOT NULL,
    new_remaining_value NUMERIC(18,2) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    CONSTRAINT fk_loanprojectedpayments_loaninformation
        FOREIGN KEY (loan_id) REFERENCES public."LoanInformation"(loan_id)
        ON DELETE CASCADE
);

-- Create EquipmentValuationLog table
CREATE TABLE IF NOT EXISTS public."EquipmentValuationLog" (
    log_id BIGSERIAL PRIMARY KEY,
    asset_id BIGINT NOT NULL,
    valuation_date TIMESTAMP NOT NULL,
    unadjusted_fair_market_value NUMERIC(18,2),
    unadjusted_orderly_liquidation_value NUMERIC(18,2),
    unadjusted_forced_liquidation_value NUMERIC(18,2),
    adjusted_fair_market_value NUMERIC(18,2),
    adjusted_orderly_liquidation_value NUMERIC(18,2),
    adjusted_forced_liquidation_value NUMERIC(18,2),
    salvage NUMERIC(18,2),
    CONSTRAINT fk_equipmentvaluationlog_asset
        FOREIGN KEY (asset_id) REFERENCES public."Asset"(asset_id)
        ON DELETE CASCADE
);

-- Create VehicleValuationLog table
CREATE TABLE IF NOT EXISTS public."VehicleValuationLog" (
    log_id BIGSERIAL PRIMARY KEY,
    asset_id BIGINT NOT NULL,
    valuation_date TIMESTAMP NOT NULL,
    unadjusted_low NUMERIC(18,2),
    unadjusted_high NUMERIC(18,2),
    unadjusted_finance NUMERIC(18,2),
    unadjusted_retail NUMERIC(18,2),
    unadjusted_wholesale NUMERIC(18,2),
    unadjusted_trade_in NUMERIC(18,2),
    adjusted_low NUMERIC(18,2),
    adjusted_high NUMERIC(18,2),
    adjusted_finance NUMERIC(18,2),
    adjusted_retail NUMERIC(18,2),
    adjusted_wholesale NUMERIC(18,2),
    adjusted_trade_in NUMERIC(18,2),
    CONSTRAINT fk_vehiclevaluationlog_asset
        FOREIGN KEY (asset_id) REFERENCES public."Asset"(asset_id)
        ON DELETE CASCADE
);