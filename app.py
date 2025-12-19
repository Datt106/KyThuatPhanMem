"""
Ứng dụng Quản lý Dân cư Tổ dân phố
Backend: Flask + PostgreSQL (psycopg2)
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash
import psycopg2
from psycopg2 import Error
from functools import wraps
import os

# ========== KHỞI TẠO FLASK APP ==========
app = Flask(__name__, 
            template_folder='Interface/templates',
            static_folder='Interface/static')

app.secret_key = 'quanlydancu_secret_key_2025'

# ========== CẤU HÌNH DATABASE ==========
DB_CONFIG = {
    'database': 'QuanLyPhanAnh',
    'user': 'postgres',
    'password': '271205',
    'host': 'localhost',
    'port': '5432'
}


# ========== HÀM KẾT NỐI DATABASE ==========
def get_db_connection():
    """
    Tạo kết nối đến PostgreSQL database
    Returns: connection object hoặc None nếu lỗi
    """
    try:
        connection = psycopg2.connect(
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port']
        )
        return connection
    except Error as e:
        print(f"Lỗi kết nối database: {e}")
        return None


def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    """
    Thực thi câu lệnh SQL
    Args:
        query: Câu lệnh SQL
        params: Tham số truyền vào (tuple)
        fetch_one: Lấy 1 bản ghi
        fetch_all: Lấy tất cả bản ghi
    Returns: Kết quả query hoặc None
    """
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor()
        cursor.execute(query, params)
        
        if fetch_one:
            result = cursor.fetchone()
        elif fetch_all:
            result = cursor.fetchall()
        else:
            connection.commit()
            result = cursor.rowcount
        
        cursor.close()
        connection.close()
        return result
    
    except Error as e:
        print(f"Lỗi thực thi query: {e}")
        if connection:
            connection.rollback()
            connection.close()
        return None


# ========== DECORATOR KIỂM TRA ĐĂNG NHẬP ==========
def login_required(f):
    """Decorator yêu cầu đăng nhập"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Vui lòng đăng nhập để truy cập!', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ========== ROUTES ==========

