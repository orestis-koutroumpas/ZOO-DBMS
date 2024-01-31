BEGIN TRANSACTION;

-- Animal Table
DROP TABLE IF EXISTS "ANIMAL";
CREATE TABLE IF NOT EXISTS "ANIMAL" (
	"Animal_ID" integer NOT NULL,
	"Purchase_ID" integer NOT NULL,
	"Exhibit_ID" integer NOT NULL,
	"Class" varchar(20) NOT NULL DEFAULT 'UNKNOWN',
	"Nutrition" varchar(20) NOT NULL DEFAULT 'UNKNOWN',
	"Species" varchar(20) NOT NULL DEFAULT 'UNKNOWN',
	"Name" 	varchar(20) NOT NULL DEFAULT 'UNKNOWN',
	"Age" integer DEFAULT NULL,
	"Weight" integer DEFAULT NULL,		
	"Import_Date" date DEFAULT NULL,
	PRIMARY KEY ("Animal_ID"),
	CONSTRAINT "ANIMAL_Purchase_ID_fk_1"
	FOREIGN KEY ("Purchase_ID") REFERENCES "PURCHASE" ("Purchase_ID")
    ON UPDATE CASCADE
    ON DELETE CASCADE,
	CONSTRAINT "ANIMAL_Exhibit_ID_fk_1"
	FOREIGN KEY ("Exhibit_ID") REFERENCES "EXHIBIT" ("Exhibit_ID")
    ON UPDATE CASCADE
    ON DELETE CASCADE
);

-- Eating Table
DROP TABLE IF EXISTS "EATING";
CREATE TABLE IF NOT EXISTS "EATING" (
	"Eating_ID"	integer NOT NULL,
 	"Animal_ID" integer NOT NULL,
	"Food_ID" integer NOT NULL,
	"Amount" integer DEFAULT NULL,
	PRIMARY KEY ("Eating_ID","Food_ID"),
	CONSTRAINT "EATING_Animal_ID_fk_1"
	FOREIGN KEY ("Animal_ID") REFERENCES "ANIMAL" ("Animal_ID")
    ON UPDATE CASCADE
    ON DELETE CASCADE,
	CONSTRAINT "EATING_Food_ID_fk_1"
	FOREIGN KEY ("Food_ID") REFERENCES "FOOD" ("Food_ID")
    ON UPDATE CASCADE
    ON DELETE CASCADE
);

-- Employee Table
DROP TABLE IF EXISTS "EMPLOYEE";
CREATE TABLE IF NOT EXISTS "EMPLOYEE" (
	"Employee_ID" integer NOT NULL,
	"First_Name" varchar(15) NOT NULL DEFAULT 'UNKNOWN',
	"Last_Name" varchar(20) NOT NULL DEFAULT 'UNKNOWN',
	"Date_of_Birth" date DEFAULT NULL,
	"Address" varchar(50) DEFAULT NULL,
	"Start_Date" date DEFAULT NULL,
	"Starting_Hour" time DEFAULT NULL,
	"Finishing_Hour" time DEFAULT NULL,
	"Salary" integer NOT NULL DEFAULT 0,
	PRIMARY KEY ("Employee_ID")
);

-- Exhibit Table
DROP TABLE IF EXISTS "EXHIBIT";
CREATE TABLE IF NOT EXISTS "EXHIBIT" (
	"Exhibit_ID" integer NOT NULL,
	"Employee_ID" integer NOT NULL,
	"Cage_Name" varchar(20) NOT NULL DEFAULT 'Unknown',
	"Zone" 	varchar(5) 	NOT NULL,
	"Starting_Hour" time DEFAULT NULL,
	"Finishing_Hour" time DEFAULT NULL,
	PRIMARY KEY ("Exhibit_ID"),
	CONSTRAINT "EXHIBIT_Employee_ID_fk_1"
	FOREIGN KEY ("Employee_ID") REFERENCES "EMPLOYEE" ("Employee_ID")
    ON UPDATE CASCADE
    ON DELETE CASCADE
);

-- Feeding Table
DROP TABLE IF EXISTS "FEEDING";
CREATE TABLE IF NOT EXISTS "FEEDING" (
	"Feeding_ID" integer NOT NULL,
	"Animal_ID" integer NOT NULL,
	"Employee_ID" integer NOT NULL,
	"Time" datetime DEFAULT NULL,
	PRIMARY KEY ("Feeding_ID"),
	CONSTRAINT "FEEDING_Animal_ID_fk_1"
	FOREIGN KEY ("Animal_ID") REFERENCES "ANIMAL" ("Animal_ID")
    ON UPDATE CASCADE
    ON DELETE CASCADE,
	CONSTRAINT "FEEDING_Employee_ID_fk_1"
	FOREIGN KEY ("Employee_ID") REFERENCES "EMPLOYEE" ("Employee_ID")
    ON UPDATE CASCADE
    ON DELETE CASCADE
);

