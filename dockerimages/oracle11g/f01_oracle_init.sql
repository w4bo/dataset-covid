CREATE DIRECTORY ORACLE_DUMP as '/data';

create user covid_weekly identified by oracle;
grant all privileges to covid_weekly;
grant read, write on directory oracle_dump to system;
grant read, write on directory oracle_dump to covid_weekly;
