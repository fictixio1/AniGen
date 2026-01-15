-- Core tables for canon and scene tracking

CREATE TABLE IF NOT EXISTS series_state (
    id SERIAL PRIMARY KEY,
    current_episode INTEGER NOT NULL DEFAULT 1,
    current_scene_in_episode INTEGER NOT NULL DEFAULT 1,
    total_scenes INTEGER NOT NULL DEFAULT 0,
    total_episodes INTEGER NOT NULL DEFAULT 0,
    last_generated_at TIMESTAMP,
    system_status VARCHAR(50) DEFAULT 'idle',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS characters (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    image_url TEXT NOT NULL,
    image_version INTEGER DEFAULT 1,
    canonical_state TEXT,
    first_appearance_scene INTEGER,
    last_appearance_scene INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS episodes (
    id SERIAL PRIMARY KEY,
    episode_number INTEGER UNIQUE NOT NULL,
    total_duration_seconds INTEGER DEFAULT 180,
    director_plan TEXT NOT NULL,
    episode_arc_summary TEXT,
    generation_started_at TIMESTAMP,
    generation_completed_at TIMESTAMP,
    total_cost_usd DECIMAL(10,4),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS scenes (
    id SERIAL PRIMARY KEY,
    scene_number INTEGER UNIQUE NOT NULL,
    episode_id INTEGER REFERENCES episodes(id) ON DELETE CASCADE,
    scene_in_episode INTEGER NOT NULL,
    video_url TEXT NOT NULL,
    duration_seconds INTEGER DEFAULT 30,
    video_prompt TEXT NOT NULL,
    narrative_summary TEXT NOT NULL,
    generation_started_at TIMESTAMP,
    generation_completed_at TIMESTAMP,
    generation_cost_usd DECIMAL(10,4),
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS narrative_context (
    id SERIAL PRIMARY KEY,
    scene_id INTEGER REFERENCES scenes(id) ON DELETE CASCADE,
    context_type VARCHAR(50),
    content TEXT NOT NULL,
    priority INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS generation_logs (
    id SERIAL PRIMARY KEY,
    scene_number INTEGER,
    log_level VARCHAR(20),
    component VARCHAR(50),
    message TEXT NOT NULL,
    error_details TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_episodes_episode_number ON episodes(episode_number DESC);
CREATE INDEX IF NOT EXISTS idx_scenes_scene_number ON scenes(scene_number DESC);
CREATE INDEX IF NOT EXISTS idx_scenes_episode ON scenes(episode_id);
CREATE INDEX IF NOT EXISTS idx_narrative_context_scene ON narrative_context(scene_id);
CREATE INDEX IF NOT EXISTS idx_generation_logs_scene ON generation_logs(scene_number);

-- Initialize series state with default values
INSERT INTO series_state (id, current_episode, current_scene_in_episode, total_scenes, total_episodes)
VALUES (1, 1, 1, 0, 0)
ON CONFLICT (id) DO NOTHING;
