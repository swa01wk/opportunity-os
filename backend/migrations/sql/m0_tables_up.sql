CREATE SCHEMA app;
CREATE SCHEMA media;
CREATE SCHEMA analytics;
CREATE SCHEMA dbos;

CREATE TABLE app.workspace (
  id uuid PRIMARY KEY,
  name text NOT NULL,
  reporting_currency char(3) NOT NULL DEFAULT 'INR',
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE app.member (
  id uuid PRIMARY KEY,
  workspace_id uuid NOT NULL REFERENCES app.workspace(id),
  idp_issuer text NOT NULL,
  idp_subject text NOT NULL,
  display_name text NOT NULL,
  responsibilities text[] NOT NULL,
  specialist_scopes text[] NOT NULL DEFAULT '{}',
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (idp_issuer, idp_subject)
);

CREATE TABLE app.service_identity (
  id text PRIMARY KEY,
  kind text NOT NULL CHECK (kind IN ('service','agent_task'))
);

CREATE TABLE app.brand_kit (
  id uuid PRIMARY KEY,
  workspace_id uuid NOT NULL REFERENCES app.workspace(id),
  name text NOT NULL,
  head_version int NOT NULL,
  row_version int NOT NULL DEFAULT 1
);

CREATE TABLE app.brand_kit_version (
  brand_kit_id uuid NOT NULL REFERENCES app.brand_kit(id),
  version int NOT NULL,
  workspace_id uuid NOT NULL,
  tokens jsonb NOT NULL,
  sha256 char(64) NOT NULL,
  created_by uuid NOT NULL REFERENCES app.member(id),
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (brand_kit_id, version)
);

CREATE TABLE app.project (
  id uuid PRIMARY KEY,
  workspace_id uuid NOT NULL REFERENCES app.workspace(id),
  title text NOT NULL,
  series text NOT NULL CHECK (series IN ('what_if','wait_how_does_that_work','solve_this','inside_the_machine')),
  state text NOT NULL DEFAULT 'DRAFT',
  state_reason text,
  brand_kit_id uuid NOT NULL REFERENCES app.brand_kit(id),
  brand_kit_version int NOT NULL,
  narrator jsonb NOT NULL,
  row_version int NOT NULL DEFAULT 1,
  archived_at timestamptz,
  deletion_requested_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE app.workflow_request (
  id uuid PRIMARY KEY,
  workspace_id uuid NOT NULL,
  project_id uuid NOT NULL,
  body jsonb NOT NULL,
  dispatched_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE app.execution_run (
  id uuid PRIMARY KEY,
  workspace_id uuid NOT NULL,
  project_id uuid NOT NULL,
  workflow_type text NOT NULL,
  state text NOT NULL,
  cancel_requested_at timestamptz,
  code_repair_needed boolean NOT NULL DEFAULT false,
  created_at timestamptz NOT NULL DEFAULT now(),
  finished_at timestamptz
);

CREATE TABLE app.task_attempt (
  id uuid PRIMARY KEY,
  workspace_id uuid NOT NULL,
  run_id uuid NOT NULL REFERENCES app.execution_run(id),
  task_key text NOT NULL,
  task_type text NOT NULL,
  attempt int NOT NULL,
  status text NOT NULL,
  error_class text,
  error jsonb,
  provider text,
  model_or_voice text,
  prompt_sha256 char(64),
  tool_versions jsonb,
  input_sha256 char(64),
  output_ref jsonb,
  input_bindings jsonb,
  validation jsonb,
  estimated_cost_minor bigint,
  actual_cost_minor bigint,
  currency char(3),
  fx_rate numeric,
  taken_over_by uuid REFERENCES app.member(id),
  started_at timestamptz NOT NULL,
  finished_at timestamptz,
  UNIQUE (run_id, task_key, attempt)
);

CREATE TABLE app.outbox_event (
  id uuid PRIMARY KEY,
  workspace_id uuid NOT NULL,
  seq bigserial NOT NULL UNIQUE,
  type text NOT NULL,
  body jsonb NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  delivered_at timestamptz
);

CREATE INDEX outbox_undelivered ON app.outbox_event (created_at) WHERE delivered_at IS NULL;

CREATE TABLE app.audit_log (
  id bigserial PRIMARY KEY,
  workspace_id uuid NOT NULL,
  actor jsonb NOT NULL,
  action text NOT NULL,
  subject jsonb NOT NULL,
  request_id uuid,
  trace_id text,
  at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE app.idempotency_key (
  key text NOT NULL,
  workspace_id uuid NOT NULL,
  request_sha256 char(64) NOT NULL,
  response jsonb NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (workspace_id, key)
);

CREATE TABLE media.render_job (
  job_id char(64) PRIMARY KEY,
  workspace_id uuid NOT NULL,
  request jsonb NOT NULL,
  state text NOT NULL CHECK (state IN ('queued','running','succeeded','failed','cancelled')),
  status jsonb NOT NULL,
  leased_until timestamptz,
  attempts int NOT NULL DEFAULT 0,
  updated_at timestamptz NOT NULL DEFAULT now()
);