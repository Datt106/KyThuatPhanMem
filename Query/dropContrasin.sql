-- Xóa Trigger liên quan bảng TinNhan
DROP TRIGGER trg_tao_box_chat_khi_them_phan_anh ON PhanAnh
DROP TRIGGER trg_cap_nhat_trang_thai_phan_anh ON TinNhan
ALTER TABLE TinNhan
DROP Constraint tinnhan_matepdinhkem_fkey;


-- Xóa Proc liên quan bảng TinNhan
DROP PROCEDURE IF EXISTS sp_ThemPhanAnh
DROP PROCEDURE sp_ThemTinNhan

-- Xóa constaint bảng BoxChat
ALTER TABLE BOXCHAT
DROP Constraint boxchat_maphananh_fkey;

ALTER TABLE BOXCHAT
DROP Constraint boxchat_cccd_canbo_fkey;

ALTER TABLE BOXCHAT
DROP Constraint boxchat_cccd_nguoidan_fkey;
