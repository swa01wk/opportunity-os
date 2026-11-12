-- OpportunityOS database schema DRAFT 0.2.0 (Stage 2a; 0.2.0 Stage 2b: project archive/deletion, KPI baselines, analytics schema).
-- Agreed shape for M0; the real schema is created by Alembic migrations (ADR-006).
-- Conventions:
--   * every domain table has workspace_id; row-level security keys on it (NFR-04)
--   * *_version tables are immutable (no UPDATE/DELETE grants for the app role)
--   * parent rows hold head pointers + row_version for If-Match (optimistic concurrency)
--   * sha256 columns hold canonical-JSON or file hashes; large files live in object storage (ADR-007)
--   * money is amount_minor bigint + currency char(3) (+ fx_rate where converted)
-- Schemas: app (domain), media (render jobs), analytics (KPI events, ADR-017), dbos (owned by DBOS Transact, ADR-003; not listed here).

CREATE SCHEMA IF NOT EXISTS app;
CREATE SCHEMA IF NOT EXISTS media;
CREATE SCHEMA IF NOT EXISTS analytics;

-- ---------- Workspace, members, brand, projects (F-01) ----------
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
  idp_subject text NOT NULL,              -- from the auth provider (ADR-012)
  display_name text NOT NULL,
  responsibilities text[] NOT NULL,       -- owner, editor, reviewer, publisher, analyst (R-05)
  specialist_scopes text[] NOT NULL DEFAULT '{}',  -- e.g. {'health'} for R-09 AC2
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (idp_issuer, idp_subject)
);

