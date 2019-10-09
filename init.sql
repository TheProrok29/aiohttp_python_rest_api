do $$ begin
    create type public.user_role as enum ('user', 'admin');
exception
    when duplicate_object then null;
end $$;


CREATE TABLE IF NOT EXISTS public.user (
    name varchar(60),
    password varchar(60),
    role user_role DEFAULT 'user',

    PRIMARY KEY (name),
    UNIQUE (name, role)
);

CREATE TABLE IF NOT EXISTS public.bird_sample (
    name varchar(60),
    path varchar(300),
    download_count int default 0,

    PRIMARY KEY (name),
    UNIQUE (name, path)
);

INSERT INTO public.user (name, password, role) VALUES ('tomasz', 'tomasz', 'admin');
INSERT INTO public.user (name, password, role) VALUES ('helion', 'helion', 'user');