-- Food Table
DROP TABLE IF EXISTS "FOOD";
CREATE TABLE IF NOT EXISTS "FOOD" (
	"Food_ID" integer NOT NULL,
	"Name" varchar(20) NOT NULL,
	"Category" varchar(20) DEFAULT NULL,
	PRIMARY KEY ("Food_ID")
);

-- Purchase Table
DROP TABLE IF EXISTS "PURCHASE";
CREATE TABLE IF NOT EXISTS "PURCHASE" (
	"Purchase_ID" 	integer NOT NULL,
	"Place_Of_Origin" varchar(30) NOT NULL,
	"Purchase_Date" date DEFAULT NULL,
	"Price" integer NOT NULL DEFAULT 0,
	PRIMARY KEY ("Purchase_ID")
);

-- Vet Table 
DROP TABLE IF EXISTS "VET";
CREATE TABLE IF NOT EXISTS "VET" (
	"Medical_Case_ID" integer NOT NULL,
	"Animal_ID" integer NOT NULL,
	"Reason" varchar(30) DEFAULT NULL,
	"Import_Date" date DEFAULT NULL,
	"Export_Date" date DEFAULT NULL,
	PRIMARY KEY ("Medical_Case_ID")
	CONSTRAINT "Vet_Animal_ID_fk_1"
	FOREIGN KEY ("Animal_ID") REFERENCES "ANIMAL" ("Animal_ID")
    ON UPDATE CASCADE
    ON DELETE CASCADE
);

-- Indexes for table "ANIMAL"
DROP INDEX IF EXISTS idx_ANIMAL_Animal_ID;
CREATE INDEX IF NOT EXISTS idx_ANIMAL_Animal_ID ON "ANIMAL" ("Animal_ID");
DROP INDEX IF EXISTS idx_ANIMAL_Purchase_ID;
CREATE INDEX IF NOT EXISTS idx_ANIMAL_Purchase_ID ON "ANIMAL" ("Purchase_ID");
DROP INDEX IF EXISTS idx_ANIMAL_Exhibit_ID;
CREATE INDEX IF NOT EXISTS idx_ANIMAL_Exhibit_ID ON "ANIMAL" ("Exhibit_ID");

-- Indexes for table "EATING"
DROP INDEX IF EXISTS idx_EATING_Animal_ID;
CREATE INDEX IF NOT EXISTS idx_EATING_Animal_ID ON "EATING" ("Animal_ID");
DROP INDEX IF EXISTS idx_EATING_Food_ID;
CREATE INDEX IF NOT EXISTS idx_EATING_Food_ID ON "EATING" ("Food_ID");

-- Indexes for table "EMPLOYEE"
DROP INDEX IF EXISTS idx_EMPLOYEE_Employee_ID;
CREATE INDEX IF NOT EXISTS idx_EMPLOYEE_Employee_ID ON "EMPLOYEE" ("Employee_ID");

-- Indexes for table "EXHIBIT"
DROP INDEX IF EXISTS idx_EXHIBIT_Exhibit_ID;
CREATE INDEX IF NOT EXISTS idx_EXHIBIT_Exhibit_ID ON "EXHIBIT" ("Exhibit_ID");
DROP INDEX IF EXISTS idx_EXHIBIT_Employee_ID;
CREATE INDEX IF NOT EXISTS idx_EXHIBIT_Employee_ID ON "EXHIBIT" ("Employee_ID");
-- Indexes for table "FEEDING"
DROP INDEX IF EXISTS idx_FEEDING_Animal_ID;
CREATE INDEX IF NOT EXISTS idx_FEEDING_Animal_ID ON "FEEDING" ("Animal_ID");
DROP INDEX IF EXISTS idx_FEEDING_Employee_ID;
CREATE INDEX IF NOT EXISTS idx_FEEDING_Employee_ID ON "FEEDING" ("Employee_ID");

-- Indexes for table "FOOD"
DROP INDEX IF EXISTS idx_FOOD_Food_ID;
CREATE INDEX IF NOT EXISTS idx_FOOD_Food_ID ON "FOOD" ("Food_ID");

-- Indexes for table "PURCHASE"
DROP INDEX IF EXISTS idx_PURCHASE_Purchase_ID;
CREATE INDEX IF NOT EXISTS idx_PURCHASE_Purchase_ID ON "PURCHASE" ("Purchase_ID");

-- Indexes for table "VET"
DROP INDEX IF EXISTS idx_VET_Medical_Case_ID;
CREATE INDEX IF NOT EXISTS idx_VET_Medical_Case_ID ON "VET" ("Medical_Case_ID");
DROP INDEX IF EXISTS idx_VET_Animal_ID;
CREATE INDEX IF NOT EXISTS idx_VET_Animal_ID ON "ANIMAL" ("Animal_ID");

COMMIT;