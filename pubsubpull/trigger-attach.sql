-- Attach the trigger to the requested table

DROP TRIGGER IF EXISTS "update_log_{db_table}" ON "{db_table}";

CREATE TRIGGER "update_log_{db_table}"
    AFTER INSERT OR UPDATE OR DELETE
    ON "{db_table}"
    FOR EACH ROW
    EXECUTE PROCEDURE pubsubpull_change_recorder();
