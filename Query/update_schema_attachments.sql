-- Script cập nhật database hỗ trợ đính kèm tệp
-- Chạy script này trong pgAdmin 4

BEGIN;

-- 1. Tạo bảng tepdinhkem nếu chưa tồn tại
CREATE TABLE IF NOT EXISTS public.tepdinhkem
(
    matepdinhkem serial NOT NULL,
    duongdan text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT tepdinhkem_pkey PRIMARY KEY (matepdinhkem)
);

-- 2. Thêm cột matepdinhkem vào bảng thongbao nếu chưa có
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='thongbao' AND column_name='matepdinhkem') THEN
        ALTER TABLE public.thongbao ADD COLUMN matepdinhkem integer;
    END IF;
END $$;

-- 3. Thêm khóa ngoại (Foreign Key)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints 
                   WHERE constraint_name='thongbao_matepdinhkem_fkey') THEN
        ALTER TABLE public.thongbao
            ADD CONSTRAINT thongbao_matepdinhkem_fkey FOREIGN KEY (matepdinhkem)
            REFERENCES public.tepdinhkem (matepdinhkem) MATCH SIMPLE
            ON UPDATE NO ACTION
            ON DELETE SET NULL;
    END IF;
END $$;

COMMIT;
