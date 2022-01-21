CREATE TABLE info(username VARCHAR(200), password VARCHAR(500), name VARCHAR(100), prof INT, street VARCHAR(100), city VARCHAR(50), phone VARCHAR(32), PRIMARY KEY(username));
CREATE TABLE trainers(username VARCHAR(100), PRIMARY KEY(username));
CREATE TABLE receptionalist(username VARCHAR(100), PRIMARY KEY(username));
CREATE TABLE equipments(name VARCHAR(200), count INT, PRIMARY KEY(name));
CREATE TABLE workoutplans(name VARCHAR(200), duration VARCHAR(200),price INT, PRIMARY KEY(name) );
CREATE TABLE members(username VARCHAR(200), plan VARCHAR(200), trainer VARCHAR(200), PRIMARY KEY(username) ,FOREIGN KEY(username) references info(username));
CREATE TABLE dailyupdate(username VARCHAR(100),exercise VARCHAR(200),sets INT,reps INT,date VARCHAR(100),time VARCHAR(100), PRIMARY KEY(exercise));
CREATE TABLE attendance(username VARCHAR(100) , date VARCHAR(100), time VARCHAR(100), latitude VARCHAR(100), longitude VARCHAR(100), PRIMARY KEY(username,date));