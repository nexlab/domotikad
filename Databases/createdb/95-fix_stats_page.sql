ALTER TABLE  `user_gui_panels` CHANGE  `page`  `page` ENUM(  'actuations',  'video',  'cameras',  'stats',  'gmi' ) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL DEFAULT  'actuations';
DELETE FROM user_gui_panels where page='';
