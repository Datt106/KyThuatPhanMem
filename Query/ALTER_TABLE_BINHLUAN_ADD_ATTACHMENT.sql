-- Thêm cột matepdinhkem vào bảng binhluan
ALTER TABLE binhluan 
ADD COLUMN matepdinhkem integer;

-- Thêm foreign key constraint
ALTER TABLE binhluan 
ADD CONSTRAINT binhluan_matepdinhkem_fkey 
FOREIGN KEY (matepdinhkem) 
REFERENCES tepdinhkem (matepdinhkem) 
ON DELETE SET NULL;

-- Tạo index cho hiệu suất tốt hơn
CREATE INDEX IF NOT EXISTS idx_binhluan_matepdinhkem 
ON binhluan(matepdinhkem);
