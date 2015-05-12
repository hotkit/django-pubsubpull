-- The Postgres trigger function

CREATE OR REPLACE FUNCTION pubsubpull_change_recorder() RETURNS TRIGGER AS $body$
BEGIN
  IF (TG_OP = 'DELETE') THEN
    INSERT INTO pubsubpull_updatelog ("table", "when", old, new)
    SELECT TG_TABLE_NAME, now(), row_to_json(OLD)::jsonb, NULL;
  ELSEIF (TG_OP = 'UPDATE') THEN
    INSERT INTO pubsubpull_updatelog ("table", "when", old, new)
    SELECT TG_TABLE_NAME, now(), row_to_json(OLD)::jsonb, row_to_json(NEW)::jsonb;
  ELSEIF (TG_OP = 'INSERT') THEN
    INSERT INTO pubsubpull_updatelog ("table", "when", old, new)
    SELECT TG_TABLE_NAME, now(), NULL, row_to_json(NEW)::jsonb;
  END IF;
  RETURN NULL;
END;
$body$ LANGUAGE plpgsql;
