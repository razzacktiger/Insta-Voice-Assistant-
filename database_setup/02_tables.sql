-- ==== USER PROFILES TABLE ====
CREATE TABLE IF NOT EXISTS public.user_profiles (
    user_id TEXT PRIMARY KEY,
    email TEXT UNIQUE,
    full_name TEXT,
    subscription_tier TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER on_user_profiles_updated
  BEFORE UPDATE ON public.user_profiles
  FOR EACH ROW
  EXECUTE PROCEDURE public.handle_updated_at();

ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;

-- ==== KNOWLEDGE ARTICLES TABLE ====
CREATE TABLE IF NOT EXISTS public.knowledge_articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR(1536),
    category TEXT,
    tags TEXT[],
    source_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE TRIGGER on_knowledge_articles_updated
  BEFORE UPDATE ON public.knowledge_articles
  FOR EACH ROW
  EXECUTE PROCEDURE public.handle_updated_at();

ALTER TABLE public.knowledge_articles ENABLE ROW LEVEL SECURITY;

-- ==== INTERACTION SUMMARIES TABLE ====
CREATE TABLE IF NOT EXISTS public.interaction_summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL REFERENCES public.user_profiles(user_id) ON DELETE CASCADE,
    session_id TEXT,
    summary TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

ALTER TABLE public.interaction_summaries ENABLE ROW LEVEL SECURITY; 