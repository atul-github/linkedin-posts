-- Table: public.mentions

-- DROP TABLE IF EXISTS public.mentions;

CREATE TABLE IF NOT EXISTS public.mentions
(
    id integer NOT NULL DEFAULT nextval('mentions_id_seq'::regclass),
    mention_url text COLLATE pg_catalog."default",
    post_id integer,
    CONSTRAINT mentions_pkey PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.mentions
    OWNER to postgres;
    
-- Table: public.messages

-- DROP TABLE IF EXISTS public.messages;

CREATE TABLE IF NOT EXISTS public.messages
(
    id integer NOT NULL DEFAULT nextval('messages_id_seq'::regclass),
    post_text text COLLATE pg_catalog."default",
    create_url text COLLATE pg_catalog."default",
    type text COLLATE pg_catalog."default",
    post_id integer,
    CONSTRAINT messages_pkey PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.messages
    OWNER to postgres;
        