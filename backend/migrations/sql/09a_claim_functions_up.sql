-- ADR-023: SECURITY DEFINER claim helpers for FORCE RLS tables (SPEC-09a).

CREATE OR REPLACE FUNCTION app.claim_workflow_requests(p_limit int)
RETURNS TABLE (id uuid, workspace_id uuid)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, app
AS $func$
BEGIN
  SET LOCAL row_security = off;
  RETURN QUERY
  SELECT wr.id, wr.workspace_id
  FROM app.workflow_request AS wr
  WHERE wr.dispatched_at IS NULL
  ORDER BY wr.created_at ASC
  FOR UPDATE OF wr SKIP LOCKED
  LIMIT GREATEST(p_limit, 0);
END;
$func$;

CREATE OR REPLACE FUNCTION app.claim_outbox_events(p_limit int)
RETURNS TABLE (id uuid, workspace_id uuid)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, app
AS $func$
BEGIN
  SET LOCAL row_security = off;
  RETURN QUERY
  SELECT oe.id, oe.workspace_id
  FROM app.outbox_event AS oe
  WHERE oe.delivered_at IS NULL
  ORDER BY oe.seq ASC
  FOR UPDATE OF oe SKIP LOCKED
  LIMIT GREATEST(p_limit, 0);
END;
$func$;

ALTER FUNCTION app.claim_workflow_requests(int) OWNER TO oos_migrator;
ALTER FUNCTION app.claim_outbox_events(int) OWNER TO oos_migrator;

REVOKE ALL ON FUNCTION app.claim_workflow_requests(int) FROM PUBLIC;
REVOKE ALL ON FUNCTION app.claim_outbox_events(int) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION app.claim_workflow_requests(int) TO oos_worker;
GRANT EXECUTE ON FUNCTION app.claim_outbox_events(int) TO oos_worker;