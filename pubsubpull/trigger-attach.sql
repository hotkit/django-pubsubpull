-- Attach the trigger to the requested table

CREATE TRIGGER "update_log_slumber_examples_pizza"
    AFTER INSERT OR UPDATE OR DELETE
    ON "slumber_examples_pizza"
    FOR EACH ROW
    EXECUTE PROCEDURE pubsubpull_change_recorder();
