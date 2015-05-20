-- The Postgres trigger function

CREATE OR REPLACE FUNCTION pubsubpull_change_recorder() RETURNS TRIGGER AS $body$
DECLARE
    request_id int;
BEGIN
    BEGIN
    request_id := current_setting('pubsubpull.request_id');
    EXCEPTION
        WHEN OTHERS THEN
            request_id := NULL;
    END;
    IF (TG_OP = 'DELETE') THEN
        INSERT INTO pubsubpull_updatelog ("table", type, "when", request_id, old, new)
            SELECT TG_TABLE_NAME, 'D', now(), request_id, row_to_json(OLD)::jsonb, NULL;
    ELSEIF (TG_OP = 'UPDATE') THEN
        INSERT INTO pubsubpull_updatelog ("table", type, "when", request_id, old, new)
            SELECT TG_TABLE_NAME, 'U', now(), request_id, row_to_json(OLD)::jsonb, row_to_json(NEW)::jsonb;
    ELSEIF (TG_OP = 'INSERT') THEN
        INSERT INTO pubsubpull_updatelog ("table", type, "when", request_id, old, new)
            SELECT TG_TABLE_NAME, 'I', now(), request_id, NULL, row_to_json(NEW)::jsonb;
    END IF;
    RETURN NULL;
END;
$body$ LANGUAGE plpgsql;
