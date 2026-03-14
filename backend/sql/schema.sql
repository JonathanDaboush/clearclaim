-- ClearClaim database schema
-- Applied to both clear_case (production) and clear_case_test (testing).
-- Every statement is idempotent (CREATE TABLE IF NOT EXISTS).

CREATE TABLE IF NOT EXISTS users (
    id                    TEXT PRIMARY KEY,
    email                 TEXT NOT NULL UNIQUE,
    password_hash         TEXT NOT NULL,
    authenticator_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    role_id               TEXT,
    verification_status   TEXT NOT NULL DEFAULT 'unverified',
    totp_secret           TEXT NOT NULL DEFAULT '',
    created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at            TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS password_reset_tokens (
    token      TEXT PRIMARY KEY,
    user_id    TEXT NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() + INTERVAL '2 hours'),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS devices (
    id          TEXT PRIMARY KEY,
    user_id     TEXT NOT NULL,
    device_info TEXT NOT NULL DEFAULT '',
    location    TEXT NOT NULL DEFAULT '',
    trusted     BOOLEAN NOT NULL DEFAULT FALSE,
    added_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    revoked     BOOLEAN NOT NULL DEFAULT FALSE,
    revoked_at  TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS projects (
    id            TEXT PRIMARY KEY,
    name          TEXT NOT NULL,
    main_party_id TEXT NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at    TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS subgroups (
    id         TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    name       TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS memberships (
    id           TEXT PRIMARY KEY,
    user_id      TEXT NOT NULL,
    project_id   TEXT NOT NULL,
    subgroup_id  TEXT NOT NULL DEFAULT '',
    role_id      TEXT NOT NULL DEFAULT '',
    soft_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    joined_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    left_at      TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS contracts (
    id              TEXT PRIMARY KEY,
    project_id      TEXT NOT NULL,
    name            TEXT NOT NULL DEFAULT 'Untitled Contract',
    created_by      TEXT NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    current_version TEXT,
    status          TEXT NOT NULL DEFAULT 'draft'
);

CREATE TABLE IF NOT EXISTS contract_versions (
    id             TEXT PRIMARY KEY,
    contract_id    TEXT NOT NULL,
    content        TEXT NOT NULL DEFAULT '',
    created_by     TEXT NOT NULL DEFAULT '',
    version_number INTEGER NOT NULL DEFAULT 1,
    content_hash   TEXT NOT NULL DEFAULT '',
    signed         BOOLEAN NOT NULL DEFAULT FALSE,
    rejected       BOOLEAN NOT NULL DEFAULT FALSE,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS contract_version_approvals (
    id                  TEXT PRIMARY KEY,
    contract_version_id TEXT NOT NULL,
    user_id             TEXT NOT NULL,
    approved_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (contract_version_id, user_id)
);

CREATE TABLE IF NOT EXISTS contract_revision_approvals (
    id                  TEXT PRIMARY KEY,
    contract_version_id TEXT NOT NULL,
    user_id             TEXT NOT NULL,
    approved_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- signed_at stored as TEXT to preserve the exact ISO string used in signature hashes
CREATE TABLE IF NOT EXISTS signatures (
    id                  TEXT PRIMARY KEY,
    contract_version_id TEXT NOT NULL,
    user_id             TEXT NOT NULL,
    device_id           TEXT NOT NULL DEFAULT '',
    signed_at           TEXT NOT NULL DEFAULT '',
    signature_hash      TEXT NOT NULL DEFAULT '',
    image_url           TEXT,
    ip                  TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS evidence (
    id          TEXT PRIMARY KEY,
    contract_id TEXT NOT NULL,
    added_by    TEXT NOT NULL,
    file_url    TEXT NOT NULL DEFAULT '',
    file_type   TEXT,
    file_size   BIGINT,
    hash_value  TEXT,
    metadata    TEXT,
    status      TEXT NOT NULL DEFAULT 'pending',
    added_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at  TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS evidence_approvals (
    id          TEXT PRIMARY KEY,
    evidence_id TEXT NOT NULL,
    user_id     TEXT NOT NULL,
    action      TEXT NOT NULL,
    actioned_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS evidence_contracts (
    id          TEXT PRIMARY KEY,
    evidence_id TEXT NOT NULL,
    contract_id TEXT NOT NULL,
    UNIQUE (evidence_id, contract_id)
);

-- timestamp stored as TEXT to preserve the exact ISO string used when computing each entry's hash
CREATE TABLE IF NOT EXISTS audit_logs (
    id                  TEXT PRIMARY KEY,
    user_id             TEXT NOT NULL,
    device_id           TEXT NOT NULL DEFAULT '',
    event_type          TEXT NOT NULL,
    related_object_id   TEXT NOT NULL DEFAULT '',
    contract_id         TEXT NOT NULL DEFAULT '',
    contract_version_id TEXT NOT NULL DEFAULT '',
    details             TEXT NOT NULL DEFAULT '',
    timestamp           TEXT NOT NULL DEFAULT '',
    prev_hash           TEXT NOT NULL DEFAULT '',
    hash                TEXT NOT NULL DEFAULT '',
    snapshot_hash       TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS notifications (
    id                  TEXT PRIMARY KEY,
    user_id             TEXT NOT NULL,
    event_type          TEXT NOT NULL,
    content             TEXT NOT NULL DEFAULT '',
    related_object_id   TEXT NOT NULL DEFAULT '',
    related_object_type TEXT NOT NULL DEFAULT '',
    sent_at             TEXT NOT NULL DEFAULT '',
    read_at             TEXT
);

CREATE TABLE IF NOT EXISTS subscriptions (
    id         TEXT PRIMARY KEY,
    user_id    TEXT NOT NULL,
    tier       TEXT NOT NULL DEFAULT '',
    start_date TEXT NOT NULL DEFAULT '',
    end_date   TEXT NOT NULL DEFAULT '',
    status     TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS payments (
    id      TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    amount  NUMERIC(12,2) NOT NULL DEFAULT 0,
    method  TEXT NOT NULL DEFAULT '',
    status  TEXT NOT NULL DEFAULT 'completed',
    metrics TEXT,
    paid_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS roles (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL UNIQUE,
    permissions TEXT NOT NULL DEFAULT '[]',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS revision_changes (
    id                  TEXT PRIMARY KEY,
    contract_version_id TEXT NOT NULL,
    diff                TEXT NOT NULL DEFAULT '{}',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS keys (
    id         TEXT PRIMARY KEY,
    type       TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    parent_id  TEXT,
    status     TEXT NOT NULL DEFAULT 'active',
    rotated_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS identity_verifications (
    id        TEXT PRIMARY KEY,
    user_id   TEXT NOT NULL UNIQUE,
    provider  TEXT NOT NULL DEFAULT '',
    status    TEXT NOT NULL DEFAULT 'unverified',
    timestamp TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS user_restrictions (
    id         TEXT PRIMARY KEY,
    user_id    TEXT NOT NULL UNIQUE,
    reason     TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ─────────────────────────────────────────────────────────────────────────────
-- Idempotency keys (issues signing, payment and other mutating endpoints)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS idempotency_keys (
    id         TEXT PRIMARY KEY,
    endpoint   TEXT NOT NULL DEFAULT '',
    user_id    TEXT NOT NULL DEFAULT '',
    response   TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() + INTERVAL '24 hours')
);

-- ─────────────────────────────────────────────────────────────────────────────
-- Audit-log immutability
-- PostgreSQL rule: any UPDATE or DELETE on audit_logs is silently dropped,
-- preserving the append-only guarantee required for legal admissibility.
-- ─────────────────────────────────────────────────────────────────────────────
DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_rules
        WHERE tablename = 'audit_logs' AND rulename = 'audit_logs_no_update'
    ) THEN
        EXECUTE 'CREATE RULE audit_logs_no_update AS ON UPDATE TO audit_logs DO INSTEAD NOTHING';
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_rules
        WHERE tablename = 'audit_logs' AND rulename = 'audit_logs_no_delete'
    ) THEN
        EXECUTE 'CREATE RULE audit_logs_no_delete AS ON DELETE TO audit_logs DO INSTEAD NOTHING';
    END IF;
END $$;

-- ─────────────────────────────────────────────────────────────────────────────
-- Device trust model — extended columns
-- ─────────────────────────────────────────────────────────────────────────────
ALTER TABLE devices ADD COLUMN IF NOT EXISTS device_fingerprint TEXT NOT NULL DEFAULT '';
ALTER TABLE devices ADD COLUMN IF NOT EXISTS last_seen          TIMESTAMPTZ;
ALTER TABLE devices ADD COLUMN IF NOT EXISTS risk_score         INTEGER NOT NULL DEFAULT 0;

-- ─────────────────────────────────────────────────────────────────────────────
-- Evidence integrity — timestamp proof and uploader binding hash
-- ─────────────────────────────────────────────────────────────────────────────
ALTER TABLE evidence ADD COLUMN IF NOT EXISTS timestamp_proof TEXT NOT NULL DEFAULT '';
ALTER TABLE evidence ADD COLUMN IF NOT EXISTS uploader_hash   TEXT NOT NULL DEFAULT '';

-- ─────────────────────────────────────────────────────────────────────────────
-- Notification delivery tracking — retry_count, status, last attempt
-- ─────────────────────────────────────────────────────────────────────────────
ALTER TABLE notifications ADD COLUMN IF NOT EXISTS delivery_status  TEXT NOT NULL DEFAULT 'pending';
ALTER TABLE notifications ADD COLUMN IF NOT EXISTS retry_count      INTEGER NOT NULL DEFAULT 0;
ALTER TABLE notifications ADD COLUMN IF NOT EXISTS last_attempt_at  TIMESTAMPTZ;

-- ─────────────────────────────────────────────────────────────────────────────
-- Background task queue (persistent job store)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS task_queue (
    id           TEXT PRIMARY KEY,
    task_type    TEXT NOT NULL DEFAULT '',
    payload      TEXT NOT NULL DEFAULT '{}',
    status       TEXT NOT NULL DEFAULT 'pending',  -- pending | running | done | failed
    retry_count  INTEGER NOT NULL DEFAULT 0,
    max_retries  INTEGER NOT NULL DEFAULT 3,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    scheduled_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    started_at   TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    error        TEXT NOT NULL DEFAULT ''
);

-- ─────────────────────────────────────────────────────────────────────────────
-- Evidence immutability
-- Constraint: hash_value must be present (legal: file must be verifiable).
-- Trigger: block any attempt to UPDATE hash_value after initial insert.
-- ─────────────────────────────────────────────────────────────────────────────

-- 1. NOT NULL constraint (idempotent — safe to run again if already applied)
DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'evidence'
          AND column_name = 'hash_value'
          AND is_nullable = 'NO'
    ) THEN
        ALTER TABLE evidence ALTER COLUMN hash_value SET NOT NULL;
        ALTER TABLE evidence ALTER COLUMN hash_value SET DEFAULT '';
    END IF;
END $$;

-- 2. Trigger: prevent hash_value from being changed once set
CREATE OR REPLACE FUNCTION evidence_hash_immutable()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    IF OLD.hash_value IS NOT NULL AND OLD.hash_value <> '' AND NEW.hash_value <> OLD.hash_value THEN
        RAISE EXCEPTION
            'evidence_hash_immutable: hash_value cannot be changed after initial upload (evidence id=%). '
            'Legal integrity requires the original file hash to be permanent.',
            OLD.id;
    END IF;
    RETURN NEW;
END;
$$;

DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_trigger
        WHERE tgname = 'trg_evidence_hash_immutable'
    ) THEN
        EXECUTE '
            CREATE TRIGGER trg_evidence_hash_immutable
            BEFORE UPDATE ON evidence
            FOR EACH ROW EXECUTE FUNCTION evidence_hash_immutable()
        ';
    END IF;
END $$;

-- ─────────────────────────────────────────────────────────────────────────────
-- Signature snapshot columns
-- Store a PDF hash and TOTP-verified flag directly on each signature record.
-- Required for ESIGN Act compliance and for the signing certificate page.
-- ─────────────────────────────────────────────────────────────────────────────
ALTER TABLE signatures ADD COLUMN IF NOT EXISTS contract_snapshot_hash TEXT NOT NULL DEFAULT '';
ALTER TABLE signatures ADD COLUMN IF NOT EXISTS totp_verified          BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE signatures ADD COLUMN IF NOT EXISTS user_agent             TEXT NOT NULL DEFAULT '';

-- ─────────────────────────────────────────────────────────────────────────────
-- JWT refresh token store
-- Raw tokens are NEVER stored — only SHA-256 hashes.
-- Tokens expire after 7 days and are revoked on sign-out / password reset.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS refresh_tokens (
    token_hash TEXT        PRIMARY KEY,
    user_id    TEXT        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    expires_at TIMESTAMPTZ NOT NULL,
    revoked    BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

