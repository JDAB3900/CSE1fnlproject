USE init_db;

INSERT INTO departments (name, description) VALUES
('IT','Information Technology'),
('HR','Human Resources'),
('Finance','Finance Department');

INSERT INTO users (username, password, role) VALUES
('admin','admin_hashed_password','admin');

INSERT INTO employees (first_name,middle_name,last_name,name_extension,birthdate,birth_city,birth_province,birth_country,sex,civil_status,department_id) VALUES
('Jose','A.','Dabs','','1998-01-10','CityA','ProvA','Philippines','Male','Single',1),
('Maria','B.','Santos','','1995-03-21','CityB','ProvB','Philippines','Female','Single',2),
('Juan','C.','Reyes','','1988-07-12','CityC','ProvC','Philippines','Male','Married',1),
('Anna','D.','Lopez','','1990-02-28','CityD','ProvD','Philippines','Female','Single',3),
('Mark','E.','Tan','','1992-10-02','CityE','ProvE','Philippines','Male','Single',1),
('Liza','F.','Garcia','','1985-06-14','CityF','ProvF','Philippines','Female','Married',2),
('Ken','G.','Lim','','1991-09-09','CityG','ProvG','Philippines','Male','Single',3),
('Rosa','H.','Cruz','','1987-11-01','CityH','ProvH','Philippines','Female','Married',2),
('Pedro','I.','Lopez','','1993-12-12','CityI','ProvI','Philippines','Male','Single',1),
('Maya','J.','Santos','','1999-05-05','CityJ','ProvJ','Philippines','Female','Single',3),
('Lloyd','K.','Vega','','1989-04-04','CityK','ProvK','Philippines','Male','Married',1),
('Nina','L.','Ramos','','1994-08-18','CityL','ProvL','Philippines','Female','Single',2),
('Omar','M.','Diaz','','1983-03-03','CityM','ProvM','Philippines','Male','Married',3),
('Faye','N.','Lopez','','1996-07-07','CityN','ProvN','Philippines','Female','Single',1),
('Ike','O.','Torres','','1997-11-11','CityO','ProvO','Philippines','Male','Single',2),
('Gina','P.','Reyes','','1986-09-09','CityP','ProvP','Philippines','Female','Married',3),
('Tito','Q.','Cruz','','1990-01-20','CityQ','ProvQ','Philippines','Male','Married',1),
('Luna','R.','Santos','','1992-02-14','CityR','ProvR','Philippines','Female','Single',2),
('Vince','S.','Gomez','','1998-06-06','CityS','ProvS','Philippines','Male','Single',3),
('Paula','T.','Reyes','','1995-05-15','CityT','ProvT','Philippines','Female','Single',1),
('Ramon','U.','Alvarez','','1984-12-30','CityU','ProvU','Philippines','Male','Married',2),
('Bela','V.','Santos','','1993-04-22','CityV','ProvV','Philippines','Female','Single',3),
('Derek','W.','Ibrahim','','1991-08-08','CityW','ProvW','Philippines','Male','Single',1),
('Zara','X.','Lopez','','1997-03-03','CityX','ProvX','Philippines','Female','Single',2),
('Kyle','Y.','Mendoza','','1996-10-10','CityY','ProvY','Philippines','Male','Single',3);