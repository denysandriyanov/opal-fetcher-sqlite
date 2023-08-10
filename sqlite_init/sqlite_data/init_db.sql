-- init_db.sql
CREATE TABLE city (
                      id INTEGER PRIMARY KEY,
                      name TEXT,
                      population INTEGER
);

INSERT INTO city (name, population) VALUES ('New York', 8175133);
INSERT INTO city (name, population) VALUES ('Los Angeles', 3792621);
INSERT INTO city (name, population) VALUES ('Chicago', 2695598);
INSERT INTO city (name, population) VALUES ('Houston', 2100263);
INSERT INTO city (name, population) VALUES ('Phoenix', 1445632);