@app.route('/')
def index():
    """Trang chủ - Redirect đến login hoặc dashboard"""
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Trang đăng nhập bằng CCCD và mật khẩu"""
    if request.method == 'POST':
        cccd = request.form.get('cccd', '').strip()
        password = request.form.get('password', '').strip()
        
        if not cccd or not password:
            flash('Vui lòng nhập đầy đủ thông tin!', 'danger')
            return render_template('login.html')
        
        # Query kiểm tra đăng nhập bằng CCCD
        query = """
            SELECT cccd, name, vaitro, user_name 
            FROM nguoidung 
            WHERE cccd = %s AND matkhau = %s
        """
        user = execute_query(query, (cccd, password), fetch_one=True)
        
        if user:
            session['user'] = {
                'cccd': user[0].strip() if user[0] else '',
                'name': user[1],
                'vaitro': user[2],
                'user_name': user[3]
            }
            flash(f'Chào mừng {user[1]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('CCCD hoặc mật khẩu không đúng!', 'danger')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Đăng xuất"""
    session.pop('user', None)
    flash('Đã đăng xuất thành công!', 'info')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Trang Dashboard - Thống kê và danh sách hộ khẩu"""
    
    # Thống kê tổng số nhân khẩu
    query_nhankhau = "SELECT COUNT(*) FROM nguoidung"
    total_nhankhau = execute_query(query_nhankhau, fetch_one=True)
    total_nhankhau = total_nhankhau[0] if total_nhankhau else 0
    
    # Thống kê tổng số hộ khẩu
    query_hokhau = "SELECT COUNT(*) FROM hokhau"
    total_hokhau = execute_query(query_hokhau, fetch_one=True)
    total_hokhau = total_hokhau[0] if total_hokhau else 0
    
    # Thống kê tổng số phản ánh
    query_phananh = "SELECT COUNT(*) FROM phananh"
    total_phananh = execute_query(query_phananh, fetch_one=True)
    total_phananh = total_phananh[0] if total_phananh else 0
    
    # Thống kê phản ánh chưa xử lý
    query_chuaxuly = "SELECT COUNT(*) FROM phananh WHERE trangthaiphananh = 'ChuaXuLy'"
    total_chuaxuly = execute_query(query_chuaxuly, fetch_one=True)
    total_chuaxuly = total_chuaxuly[0] if total_chuaxuly else 0
    
    # Danh sách hộ khẩu với địa chỉ
    query_dshokhau = """
        SELECT 
            h.mahokhau,
            d.tinh,
            d.xaphuong,
            d.chitiet,
            h.ngaycap,
            h.ghichu,
            (SELECT COUNT(*) FROM thanhvienhokhau tv WHERE tv.mahokhau = h.mahokhau) as so_thanh_vien
        FROM hokhau h
        LEFT JOIN diachi d ON h.madiachi = d.madiachi
        ORDER BY h.mahokhau DESC
        LIMIT 50
    """
    ds_hokhau = execute_query(query_dshokhau, fetch_all=True)
    ds_hokhau = ds_hokhau if ds_hokhau else []
    
    return render_template('dashboard.html',
                         total_nhankhau=total_nhankhau,
                         total_hokhau=total_hokhau,
                         total_phananh=total_phananh,
                         total_chuaxuly=total_chuaxuly,
                         ds_hokhau=ds_hokhau)


@app.route('/hokhau')
@login_required
def hokhau_list():
    """Danh sách hộ khẩu chi tiết"""
    
    query = """
        SELECT 
            h.mahokhau,
            d.tinh,
            d.xaphuong,
            d.chitiet,
            h.ngaycap,
            h.ghichu,
            (SELECT COUNT(*) FROM thanhvienhokhau tv WHERE tv.mahokhau = h.mahokhau) as so_thanh_vien,
            (SELECT n.name FROM thanhvienhokhau tv 
             JOIN nguoidung n ON tv.cccd = n.cccd 
             WHERE tv.mahokhau = h.mahokhau AND tv.quanhechuho = 'Chủ hộ' LIMIT 1) as chu_ho
        FROM hokhau h
        LEFT JOIN diachi d ON h.madiachi = d.madiachi
        ORDER BY h.mahokhau DESC
    """
    ds_hokhau = execute_query(query, fetch_all=True)
    ds_hokhau = ds_hokhau if ds_hokhau else []
    
    return render_template('hokhau.html', ds_hokhau=ds_hokhau)


@app.route('/hokhau/<int:mahokhau>')
@login_required
def hokhau_detail(mahokhau):
    """Chi tiết một hộ khẩu"""
    
    # Thông tin hộ khẩu
    query_hokhau = """
        SELECT 
            h.mahokhau,
            d.tinh,
            d.xaphuong,
            d.chitiet,
            h.ngaycap,
            h.ghichu
        FROM hokhau h
        LEFT JOIN diachi d ON h.madiachi = d.madiachi
        WHERE h.mahokhau = %s
    """
    hokhau = execute_query(query_hokhau, (mahokhau,), fetch_one=True)
    
    if not hokhau:
        flash('Không tìm thấy hộ khẩu!', 'danger')
        return redirect(url_for('hokhau_list'))
    
    # Danh sách thành viên
    query_thanhvien = """
        SELECT 
            n.cccd,
            n.name,
            n.ngaysinh,
            n.gioitinh,
            n.dantoc,
            n.sdt,
            tv.quanhechuho,
            tv.ngaybatdau
        FROM thanhvienhokhau tv
        JOIN nguoidung n ON tv.cccd = n.cccd
        WHERE tv.mahokhau = %s
        ORDER BY 
            CASE WHEN tv.quanhechuho = 'Chủ hộ' THEN 0 ELSE 1 END,
            tv.ngaybatdau
    """
    thanhvien = execute_query(query_thanhvien, (mahokhau,), fetch_all=True)
    thanhvien = thanhvien if thanhvien else []
    
    return render_template('hokhau_detail.html', hokhau=hokhau, thanhvien=thanhvien)


@app.route('/nguoidung')
@login_required  
def nguoidung_list():
    """Danh sách người dùng/nhân khẩu"""
    
    query = """
        SELECT 
            cccd,
            name,
            sdt,
            ngaysinh,
            gioitinh,
            dantoc,
            vaitro
        FROM nguoidung
        ORDER BY name
    """
    ds_nguoidung = execute_query(query, fetch_all=True)
    ds_nguoidung = ds_nguoidung if ds_nguoidung else []
    
    return render_template('nguoidung.html', ds_nguoidung=ds_nguoidung)


@app.route('/phananh')
@login_required
def phananh_list():
    """Danh sách phản ánh"""
    
    query = """
        SELECT 
            p.maphananh,
            n.name as nguoiphan,
            p.loaiphananh,
            p.trangthaiphananh,
            p.mota,
            d.tinh,
            d.xaphuong,
            d.chitiet
        FROM phananh p
        LEFT JOIN nguoidung n ON p.cccd = n.cccd
        LEFT JOIN diachi d ON p.madiachi = d.madiachi
        ORDER BY p.maphananh DESC
    """
    ds_phananh = execute_query(query, fetch_all=True)
    ds_phananh = ds_phananh if ds_phananh else []
    
    return render_template('phananh.html', ds_phananh=ds_phananh)


# ========== CHẠY ỨNG DỤNG ==========
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
