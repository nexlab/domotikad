/***************************************************************************
* Copyright (c) 2011-2014 Unixmedia S.r.l. <info@unixmedia.it>
* Copyright (c) 2011-2014 Franco (nextime) Lanza <franco@unixmedia.it>
*
* Domotika System Controller Daemon "domotikad"  [http://trac.unixmedia.it]
*
* This file is part of domotikad.
*
* domotikad is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation, either version 3 of the License, or
* (at your option) any later version.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with this program.  If not, see <http://www.gnu.org/licenses/>.
*
******************************************************************************/

CREATE DATABASE domotika;
CREATE USER 'domotika'@'localhost' IDENTIFIED BY  'dmdbpwdmsql';
CREATE USER 'asterisk'@'localhost' IDENTIFIED BY  'astdbpwd';
GRANT USAGE ON * . * TO  'domotika'@'localhost' IDENTIFIED BY  'dmdbpwdmsql' WITH MAX_QUERIES_PER_HOUR 0 MAX_CONNECTIONS_PER_HOUR 0 MAX_UPDATES_PER_HOUR 0 MAX_USER_CONNECTIONS 0 ;
GRANT USAGE ON * . * TO  'asterisk'@'localhost' IDENTIFIED BY  'dmdbpwdmsql' WITH MAX_QUERIES_PER_HOUR 0 MAX_CONNECTIONS_PER_HOUR 0 MAX_UPDATES_PER_HOUR 0 MAX_USER_CONNECTIONS 0 ;
GRANT ALL PRIVILEGES ON  `domotika` . * TO  'domotika'@'localhost' WITH GRANT OPTION ;
GRANT ALL PRIVILEGES ON  `domotika` . * TO  'asterisk'@'localhost' WITH GRANT OPTION ;
FLUSH PRIVILEGES;

