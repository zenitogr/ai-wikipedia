DROP TABLE IF EXISTS articles;

CREATE TABLE articles (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    images TEXT,
    image_suggestions TEXT
);