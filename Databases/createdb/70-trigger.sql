DELIMITER $$

CREATE TRIGGER relstatus_lastchange BEFORE UPDATE ON relstatus
   FOR EACH ROW
   BEGIN
      IF NEW.status <> OLD.status OR NEW.ampere <> OLD.ampere THEN
         SET NEW.lastchange = NEW.lastupdate;   
      END IF;
   END$$

CREATE TRIGGER inpstatus_lastchange BEFORE UPDATE ON inpstatus
   FOR EACH ROW
   BEGIN
      IF NEW.status <> OLD.status THEN
         SET NEW.lastchange = NEW.lastupdate;
      END IF;
   END$$

CREATE TRIGGER anastatus_lastchange BEFORE UPDATE ON anastatus
   FOR EACH ROW
   BEGIN
      IF NEW.status <> OLD.status THEN
         SET NEW.lastchange = NEW.lastupdate;
      END IF;
   END$$

CREATE TRIGGER actstatus_lastchange BEFORE UPDATE ON actstatus
   FOR EACH ROW
   BEGIN
      IF NEW.status <> OLD.status OR NEW.status2 <> OLD.status2 THEN
         SET NEW.lastchange = NEW.lastupdate;
      END IF;
   END$$


DELIMITER ;
