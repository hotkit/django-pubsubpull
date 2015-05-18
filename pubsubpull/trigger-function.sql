-- The Postgres trigger function

CREATE OR REPLACE FUNCTION pubsubpull_change_recorder() RETURNS TRIGGER AS $body$
BEGIN
  IF (TG_OP = 'DELETE') THEN
    INSERT INTO pubsubpull_updatelog ("table", type, "when", old, new)
    SELECT TG_TABLE_NAME, 'D', now(), row_to_json(OLD)::jsonb, NULL;
  ELSEIF (TG_OP = 'UPDATE') THEN
    INSERT INTO pubsubpull_updatelog ("table", type, "when", old, new)
    SELECT TG_TABLE_NAME, 'U', now(), row_to_json(OLD)::jsonb, row_to_json(NEW)::jsonb;
  ELSEIF (TG_OP = 'INSERT') THEN
    INSERT INTO pubsubpull_updatelog ("table", type, "when", old, new)
    SELECT TG_TABLE_NAME, 'I', now(), NULL, row_to_json(NEW)::jsonb;
  END IF;
  RETURN NULL;
END;
$body$ LANGUAGE plpgsql;
