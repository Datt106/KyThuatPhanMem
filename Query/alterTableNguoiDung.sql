INSERT INTO tepdinhkem 
VALUES (1, './images/default.png')

ALTER TABLE NguoiDung
ADD COLUMN Avarta INT NOT NULL
DEFAULT 1
REFERENCES tepdinhkem(MaTepDinhKem)

ALTER TABLE NguoiDung
ADD COLUMN NgheNghiep TEXT

