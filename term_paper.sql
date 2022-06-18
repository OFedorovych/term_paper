USE term_paper;

DROP TABLE IF EXISTS TValues;
DROP TABLE IF EXISTS Sensors;
DROP TABLE IF EXISTS Devices;

SET time_zone ='+03:00';

/*----------------------------------------------------------------------------------------*/

CREATE TABLE TValues(
	ID int AUTO_INCREMENT PRIMARY KEY NOT NULL,
    SensorID int NOT NULL,
    Time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Value float
);


CREATE TABLE Sensors(
		ID int AUTO_INCREMENT PRIMARY KEY NOT NULL,
    DevID int NOT NULL,
    CmdID int NOT NULL,
    Name varchar(20)  NOT NULL
);

CREATE TABLE Devices (
	ID int AUTO_INCREMENT PRIMARY KEY NOT NULL,
    Address int NOT NULL,
    Name varchar(20)  NOT NULL
);

/*----------------------------------------------------------------------------------------*/

ALTER TABLE Sensors ADD  CONSTRAINT FK_Sensors_Devices FOREIGN KEY(DevID)
	REFERENCES Devices (ID)
	ON UPDATE CASCADE
	ON DELETE CASCADE;
    
ALTER TABLE TValues ADD  CONSTRAINT FK_TValues_Sensors_ FOREIGN KEY(SensorID)
	REFERENCES Sensors (ID)
	ON UPDATE CASCADE
	ON DELETE CASCADE;

/*----------------------------------------------------------------------------------------*/

INSERT INTO Devices (Address, Name) VALUES (233, "ATMega328P");
INSERT INTO Devices (Address, Name) VALUES (234, "ATMega328P");

INSERT INTO Sensors (DevID, CmdID, Name) VALUES (1, 1, "distance");
INSERT INTO Sensors (DevID, CmdID, Name) VALUES (1, 2, "dust");
INSERT INTO Sensors (DevID, CmdID, Name) VALUES (2, 3, "humidity");
INSERT INTO Sensors (DevID, CmdID, Name) VALUES (2, 4, "temperature");




-- select * from tvalues;
-- select value from tvalues
-- where sensorid = 2;
-- select value, time from tvalues where sensorid = 2