CREATE TABLE app.service_identity (       -- worker, render, agent tasks; never approve (R-43)
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
  tokens jsonb NOT NULL,                  -- palette, type scale, safe zones, caption placement, easing (R-23)
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
  state text NOT NULL DEFAULT 'DRAFT',    -- R-44 production state machine
  state_reason text,
  brand_kit_id uuid NOT NULL REFERENCES app.brand_kit(id),
  brand_kit_version int NOT NULL,         -- pinned (R-02)
  narrator jsonb NOT NULL,                -- provider, voice_id, settings; pinned per take (R-03)
  row_version int NOT NULL DEFAULT 1,
  archived_at timestamptz,                -- hidden from lists; nothing deleted (0.2.0)
  deletion_requested_at timestamptz,      -- set by DELETE; purge run removes the rest (NFR-10 AC2)
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE app.destination (            -- R-04
  id uuid PRIMARY KEY,
  workspace_id uuid NOT NULL,
  project_id uuid NOT NULL REFERENCES app.project(id),
  platform text NOT NULL CHECK (platform IN ('youtube','instagram')),
  account_label text NOT NULL,
  external_account_id text,               -- R3 connected; manual at R2
  timezone text NOT NULL DEFAULT 'Asia/Kolkata',
  export_profile text NOT NULL DEFAULT 'shorts_1080x1920_30',
  disclosure jsonb NOT NULL DEFAULT '{}', -- AI identity + platform disclosure assessment (R-60)
  is_reference_only boolean NOT NULL DEFAULT false,  -- R-04 AC3: cannot be a destination
  row_version int NOT NULL DEFAULT 1
);

-- ---------- Content Opportunity Contract (F-02) ----------
CREATE TABLE app.opportunity_contract (
  id uuid PRIMARY KEY,
  workspace_id uuid NOT NULL,
  project_id uuid NOT NULL REFERENCES app.project(id),
  head_version int NOT NULL,
  row_version int NOT NULL DEFAULT 1
);
CREATE TABLE app.opportunity_contract_version (
  contract_id uuid NOT NULL REFERENCES app.opportunity_contract(id),
  version int NOT NULL,
  workspace_id uuid NOT NULL,
  body jsonb NOT NULL,                    -- audience, question, promise, format, evidence plan, families, budget, hypothesis, measurement plan (R-06)
  sha256 char(64) NOT NULL,
  created_by uuid NOT NULL REFERENCES app.member(id),
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (contract_id, version)
);

-- ---------- Sources, claims, evidence (F-03) ----------
CREATE TABLE app.source (
  id uuid PRIMARY KEY,
  workspace_id uuid NOT NULL,
  url text NOT NULL,
  final_url text NOT NULL,
  title text, publisher text, published_at text,
  retrieved_at timestamptz NOT NULL,
  content_type text NOT NULL,
  content_sha256 char(64) NOT NULL       -- text itself is not kept (A-25)
);

CREATE TABLE app.claim (
  id uuid PRIMARY KEY,
  workspace_id uuid NOT NULL,
  project_id uuid NOT NULL REFERENCES app.project(id),
  text text NOT NULL,
  claim_type text NOT NULL,
  materiality text NOT NULL CHECK (materiality IN ('material','supporting')),
  review_status text NOT NULL DEFAULT 'unreviewed'
    CHECK (review_status IN ('unreviewed','approved','qualified','unsupported','contradicted','needs_specialist','removed')),
  specialist_scope text,                  -- set when needs_specialist (R-09 AC2)
  qualification text,
  reviewed_by uuid REFERENCES app.member(id),
  reviewed_at timestamptz,
  row_version int NOT NULL DEFAULT 1
);

CREATE TABLE app.evidence_record (
  id uuid PRIMARY KEY,
  workspace_id uuid NOT NULL,
  claim_id uuid NOT NULL REFERENCES app.claim(id),
  source_id uuid NOT NULL REFERENCES app.source(id),
  stance text NOT NULL CHECK (stance IN ('supports','partially_supports','contradicts')),
  locator text NOT NULL,
  excerpt text CHECK (excerpt IS NULL OR array_length(regexp_split_to_array(trim(excerpt), '\s+'), 1) < 25),
  citation_valid boolean NOT NULL,        -- R-08 AC2: locates the supporting text
  created_by_attempt uuid                 -- task_attempt that proposed it
);

-- ---------- Demonstrations, scripts, storyboards (F-04, F-05) ----------
CREATE TABLE app.demonstration_version (
  id uuid NOT NULL,
  version int NOT NULL,
  workspace_id uuid NOT NULL,
  project_id uuid NOT NULL REFERENCES app.project(id),
  body jsonb NOT NULL,                    -- media/demonstration.schema.json
  sha256 char(64) NOT NULL,
  review_status text NOT NULL DEFAULT 'unreviewed',
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (id, version)
);

CREATE TABLE app.script (
  id uuid PRIMARY KEY, workspace_id uuid NOT NULL,
  project_id uuid NOT NULL REFERENCES app.project(id),
  head_version int, row_version int NOT NULL DEFAULT 1
);
CREATE TABLE app.script_version (
  script_id uuid NOT NULL REFERENCES app.script(id),
  version int NOT NULL,
  workspace_id uuid NOT NULL,
  body jsonb NOT NULL,                    -- agent-tools task-io ScriptOutput shape
  sha256 char(64) NOT NULL,
  origin text NOT NULL CHECK (origin IN ('agent_task','member_edit')),
  origin_attempt uuid, created_by uuid,
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (script_id, version)
);
CREATE TABLE app.script_claim_ref (       -- R-10 traceability, queryable
  script_id uuid NOT NULL, script_version int NOT NULL,
  segment_id text NOT NULL, claim_id uuid NOT NULL REFERENCES app.claim(id),
  PRIMARY KEY (script_id, script_version, segment_id, claim_id)
);

CREATE TABLE app.storyboard (
  id uuid PRIMARY KEY, workspace_id uuid NOT NULL,
  project_id uuid NOT NULL REFERENCES app.project(id),
  head_version int, row_version int NOT NULL DEFAULT 1
);
CREATE TABLE app.storyboard_version (     -- holds the VideoSpec
  storyboard_id uuid NOT NULL REFERENCES app.storyboard(id),
  version int NOT NULL,
  workspace_id uuid NOT NULL,
  script_id uuid NOT NULL, script_version int NOT NULL,
  video_spec jsonb NOT NULL,              -- media/video-spec.schema.json
  sha256 char(64) NOT NULL,
  timing_status text NOT NULL CHECK (timing_status IN ('provisional','measured')),
  validation jsonb NOT NULL DEFAULT '[]', -- last ValidationError[]
  origin text NOT NULL, origin_attempt uuid, created_by uuid,
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (storyboard_id, version)
);
CREATE TABLE app.scene_version (          -- one row per scene per storyboard version, for diff/reuse
  storyboard_id uuid NOT NULL, storyboard_version int NOT NULL,
  scene_id text NOT NULL,
  workspace_id uuid NOT NULL,
  input_sha256 char(64) NOT NULL,         -- effective input hash (R-32)
  entry_state_sha256 char(64) NOT NULL,
  exit_state_sha256 char(64) NOT NULL,
  PRIMARY KEY (storyboard_id, storyboard_version, scene_id)
);

-- ---------- Narration, timing, renders (F-07, F-08) ----------
CREATE TABLE app.narration_take (
  id uuid PRIMARY KEY, workspace_id uuid NOT NULL,
  project_id uuid NOT NULL REFERENCES app.project(id),
  script_id uuid NOT NULL, script_version int NOT NULL,
  scene_scope text[],                     -- null = whole script
  timing jsonb NOT NULL,                  -- media/timing.schema.json NarrationTiming
  audio_key text NOT NULL, audio_sha256 char(64) NOT NULL,
  sha256 char(64) NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE app.pronunciation (
  id uuid PRIMARY KEY, workspace_id uuid NOT NULL,
  term text NOT NULL, say text NOT NULL, UNIQUE (workspace_id, term)
);

CREATE TABLE app.render (
  id uuid PRIMARY KEY, workspace_id uuid NOT NULL,
  project_id uuid NOT NULL REFERENCES app.project(id),
  kind text NOT NULL CHECK (kind IN ('preview','master')),
  storyboard_id uuid NOT NULL, storyboard_version int NOT NULL,
  narration_take_id uuid,
  manifest jsonb,                         -- media/render-manifest.schema.json, immutable once set
  manifest_sha256 char(64),
  output_key text, output_sha256 char(64),
  status text NOT NULL,                   -- requested, running, succeeded, failed, cancelled
  created_at timestamptz NOT NULL DEFAULT now()
);

-- ---------- Revisions (F-09) ----------
CREATE TABLE app.revision (
  id uuid PRIMARY KEY, workspace_id uuid NOT NULL,
  project_id uuid NOT NULL REFERENCES app.project(id),
  request text NOT NULL,                  -- operator instruction
  target jsonb NOT NULL,                  -- claim / scene / object refs
  impact jsonb NOT NULL,                  -- rebuild, reuse, cost estimate, timing shifts, reopened gates (R-31)
  status text NOT NULL CHECK (status IN ('previewed','applied','discarded')),
  created_by uuid NOT NULL REFERENCES app.member(id),
  created_at timestamptz NOT NULL DEFAULT now()
);

-- ---------- Review, approvals (F-11, F-12) ----------
CREATE TABLE app.finding (
  id uuid PRIMARY KEY, workspace_id uuid NOT NULL,
  project_id uuid NOT NULL REFERENCES app.project(id),
  target jsonb NOT NULL,                  -- claim, scene, object or asset (R-37)
  severity text NOT NULL CHECK (severity IN ('material_factual','rights_blocker','quality','minor')),
  text text NOT NULL,
  disposition text NOT NULL DEFAULT 'open' CHECK (disposition IN ('open','fixed','accepted','wont_fix')),
  raised_by jsonb NOT NULL, resolved_by uuid, row_version int NOT NULL DEFAULT 1
);
CREATE TABLE app.rubric_score (
  id uuid PRIMARY KEY, workspace_id uuid NOT NULL,
  render_id uuid NOT NULL REFERENCES app.render(id),  -- must be a final master (R-38)
  scores jsonb NOT NULL,                  -- correctness, clarity, originality, readability_muted, promise_payoff
  muted_review_passed boolean NOT NULL,   -- KPI-14
  scored_by uuid NOT NULL REFERENCES app.member(id),
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE app.approval (               -- R-40, R-41; insert-only
  id uuid PRIMARY KEY, workspace_id uuid NOT NULL,
  project_id uuid NOT NULL REFERENCES app.project(id),
  gate text NOT NULL CHECK (gate IN ('A_brief','B_explanation_script','C_storyboard','D_final_package','E_public_release')),
  decision text NOT NULL CHECK (decision IN ('approved','returned')),
  target_type text NOT NULL,
  target_id uuid NOT NULL, target_version int NOT NULL, target_sha256 char(64) NOT NULL,
  scope text NOT NULL,
  destination_id uuid REFERENCES app.destination(id),
  actor_member_id uuid NOT NULL REFERENCES app.member(id),   -- members only (R-43)
  responsibility text NOT NULL,
  evidence jsonb NOT NULL,                -- what was shown at the gate
  invalidated_at timestamptz, invalidated_reason text,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX approval_current ON app.approval (project_id, gate) WHERE invalidated_at IS NULL;

-- ---------- Packages, export, publication (F-13) ----------
CREATE TABLE app.package_version (
  id uuid NOT NULL, version int NOT NULL, workspace_id uuid NOT NULL,
  project_id uuid NOT NULL REFERENCES app.project(id),
  master_render_id uuid NOT NULL REFERENCES app.render(id),
  metadata jsonb NOT NULL,                -- title, description with attribution, tags, audience/made-for-kids (R-04 AC2), disclosure
  cover_key text, captions_key text,
  sha256 char(64) NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (id, version)
);
CREATE TABLE app.export_bundle (
  id uuid PRIMARY KEY, workspace_id uuid NOT NULL,
  package_id uuid NOT NULL, package_version int NOT NULL,
  bundle_key text NOT NULL, bundle_sha256 char(64) NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE app.publication (            -- per package, platform and account (R-48)
  id uuid PRIMARY KEY, workspace_id uuid NOT NULL,
  package_id uuid NOT NULL, package_version int NOT NULL,
  destination_id uuid NOT NULL REFERENCES app.destination(id),
  route text NOT NULL CHECK (route IN ('manual','connected')),
  state text NOT NULL,
  external_id text, url text, published_at timestamptz,
  observed_visibility text,
  provider_processing_status text, provider_checked_at timestamptz,
  verification text NOT NULL DEFAULT 'NOT_CHECKED' CHECK (verification IN ('NOT_CHECKED','PASSED','PARTIAL','FAILED')),
  verification_evidence jsonb,
  package_mismatch boolean NOT NULL DEFAULT false,
  row_version int NOT NULL DEFAULT 1
);
CREATE TABLE app.correction (             -- R-49
  id uuid PRIMARY KEY, workspace_id uuid NOT NULL,
  publication_id uuid NOT NULL REFERENCES app.publication(id),
  problem text NOT NULL, proposed_plan jsonb NOT NULL,
  status text NOT NULL DEFAULT 'proposed'
);
CREATE TABLE app.performance_snapshot (   -- manual at R2 (KPI-06), imported at R3 (R-72)
  id uuid PRIMARY KEY, workspace_id uuid NOT NULL,
  publication_id uuid NOT NULL REFERENCES app.publication(id),
  measure text NOT NULL, platform_definition text NOT NULL,
  value numeric, availability text NOT NULL CHECK (availability IN ('available','missing','delayed','unsupported','permission_denied')),
  window_start timestamptz NOT NULL, window_end timestamptz NOT NULL,
  denominator text, source text NOT NULL CHECK (source IN ('manual','api')),
  api_version text, recorded_at timestamptz NOT NULL DEFAULT now()
);

-- ---------- Runs, attempts, cost, effort (F-10, F-14) ----------
CREATE TABLE app.workflow_request (       -- outbox for workflow starts (ADR-003)
  id uuid PRIMARY KEY, workspace_id uuid NOT NULL,
  project_id uuid NOT NULL, body jsonb NOT NULL,   -- events/workflow-request.schema.json
  dispatched_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE app.execution_run (          -- projection of a DBOS workflow
  id uuid PRIMARY KEY,                    -- = workflow_request.id = DBOS workflow id
  workspace_id uuid NOT NULL, project_id uuid NOT NULL,
  workflow_type text NOT NULL,
  state text NOT NULL,                    -- pending, running, waiting_approval, paused_budget, succeeded, failed, cancelled
  cancel_requested_at timestamptz,
  code_repair_needed boolean NOT NULL DEFAULT false,   -- KPI-02
  created_at timestamptz NOT NULL DEFAULT now(), finished_at timestamptz
);
CREATE TABLE app.task_attempt (
  id uuid PRIMARY KEY, workspace_id uuid NOT NULL,
  run_id uuid NOT NULL REFERENCES app.execution_run(id),
  task_key text NOT NULL, task_type text NOT NULL, attempt int NOT NULL,
  status text NOT NULL,
  error_class text, error jsonb,
  provider text, model_or_voice text, prompt_sha256 char(64), tool_versions jsonb,
  input_sha256 char(64), output_ref jsonb,
  estimated_cost_minor bigint, actual_cost_minor bigint, currency char(3), fx_rate numeric,
  taken_over_by uuid REFERENCES app.member(id),        -- R-51 AC2
  started_at timestamptz NOT NULL, finished_at timestamptz,
  UNIQUE (run_id, task_key, attempt)
);
CREATE TABLE app.budget (                 -- per project allowance; limits are configuration (Q-05)
  project_id uuid PRIMARY KEY REFERENCES app.project(id),
  workspace_id uuid NOT NULL,
  allowance_minor bigint,                 -- NULL = not set: paid dispatch blocked (dev seeds a default, Q-05)
  currency char(3) NOT NULL DEFAULT 'INR',
  reserved_minor bigint NOT NULL DEFAULT 0,
  spent_minor bigint NOT NULL DEFAULT 0,
  row_version int NOT NULL DEFAULT 1,
  CHECK (allowance_minor IS NULL OR reserved_minor + spent_minor <= allowance_minor)
);
CREATE TABLE app.budget_reservation (
  id uuid PRIMARY KEY, workspace_id uuid NOT NULL,
  project_id uuid NOT NULL REFERENCES app.budget(project_id),
  attempt_id uuid NOT NULL UNIQUE,        -- one reservation per attempt (idempotent)
  amount_minor bigint NOT NULL,
  status text NOT NULL CHECK (status IN ('held','settled','released')),
  settled_minor bigint
);
CREATE TABLE app.effort_entry (           -- R-36, KPI-04
  id uuid PRIMARY KEY, workspace_id uuid NOT NULL,
  project_id uuid NOT NULL REFERENCES app.project(id),
  member_id uuid NOT NULL REFERENCES app.member(id),
  activity text NOT NULL, active_minutes int NOT NULL CHECK (active_minutes >= 0),
  is_code_repair boolean NOT NULL DEFAULT false,
  recorded_at timestamptz NOT NULL DEFAULT now()
);

-- ---------- Assets and rights (F-15) ----------
CREATE TABLE app.kpi_baseline (           -- KPI-04 manual baseline (Q-13); insert-only
  id uuid PRIMARY KEY,
  workspace_id uuid NOT NULL REFERENCES app.workspace(id),
  kpi text NOT NULL CHECK (kpi IN ('KPI-04')),
  measured_on date NOT NULL,
  method text NOT NULL,
  active_minutes int NOT NULL CHECK (active_minutes > 0),
  revisions int,
  cost_minor bigint, cost_currency char(3),
  recorded_by uuid NOT NULL REFERENCES app.member(id),
  recorded_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE app.asset (
  id uuid PRIMARY KEY, workspace_id uuid NOT NULL,
  kind text NOT NULL CHECK (kind IN ('font','sound_effect','image','voice','other')),
  name text NOT NULL, object_key text NOT NULL, sha256 char(64) NOT NULL,
  origin text NOT NULL, licence text NOT NULL, licence_evidence_key text,
  expires_at timestamptz, version int NOT NULL DEFAULT 1,
  lifecycle text NOT NULL DEFAULT 'active' CHECK (lifecycle IN ('active','expired','withdrawn'))
);

-- ---------- Events and audit (ADR-010) ----------
CREATE TABLE app.outbox_event (
  id uuid PRIMARY KEY, workspace_id uuid NOT NULL,
  type text NOT NULL, body jsonb NOT NULL,             -- events/domain-event.schema.json
  created_at timestamptz NOT NULL DEFAULT now(), delivered_at timestamptz
);
CREATE INDEX outbox_undelivered ON app.outbox_event (created_at) WHERE delivered_at IS NULL;
CREATE TABLE app.audit_log (
  id bigserial PRIMARY KEY, workspace_id uuid NOT NULL,
  actor jsonb NOT NULL, action text NOT NULL, subject jsonb NOT NULL,
  request_id uuid, trace_id text, at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE app.idempotency_key (
  key text NOT NULL, workspace_id uuid NOT NULL, request_sha256 char(64) NOT NULL,
  response jsonb NOT NULL, created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (workspace_id, key)
);

-- ---------- Render jobs (media schema, owned by the render service) ----------
CREATE TABLE media.render_job (
  job_id char(64) PRIMARY KEY,            -- effective input hash = idempotency key
  workspace_id uuid NOT NULL,
  request jsonb NOT NULL,                 -- media/render-job.schema.json RenderJobRequest
  state text NOT NULL CHECK (state IN ('queued','running','succeeded','failed','cancelled')),
  status jsonb NOT NULL,                  -- RenderJobStatus
  leased_until timestamptz,               -- crashed renders become claimable again
  attempts int NOT NULL DEFAULT 0,
  updated_at timestamptz NOT NULL DEFAULT now()
);

-- ---------- KPI analytics events (ADR-017); written only by the outbox relay ----------
CREATE TABLE analytics.event (
  id bigserial PRIMARY KEY,
  source_event_id uuid NOT NULL UNIQUE,   -- outbox event id; makes relay delivery idempotent
  event_name text NOT NULL,               -- analytics/events.schema.json
  event_version int NOT NULL,
  occurred_at timestamptz NOT NULL,
  workspace_id uuid NOT NULL,
  project_id uuid,
  member_id uuid,                         -- actor UUID only; no names or emails
  properties jsonb NOT NULL
);
CREATE INDEX analytics_event_name_time ON analytics.event (event_name, occurred_at);
-- Grafana reads KPI views through a read-only role (analytics_ro), created by the M0 migration.

-- R3 tables (connection, oauth_credential, experiment, learning_record, opportunity_rating)
-- are added by the spec that starts R3 (A-18); not part of this draft.
