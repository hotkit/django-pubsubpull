-- The Postgres trigger function

CREATE OR REPLACE FUNCTION pubsubpull_change_recorder() RETURNS TRIGGER AS $body$
BEGIN
  IF (TG_OP = 'DELETE') THEN
    INSERT INTO pubsubpull_updatelog ("table", old, new)
    SELECT 'table_name', row_to_json(OLD), NULL;
  ELSEIF (TG_OP = 'UPDATE') THEN
    INSERT INTO pubsubpull_updatelog ("table", old, new)
    SELECT 'table_name', row_to_json(OLD), row_to_json(NEW);
  ELSEIF (TG_OP = 'INSERT') THEN
    INSERT INTO pubsubpull_updatelog ("table", old, new)
    SELECT 'table_name', NULL, row_to_json(NEW);
  END IF;
  RETURN NULL;
END;
$body$ LANGUAGE plpgsql;
