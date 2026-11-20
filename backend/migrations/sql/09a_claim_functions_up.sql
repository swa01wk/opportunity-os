-- ADR-023: SECURITY DEFINER claim helpers for FORCE RLS tables (SPEC-09a).
-- Role oos_claim is created in the Alembic revision before this script runs.

GRANT SELECT, UPDATE ON app.workflow_request TO oos_claim;
GRANT SELECT, UPDATE ON app.outbox_event TO oos_claim;

CREATE POLICY claim_fn_select ON app.workflow_request
  FOR SELECT TO oos_claim
  USING (true);

CREATE POLICY claim_fn_update ON app.workflow_request
  FOR UPDATE TO oos_claim
  USING (true)
  WITH CHECK (true);

CREATE POLICY claim_fn_select ON app.outbox_event
  FOR SELECT TO oos_claim
  USING (true);

CREATE POLICY claim_fn_update ON app.outbox_event
  FOR UPDATE TO oos_claim
  USING (true)
  WITH CHECK (true);

CREATE OR REPLACE FUNCTION app.claim_workflow_requests(p_limit int)
RETURNS TABLE (id uuid, workspace_id uuid)
LANGUAGE sql
SECURITY DEFINER
SET search_path = pg_catalog, app
AS $func$
  SELECT wr.id, wr.workspace_id
  FROM app.workflow_request AS wr
  WHERE wr.dispatched_at IS NULL
  ORDER BY wr.created_at ASC
  FOR UPDATE OF wr SKIP LOCKED
  LIMIT GREATEST(p_limit, 0);
$func$;

CREATE OR REPLACE FUNCTION app.claim_outbox_events(p_limit int)
RETURNS TABLE (id uuid, workspace_id uuid)
LANGUAGE sql
SECURITY DEFINER
SET search_path = pg_catalog, app
AS $func$
  SELECT oe.id, oe.workspace_id
  FROM app.outbox_event AS oe
  WHERE oe.delivered_at IS NULL
  ORDER BY oe.seq ASC
  FOR UPDATE OF oe SKIP LOCKED
  LIMIT GREATEST(p_limit, 0);
$func$;

ALTER FUNCTION app.claim_workflow_requests(int) OWNER TO oos_claim;
ALTER FUNCTION app.claim_outbox_events(int) OWNER TO oos_claim;

REVOKE ALL ON FUNCTION app.claim_workflow_requests(int) FROM PUBLIC;
REVOKE ALL ON FUNCTION app.claim_outbox_events(int) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION app.claim_workflow_requests(int) TO oos_worker;
GRANT EXECUTE ON FUNCTION app.claim_outbox_events(int) TO oos_worker;