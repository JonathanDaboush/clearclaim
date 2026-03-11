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
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS devices (
    id          TEXT PRIMARY KEY,
    user_id     TEXT NOT NULL,
    device_info TEXT NOT NULL DEFAULT '',
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
    created_by      TEXT NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    current_version TEXT
);

CREATE TABLE IF NOT EXISTS contract_versions (
    id             TEXT PRIMARY KEY,
    contract_id    TEXT NOT NULL,
    content        TEXT NOT NULL DEFAULT '',
    created_by     TEXT NOT NULL DEFAULT '',
    version_number INTEGER NOT NULL DEFAULT 1,
    content_hash   TEXT NOT NULL DEFAULT '',
    signed         BOOLEAN NOT NULL DEFAULT FALSE,
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
