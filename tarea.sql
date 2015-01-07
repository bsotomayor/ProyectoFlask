DROP TABLE IF EXISTS "imagen";
CREATE TABLE "imagen" ("ID" INTEGER PRIMARY KEY  NOT NULL ,"nombre" VARCHAR,"fecha_subida" DATETIME,"tema" VARCHAR,"descripcion" TEXT,"camara" VARCHAR,"id_usuario" INTEGER,"data" BLOB, "nombre_archivo" VARCHAR);
DROP TABLE IF EXISTS "user";
CREATE TABLE user ( id integer primary key autoincrement, name text not null, user text not null unique, pass text not null, salt text not null, "pais" VARCHAR, "email" VARCHAR);
INSERT INTO "user" VALUES(1,'admin','admin','dcf9a401e434230d7f789fc810055d91034c45a835815b9683be0768','fYzJf','admin','admin');
