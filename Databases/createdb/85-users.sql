ALTER TABLE  `users` ADD  `slide` TINYINT( 1 ) NOT NULL DEFAULT  '0', ADD  `webspeech` ENUM(  'no',  'touch',  'continuous' ) NOT NULL DEFAULT  'touch';
ALTER TABLE  `users` ADD  `speechlang` ENUM(  'en-US','en-GB','it-IT','it-CH' ) NOT NULL DEFAULT  'en-US';
