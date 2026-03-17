-- Fix pattern for MySQL view update issues
-- Problem: UPDATE shipment_details_view ... can fail depending on view definition/updatability.
-- Solution: write to the base table (`shipments`) and optionally append to `shipment_history`.

-- 1) Safe read from the view
SELECT *
FROM shipment_details_view
LIMIT 100;

-- 2) Safe update via base table (instead of the view)
UPDATE shipments
SET status = 'Delivered'
WHERE shipment_id = 3;

-- 3) Optional audit/history trail
INSERT INTO shipment_history (shipment_id, status, changed_at)
VALUES (3, 'Delivered', UTC_TIMESTAMP());

-- 4) Verify
SELECT shipment_id, status
FROM shipments
WHERE shipment_id = 3;

SELECT *
FROM shipment_details_view
WHERE shipment_id = 3;
