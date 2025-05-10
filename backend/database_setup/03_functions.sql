CREATE OR REPLACE FUNCTION match_knowledge_articles (
  query_embedding VECTOR(1536),
  match_threshold FLOAT,
  match_count INT
)
RETURNS TABLE (
  id UUID,
  title TEXT,
  content TEXT,
  category TEXT,
  tags TEXT[],
  source_url TEXT,
  similarity FLOAT
)
LANGUAGE sql STABLE
AS $$
  SELECT
    ka.id,
    ka.title,
    ka.content,
    ka.category,
    ka.tags,
    ka.source_url,
    1 - (ka.embedding <=> query_embedding) AS similarity
  FROM
    public.knowledge_articles AS ka
  WHERE 1 - (ka.embedding <=> query_embedding) > match_threshold
  ORDER BY
    ka.embedding <=> query_embedding
  LIMIT match_count;
$$; 