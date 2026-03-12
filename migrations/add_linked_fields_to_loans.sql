-- Migration: Add linked_type and linked_id to Loans table
-- This allows loans to be linked to either Assets or Purchases

-- Step 1: Add new columns
ALTER TABLE "Loans" 
ADD COLUMN linked_type VARCHAR(20),
ADD COLUMN linked_id INTEGER;

-- Step 2: Migrate existing data from asset_id to the new columns
UPDATE "Loans"
SET linked_type = 'asset',
    linked_id = asset_id
WHERE asset_id IS NOT NULL;

-- Step 3: Drop the old asset_id column and its foreign key constraint
ALTER TABLE "Loans" DROP COLUMN asset_id;

-- Note: The new structure allows:
-- - linked_type = 'asset' with linked_id = AssetId from Assets table
-- - linked_type = 'purchase' with linked_id = purchase_id from Purchases table
-- - linked_type = NULL and linked_id = NULL for no link
