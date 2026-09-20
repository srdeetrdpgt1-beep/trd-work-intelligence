PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS cases (
    case_id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    source TEXT,
    source_message_id TEXT,
    trd_relevance TEXT,
    category TEXT,
    division TEXT,
    section TEXT,
    location TEXT,
    work_issue TEXT,
    asset TEXT,
    responsible_unit TEXT,
    responsible_person TEXT,
    status TEXT NOT NULL DEFAULT 'IN_PROGRESS',
    priority TEXT,
    original_due_date TEXT,
    current_target_date TEXT,
    delay_days INTEGER,
    delay_reason TEXT,
    material_status TEXT,
    next_action TEXT,
    next_followup TEXT,
    last_response TEXT,
    evidence_link TEXT,
    closed_at TEXT,
    ai_confidence REAL,
    human_verified INTEGER NOT NULL DEFAULT 0,
    is_ai_classified INTEGER NOT NULL DEFAULT 0,
    needs_human_review INTEGER NOT NULL DEFAULT 0,
    parent_case_id TEXT,
    related_case_id TEXT,
    duplicate_of_case_id TEXT
);

CREATE TABLE IF NOT EXISTS case_facts (
    fact_id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL,
    field_name TEXT NOT NULL,
    current_value TEXT,
    value_type TEXT,
    source_event_id TEXT,
    source_message_id TEXT,
    document_id TEXT,
    page_or_section TEXT,
    source_timestamp TEXT,
    asserted_at TEXT,
    ingested_timestamp TEXT NOT NULL,
    basis TEXT,
    source_reliability TEXT,
    ai_provider TEXT,
    ai_model TEXT,
    prompt_version TEXT,
    schema_version TEXT,
    processing_version TEXT,
    confidence REAL,
    human_verified INTEGER NOT NULL DEFAULT 0,
    verified_by TEXT,
    verified_at TEXT,
    locked INTEGER NOT NULL DEFAULT 0,
    valid_from TEXT,
    valid_to TEXT,
    is_current INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (case_id) REFERENCES cases(case_id)
);

CREATE TABLE IF NOT EXISTS actions (
    action_id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL,
    description TEXT NOT NULL,
    responsible_unit TEXT,
    responsible_person TEXT,
    status_raw TEXT,
    due_date TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    source_event_id TEXT,
    confidence REAL,
    human_verified INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (case_id) REFERENCES cases(case_id)
);

CREATE TABLE IF NOT EXISTS dependencies (
    dependency_id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL,
    description TEXT NOT NULL,
    dependency_type TEXT,
    responsible_unit TEXT,
    status_raw TEXT,
    blocking_raw TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    source_event_id TEXT,
    confidence REAL,
    human_verified INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (case_id) REFERENCES cases(case_id)
);

CREATE TABLE IF NOT EXISTS event_log (
    event_id TEXT PRIMARY KEY,
    case_id TEXT,
    timestamp TEXT NOT NULL,
    event_type TEXT NOT NULL,
    actor_type TEXT,
    actor_id TEXT,
    source_message_id TEXT,
    raw_message_text TEXT,
    old_value TEXT,
    new_value TEXT,
    reason TEXT,
    ai_confidence REAL,
    evidence_link TEXT,
    human_verified INTEGER NOT NULL DEFAULT 0,
    correlation_id TEXT,
    FOREIGN KEY (case_id) REFERENCES cases(case_id)
);

CREATE TABLE IF NOT EXISTS message_registry (
    message_id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    sender_reference TEXT,
    received_at TEXT NOT NULL,
    message_hash TEXT,
    message_type TEXT,
    raw_evidence_path TEXT,
    processing_status TEXT NOT NULL DEFAULT 'RECEIVED',
    correlation_id TEXT,
    restricted INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS document_registry (
    document_id TEXT PRIMARY KEY,
    case_id TEXT,
    filename TEXT,
    content_hash TEXT,
    mime_type TEXT,
    original_path TEXT,
    normalized_path TEXT,
    extraction_method TEXT,
    processing_version TEXT,
    registered_at TEXT NOT NULL,
    processing_status TEXT,
    FOREIGN KEY (case_id) REFERENCES cases(case_id)
);

CREATE TABLE IF NOT EXISTS followup_log (
    followup_id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL,
    question TEXT NOT NULL,
    recipient_reference TEXT,
    created_at TEXT NOT NULL,
    sent_at TEXT,
    attempt_count INTEGER NOT NULL DEFAULT 0,
    status TEXT,
    whatsapp_message_id TEXT,
    delivery_status TEXT,
    failure_code TEXT,
    FOREIGN KEY (case_id) REFERENCES cases(case_id)
);

CREATE TABLE IF NOT EXISTS human_review (
    review_id TEXT PRIMARY KEY,
    case_id TEXT,
    review_type TEXT NOT NULL,
    reason TEXT NOT NULL,
    created_at TEXT NOT NULL,
    reviewed_at TEXT,
    reviewer TEXT,
    decision TEXT,
    notes TEXT,
    FOREIGN KEY (case_id) REFERENCES cases(case_id)
);

CREATE TABLE IF NOT EXISTS system_config (
    config_key TEXT PRIMARY KEY,
    config_value TEXT,
    value_type TEXT,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_cases_status
    ON cases(status);

CREATE INDEX IF NOT EXISTS idx_cases_location
    ON cases(location);

CREATE INDEX IF NOT EXISTS idx_event_case
    ON event_log(case_id);

CREATE INDEX IF NOT EXISTS idx_event_timestamp
    ON event_log(timestamp);

CREATE INDEX IF NOT EXISTS idx_facts_case_current
    ON case_facts(case_id, is_current);

CREATE INDEX IF NOT EXISTS idx_messages_hash
    ON message_registry(message_hash);

CREATE INDEX IF NOT EXISTS idx_documents_hash
    ON document_registry(content_hash);

CREATE INDEX IF NOT EXISTS idx_followups_case
    ON followup_log(case_id);
