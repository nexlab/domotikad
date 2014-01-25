ALTER TABLE  `users` ADD  `left_bar` ENUM(  'all',  'none', 'visible-sm',  'visible-md',  'visible-lg',  'hidden-sm',  'hidden-md',  'hidden-lg' ) NOT NULL DEFAULT  'hidden-sm',
ADD  `right_bar` ENUM(  'all',  'none',  'visible-sm',  'visible-md',  'visible-lg',  'hidden-sm',  'hidden-md',  'hidden-lg' ) NOT NULL DEFAULT  'hidden-sm';
