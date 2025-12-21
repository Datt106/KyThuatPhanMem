"""
Ứng dụng Quản lý Dân cư Tổ dân phố
Backend: Flask + PostgreSQL (psycopg2)
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
import psycopg2
from psycopg2 import Error
from functools import wraps
import os
from datetime import datetime
from io import BytesIO
try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

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
    """Trang Dashboard - Thống kê và danh sách hộ khẩu với phân trang"""
    
    # ========== CẤU HÌNH PHÂN TRANG ==========
    per_page = 20  # Số bản ghi mỗi trang
    
    # Lấy số trang từ URL, mặc định là 1
    try:
        page = int(request.args.get('page', 1))
        if page < 1:
            page = 1
    except (ValueError, TypeError):
        page = 1
    
    # Tính offset
    offset = (page - 1) * per_page
    
    # ========== THỐNG KÊ ==========
    # Thống kê tổng số nhân khẩu
    query_nhankhau = "SELECT COUNT(*) FROM nguoidung"
    total_nhankhau = execute_query(query_nhankhau, fetch_one=True)
    total_nhankhau = total_nhankhau[0] if total_nhankhau else 0
    
    # Thống kê tổng số hộ khẩu (dùng cho pagination)
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
    
    # ========== PHÂN TRANG DANH SÁCH HỘ KHẨU ==========
    # Tính tổng số trang
    import math
    total_pages = math.ceil(total_hokhau / per_page) if total_hokhau > 0 else 1
    
    # Đảm bảo page không vượt quá total_pages
    if page > total_pages:
        page = total_pages
    
    # Query danh sách hộ khẩu với LIMIT và OFFSET
    query_dshokhau = """
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
             WHERE tv.mahokhau = h.mahokhau AND tv.quanhechuho = 'ChuHo' LIMIT 1) as chu_ho
        FROM hokhau h
        LEFT JOIN diachi d ON h.madiachi = d.madiachi
        ORDER BY h.mahokhau DESC
        LIMIT %s OFFSET %s
    """
    ds_hokhau = execute_query(query_dshokhau, (per_page, offset), fetch_all=True)
    ds_hokhau = ds_hokhau if ds_hokhau else []
    
    return render_template('dashboard.html',
                         total_nhankhau=total_nhankhau,
                         total_hokhau=total_hokhau,
                         total_phananh=total_phananh,
                         total_chuaxuly=total_chuaxuly,
                         ds_hokhau=ds_hokhau,
                         page=page,
                         per_page=per_page,
                         total_pages=total_pages)


@app.route('/hokhau')
@login_required
def hokhau_list():
    """Danh sách hộ khẩu chi tiết với phân trang, tìm kiếm và lọc"""
    
    # ========== CẤU HÌNH PHÂN TRANG ==========
    per_page = 20  # Số bản ghi mỗi trang
    
    # Lấy số trang từ URL, mặc định là 1
    try:
        page = int(request.args.get('page', 1))
        if page < 1:
            page = 1
    except (ValueError, TypeError):
        page = 1
    
    # Tính offset
    offset = (page - 1) * per_page
    
    # ========== LẤY THAM SỐ TÌM KIẾM VÀ LỌC ==========
    search = request.args.get('search', '').strip()
    xaphuong = request.args.get('xaphuong', '').strip()
    
    # ========== XÂY DỰNG ĐIỀU KIỆN WHERE ==========
    where_conditions = []
    params = []
    
    if search:
        where_conditions.append("(CAST(h.mahokhau AS TEXT) LIKE %s OR d.chitiet ILIKE %s OR d.xaphuong ILIKE %s)")
        search_pattern = f"%{search}%"
        params.extend([search_pattern, search_pattern, search_pattern])
    
    if xaphuong:
        where_conditions.append("d.xaphuong ILIKE %s")
        params.append(f"%{xaphuong}%")
    
    where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
    
    # ========== ĐẾM TỔNG SỐ HỘ KHẨU ==========
    query_count = f"""
        SELECT COUNT(*) 
        FROM hokhau h
        LEFT JOIN diachi d ON h.madiachi = d.madiachi
        WHERE {where_clause}
    """
    total_count = execute_query(query_count, tuple(params), fetch_one=True)
    total_count = total_count[0] if total_count else 0
    
    # Tính tổng số trang
    import math
    total_pages = math.ceil(total_count / per_page) if total_count > 0 else 1
    
    # Đảm bảo page không vượt quá total_pages
    if page > total_pages and total_pages > 0:
        page = total_pages
    
    # ========== QUERY DANH SÁCH HỘ KHẨU VỚI PHÂN TRANG ==========
    query = f"""
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
             WHERE tv.mahokhau = h.mahokhau AND tv.quanhechuho = 'ChuHo' LIMIT 1) as chu_ho
        FROM hokhau h
        LEFT JOIN diachi d ON h.madiachi = d.madiachi
        WHERE {where_clause}
        ORDER BY h.mahokhau DESC
        LIMIT %s OFFSET %s
    """
    params.extend([per_page, offset])
    ds_hokhau = execute_query(query, tuple(params), fetch_all=True)
    ds_hokhau = ds_hokhau if ds_hokhau else []
    
    return render_template('hokhau.html', 
                         ds_hokhau=ds_hokhau,
                         page=page,
                         per_page=per_page,
                         total_pages=total_pages,
                         total_count=total_count,
                         search=search,
                         xaphuong=xaphuong)


@app.route('/hokhau/add', methods=['GET', 'POST'])
@login_required
def hokhau_add():
    """Thêm hộ khẩu mới"""
    
    if request.method == 'POST':
        # Lấy thông tin địa chỉ
        xaphuong = request.form.get('xaphuong', '').strip()
        diachichitiet = request.form.get('diachichitiet', '').strip()
        ghichu = request.form.get('ghichu', '').strip()
        
        # Lấy thông tin chủ hộ và thành viên
        chuho_cccd = request.form.get('chuho_cccd', '').strip()
        member_cccd_list = request.form.getlist('member_cccd[]')
        member_quanhe_list = request.form.getlist('member_quanhe[]')
        
        # Validate
        if not xaphuong or not diachichitiet:
            flash('Vui lòng nhập đầy đủ thông tin địa chỉ (Xã/Phường và Địa chỉ chi tiết)!', 'danger')
            return render_template('hokhau_add.html')
        
        if not chuho_cccd:
            flash('Vui lòng nhập CCCD chủ hộ!', 'danger')
            return render_template('hokhau_add.html')
        
        # Kiểm tra CCCD chủ hộ có tồn tại không
        check_chuho = "SELECT cccd, name FROM nguoidung WHERE cccd = %s"
        nguoi_chuho = execute_query(check_chuho, (chuho_cccd,), fetch_one=True)
        if not nguoi_chuho:
            flash(f'CCCD chủ hộ "{chuho_cccd}" không tồn tại trong hệ thống!', 'danger')
            return render_template('hokhau_add.html')
        
        # Kiểm tra các CCCD thành viên có tồn tại không
        valid_members = []
        for i, cccd_tv in enumerate(member_cccd_list):
            cccd_tv = cccd_tv.strip()
            if cccd_tv:  # Nếu có nhập CCCD
                if cccd_tv == chuho_cccd:
                    flash(f'Chủ hộ không thể là thành viên khác!', 'danger')
                    return render_template('hokhau_add.html')
                
                # Kiểm tra CCCD có tồn tại
                check_member = "SELECT cccd, name FROM nguoidung WHERE cccd = %s"
                nguoi_tv = execute_query(check_member, (cccd_tv,), fetch_one=True)
                if not nguoi_tv:
                    flash(f'CCCD thành viên "{cccd_tv}" không tồn tại trong hệ thống!', 'danger')
                    return render_template('hokhau_add.html')
                
                quanhe = member_quanhe_list[i] if i < len(member_quanhe_list) else 'Khac'
                if not quanhe:
                    flash(f'Vui lòng chọn quan hệ cho thành viên "{nguoi_tv[1]}"!', 'danger')
                    return render_template('hokhau_add.html')
                
                valid_members.append((cccd_tv, quanhe))
        
        # Bước 1: Insert địa chỉ
        insert_diachi = """
            INSERT INTO diachi (tinh, xaphuong, chitiet)
            VALUES (%s, %s, %s)
            RETURNING madiachi
        """
        connection = get_db_connection()
        if not connection:
            flash('Lỗi kết nối database!', 'danger')
            return render_template('hokhau_add.html')
        
        try:
            cursor = connection.cursor()
            
            # Insert địa chỉ
            cursor.execute(insert_diachi, ('Hà Nội', xaphuong, diachichitiet))
            madiachi = cursor.fetchone()[0]
            
            # Bước 2: Insert hộ khẩu
            insert_hokhau = """
                INSERT INTO hokhau (madiachi, ghichu)
                VALUES (%s, %s)
                RETURNING mahokhau
            """
            cursor.execute(insert_hokhau, (madiachi, ghichu or None))
            mahokhau = cursor.fetchone()[0]
            
            # Bước 3: Insert chủ hộ
            insert_chuho = """
                INSERT INTO thanhvienhokhau (mahokhau, cccd, quanhechuho, ngaybatdau)
                VALUES (%s, %s, %s, CURRENT_DATE)
            """
            cursor.execute(insert_chuho, (mahokhau, chuho_cccd, 'ChuHo'))
            
            # Bước 4: Insert thành viên khác (nếu có)
            for cccd_tv, quanhe in valid_members:
                insert_thanhvien = """
                    INSERT INTO thanhvienhokhau (mahokhau, cccd, quanhechuho, ngaybatdau)
                    VALUES (%s, %s, %s, CURRENT_DATE)
                """
                cursor.execute(insert_thanhvien, (mahokhau, cccd_tv, quanhe))
            
            connection.commit()
            cursor.close()
            connection.close()
            
            flash(f'Đã thêm hộ khẩu HK{mahokhau} (Chủ hộ: {nguoi_chuho[1]}) thành công!', 'success')
            return redirect(url_for('hokhau_detail', mahokhau=mahokhau))
            
        except Error as e:
            if connection:
                connection.rollback()
                connection.close()
            flash(f'Có lỗi xảy ra: {str(e)}', 'danger')
            return render_template('hokhau_add.html')
    
    return render_template('hokhau_add.html')


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
            CASE WHEN tv.quanhechuho = 'ChuHo' THEN 0 ELSE 1 END,
            tv.ngaybatdau
    """
    thanhvien = execute_query(query_thanhvien, (mahokhau,), fetch_all=True)
    thanhvien = thanhvien if thanhvien else []
    
    return render_template('hokhau_detail.html', hokhau=hokhau, thanhvien=thanhvien)


@app.route('/hokhau/edit/<int:mahokhau>', methods=['GET', 'POST'])
@login_required
def hokhau_edit(mahokhau):
    """Sửa thông tin hộ khẩu"""
    
    if request.method == 'POST':
        # Lấy dữ liệu từ form
        xaphuong = request.form.get('xaphuong', '').strip()
        chitiet = request.form.get('chitiet', '').strip()
        ghichu = request.form.get('ghichu', '').strip()
        
        # Validate
        if not xaphuong or not chitiet:
            flash('Vui lòng nhập đầy đủ thông tin xã/phường và địa chỉ chi tiết!', 'danger')
            return redirect(url_for('hokhau_edit', mahokhau=mahokhau))
        
        # Lấy madiachi của hộ khẩu
        query_madiachi = "SELECT madiachi FROM hokhau WHERE mahokhau = %s"
        result = execute_query(query_madiachi, (mahokhau,), fetch_one=True)
        
        if not result:
            flash('Không tìm thấy hộ khẩu!', 'danger')
            return redirect(url_for('hokhau_list'))
        
        madiachi = result[0]
        
        # Update địa chỉ
        update_diachi = """
            UPDATE diachi 
            SET xaphuong = %s, chitiet = %s
            WHERE madiachi = %s
        """
        execute_query(update_diachi, (xaphuong, chitiet, madiachi))
        
        # Update ghi chú hộ khẩu
        update_hokhau = """
            UPDATE hokhau 
            SET ghichu = %s
            WHERE mahokhau = %s
        """
        result = execute_query(update_hokhau, (ghichu or None, mahokhau))
        
        if result:
            flash('Đã cập nhật thông tin hộ khẩu thành công!', 'success')
            return redirect(url_for('hokhau_detail', mahokhau=mahokhau))
        else:
            flash('Có lỗi xảy ra khi cập nhật!', 'danger')
    
    # GET: Load dữ liệu hiện tại
    query = """
        SELECT 
            h.mahokhau,
            d.tinh,
            d.xaphuong,
            d.chitiet,
            h.ngaycap,
            h.ghichu,
            d.madiachi
        FROM hokhau h
        LEFT JOIN diachi d ON h.madiachi = d.madiachi
        WHERE h.mahokhau = %s
    """
    hokhau = execute_query(query, (mahokhau,), fetch_one=True)
    
    if not hokhau:
        flash('Không tìm thấy hộ khẩu!', 'danger')
        return redirect(url_for('hokhau_list'))
    
    # Lấy danh sách thành viên
    query_thanhvien = """
        SELECT 
            n.cccd,
            n.name,
            n.ngaysinh,
            tv.quanhechuho
        FROM thanhvienhokhau tv
        JOIN nguoidung n ON tv.cccd = n.cccd
        WHERE tv.mahokhau = %s AND tv.ngayketthuc IS NULL
        ORDER BY 
            CASE WHEN tv.quanhechuho = 'ChuHo' THEN 0 ELSE 1 END,
            tv.ngaybatdau
    """
    thanhvien = execute_query(query_thanhvien, (mahokhau,), fetch_all=True)
    thanhvien = thanhvien if thanhvien else []
    
    return render_template('hokhau_edit.html', hokhau=hokhau, thanhvien=thanhvien)


@app.route('/hokhau/delete/<int:mahokhau>', methods=['POST'])
@login_required
def hokhau_delete(mahokhau):
    """Xóa hộ khẩu"""
    
    # Lấy thông tin để hiển thị
    query_info = """
        SELECT h.mahokhau, d.chitiet, d.madiachi
        FROM hokhau h
        LEFT JOIN diachi d ON h.madiachi = d.madiachi
        WHERE h.mahokhau = %s
    """
    hokhau_info = execute_query(query_info, (mahokhau,), fetch_one=True)
    
    if not hokhau_info:
        flash('Không tìm thấy hộ khẩu!', 'danger')
        return redirect(url_for('hokhau_list'))
    
    madiachi = hokhau_info[2]
    
    # Xóa theo thứ tự: thanhvienhokhau -> hokhau -> diachi
    connection = get_db_connection()
    if not connection:
        flash('Lỗi kết nối database!', 'danger')
        return redirect(url_for('hokhau_list'))
    
    try:
        cursor = connection.cursor()
        
        # Xóa thành viên hộ khẩu
        cursor.execute("DELETE FROM thanhvienhokhau WHERE mahokhau = %s", (mahokhau,))
        
        # Xóa hộ khẩu
        cursor.execute("DELETE FROM hokhau WHERE mahokhau = %s", (mahokhau,))
        
        # Xóa địa chỉ
        if madiachi:
            cursor.execute("DELETE FROM diachi WHERE madiachi = %s", (madiachi,))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        flash(f'Đã xóa hộ khẩu HK{mahokhau} thành công!', 'success')
        
    except Error as e:
        if connection:
            connection.rollback()
            connection.close()
        flash(f'Có lỗi xảy ra: {str(e)}', 'danger')
    
    return redirect(url_for('hokhau_list'))


@app.route('/thanhvien/chuyen-di/<int:mahokhau>/<string:cccd>', methods=['GET', 'POST'])
@login_required
def thanhvien_chuyen_di(mahokhau, cccd):
    """Chuyển đi/Qua đời thành viên"""
    
    if request.method == 'POST':
        ngaychuyen = request.form.get('ngaychuyen')
        lydochuyen = request.form.get('lydochuyen')
        noichuyenden = request.form.get('noichuyenden')
        ghichu = request.form.get('ghichu')
        
        try:
            # Update ngayketthuc trong thanhvienhokhau
            query = """
                UPDATE thanhvienhokhau 
                SET ngayketthuc = %s,
                    lydochuyen = %s,
                    noichuyenden = %s,
                    ghichu = %s
                WHERE mahokhau = %s AND cccd = %s AND ngayketthuc IS NULL
            """
            execute_query(query, (ngaychuyen, lydochuyen, noichuyenden, ghichu, mahokhau, cccd.strip()))
            
            flash(f'Đã cập nhật thông tin chuyển đi cho thành viên {cccd}!', 'success')
            return redirect(url_for('hokhau_detail', mahokhau=mahokhau))
        except Exception as e:
            flash(f'Lỗi khi cập nhật: {str(e)}', 'danger')
    
    # GET - Load thông tin thành viên
    query = """
        SELECT n.cccd, n.name, n.ngaysinh, tv.quanhechuho, tv.ngaybatdau
        FROM nguoidung n
        JOIN thanhvienhokhau tv ON n.cccd = tv.cccd
        WHERE tv.mahokhau = %s AND n.cccd = %s AND tv.ngayketthuc IS NULL
    """
    thanhvien = execute_query(query, (mahokhau, cccd.strip()), fetch_one=True)
    
    if not thanhvien:
        flash('Không tìm thấy thành viên trong hộ khẩu!', 'danger')
        return redirect(url_for('hokhau_detail', mahokhau=mahokhau))
    
    # Lấy thông tin hộ khẩu
    query_hk = """
        SELECT hk.mahokhau, hk.ghichu, dc.chitiet, dc.xaphuong
        FROM hokhau hk
        LEFT JOIN diachi dc ON hk.madiachi = dc.madiachi
        WHERE hk.mahokhau = %s
    """
    hokhau = execute_query(query_hk, (mahokhau,), fetch_one=True)
    
    from datetime import datetime
    return render_template('thanhvien_chuyen_di.html', 
                         thanhvien=thanhvien, 
                         hokhau=hokhau, 
                         mahokhau=mahokhau,
                         now=datetime.now())


@app.route('/hokhau/doi-chu-ho/<int:mahokhau>', methods=['GET', 'POST'])
@login_required
def hokhau_doi_chu_ho(mahokhau):
    """Thay đổi chủ hộ"""
    
    if request.method == 'POST':
        cccd_moi = request.form.get('cccd_moi')
        ngaythaydoi = request.form.get('ngaythaydoi')
        lydothaydoi = request.form.get('lydothaydoi')
        noidung = request.form.get('noidung')
        
        try:
            # Lấy thông tin chủ hộ hiện tại
            query_chuho_cu = """
                SELECT cccd FROM thanhvienhokhau 
                WHERE mahokhau = %s AND quanhechuho = 'Chủ hộ' AND ngayketthuc IS NULL
            """
            chuho_cu = execute_query(query_chuho_cu, (mahokhau,), fetch_one=True)
            
            if not chuho_cu:
                flash('Không tìm thấy chủ hộ hiện tại!', 'danger')
                return redirect(url_for('hokhau_detail', mahokhau=mahokhau))
            
            cccd_cu = chuho_cu[0].strip()
            cccd_moi = cccd_moi.strip()
            
            if cccd_cu == cccd_moi:
                flash('Chủ hộ mới phải khác chủ hộ hiện tại!', 'warning')
                return redirect(url_for('hokhau_doi_chu_ho', mahokhau=mahokhau))
            
            connection = get_db_connection()
            cursor = connection.cursor()
            
            # 1. Cập nhật quan hệ của chủ hộ cũ thành thành viên
            cursor.execute("""
                UPDATE thanhvienhokhau 
                SET quanhechuho = 'Thành viên'
                WHERE mahokhau = %s AND cccd = %s AND ngayketthuc IS NULL
            """, (mahokhau, cccd_cu))
            
            # 2. Cập nhật quan hệ của chủ hộ mới
            cursor.execute("""
                UPDATE thanhvienhokhau 
                SET quanhechuho = 'Chủ hộ'
                WHERE mahokhau = %s AND cccd = %s AND ngayketthuc IS NULL
            """, (mahokhau, cccd_moi))
            
            # 3. Lưu lịch sử thay đổi
            nguoithuchien = session.get('username', 'system')
            cursor.execute("""
                INSERT INTO lichsuthaydoichuho 
                (mahokhau, cccd_cu, cccd_moi, ngaythaydoi, lydothaydoi, noidung, nguoithuchien)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (mahokhau, cccd_cu, cccd_moi, ngaythaydoi, lydothaydoi, noidung, nguoithuchien))
            
            connection.commit()
            cursor.close()
            connection.close()
            
            flash(f'Đã thay đổi chủ hộ thành công!', 'success')
            return redirect(url_for('hokhau_detail', mahokhau=mahokhau))
            
        except Exception as e:
            if connection:
                connection.rollback()
                connection.close()
            flash(f'Lỗi khi thay đổi chủ hộ: {str(e)}', 'danger')
    
    # GET - Load thông tin hộ khẩu và danh sách thành viên
    query_hk = """
        SELECT hk.mahokhau, hk.ghichu, dc.chitiet, dc.xaphuong
        FROM hokhau hk
        LEFT JOIN diachi dc ON hk.madiachi = dc.madiachi
        WHERE hk.mahokhau = %s
    """
    hokhau = execute_query(query_hk, (mahokhau,), fetch_one=True)
    
    if not hokhau:
        flash('Không tìm thấy hộ khẩu!', 'danger')
        return redirect(url_for('hokhau_list'))
    
    # Lấy danh sách thành viên (bao gồm cả chủ hộ hiện tại)
    query_thanhvien = """
        SELECT 
            n.cccd,
            n.name,
            n.ngaysinh,
            n.gioitinh,
            tv.quanhechuho,
            tv.ngaybatdau
        FROM thanhvienhokhau tv
        JOIN nguoidung n ON tv.cccd = n.cccd
        WHERE tv.mahokhau = %s AND tv.ngayketthuc IS NULL
        ORDER BY 
            CASE WHEN tv.quanhechuho = 'Chủ hộ' THEN 0 ELSE 1 END,
            tv.ngaybatdau
    """
    thanhvien = execute_query(query_thanhvien, (mahokhau,), fetch_all=True)
    
    from datetime import datetime
    return render_template('hokhau_doi_chu_ho.html', 
                         hokhau=hokhau, 
                         thanhvien=thanhvien,
                         mahokhau=mahokhau,
                         now=datetime.now())


@app.route('/hokhau/tach-ho/<int:mahokhau>', methods=['GET', 'POST'])
@login_required
def hokhau_tach_ho(mahokhau):
    """Tách hộ khẩu - tạo hộ mới từ hộ hiện tại"""
    
    if request.method == 'POST':
        thanhvien_tach = request.form.getlist('thanhvien_tach')  # List of CCCD
        cccd_chuho_moi = request.form.get('cccd_chuho_moi')
        ngaytach = request.form.get('ngaytach')
        
        # Thông tin địa chỉ mới
        xaphuong_moi = request.form.get('xaphuong_moi')
        chitiet_moi = request.form.get('chitiet_moi')
        ghichu_moi = request.form.get('ghichu_moi')
        lydotach = request.form.get('lydotach')
        
        # Validation
        if not thanhvien_tach or len(thanhvien_tach) == 0:
            flash('Vui lòng chọn ít nhất 1 thành viên để tách!', 'warning')
            return redirect(url_for('hokhau_tach_ho', mahokhau=mahokhau))
        
        if cccd_chuho_moi not in thanhvien_tach:
            flash('Chủ hộ mới phải nằm trong danh sách thành viên được tách!', 'warning')
            return redirect(url_for('hokhau_tach_ho', mahokhau=mahokhau))
        
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            
            # 1. Tạo địa chỉ mới
            cursor.execute("""
                INSERT INTO diachi (xaphuong, chitiet)
                VALUES (%s, %s)
                RETURNING madiachi
            """, (xaphuong_moi, chitiet_moi))
            madiachi_moi = cursor.fetchone()[0]
            
            # 2. Tạo hộ khẩu mới
            cursor.execute("""
                INSERT INTO hokhau (madiachi, ghichu)
                VALUES (%s, %s)
                RETURNING mahokhau
            """, (madiachi_moi, ghichu_moi or f'Tách từ HK{mahokhau}. Lý do: {lydotach}'))
            mahokhau_moi = cursor.fetchone()[0]
            
            # 3. Cập nhật ngayketthuc cho các thành viên tách ra trong hộ cũ
            for cccd in thanhvien_tach:
                cccd = cccd.strip()
                cursor.execute("""
                    UPDATE thanhvienhokhau
                    SET ngayketthuc = %s,
                        lydochuyen = %s,
                        ghichu = %s
                    WHERE mahokhau = %s AND cccd = %s AND ngayketthuc IS NULL
                """, (ngaytach, 'Tách hộ', f'Tách sang HK{mahokhau_moi}', mahokhau, cccd))
            
            # 4. Thêm các thành viên vào hộ mới
            for cccd in thanhvien_tach:
                cccd = cccd.strip()
                quanhe = 'Chủ hộ' if cccd == cccd_chuho_moi.strip() else 'Thành viên'
                
                cursor.execute("""
                    INSERT INTO thanhvienhokhau (mahokhau, cccd, quanhechuho, ngaybatdau)
                    VALUES (%s, %s, %s, %s)
                """, (mahokhau_moi, cccd, quanhe, ngaytach))
            
            connection.commit()
            cursor.close()
            connection.close()
            
            flash(f'Tách hộ thành công! Hộ khẩu mới: HK{mahokhau_moi}', 'success')
            return redirect(url_for('hokhau_detail', mahokhau=mahokhau_moi))
            
        except Exception as e:
            if connection:
                connection.rollback()
                connection.close()
            flash(f'Lỗi khi tách hộ: {str(e)}', 'danger')
            return redirect(url_for('hokhau_tach_ho', mahokhau=mahokhau))
    
    # GET - Load thông tin hộ khẩu và danh sách thành viên
    query_hk = """
        SELECT hk.mahokhau, hk.ghichu, dc.chitiet, dc.xaphuong
        FROM hokhau hk
        LEFT JOIN diachi dc ON hk.madiachi = dc.madiachi
        WHERE hk.mahokhau = %s
    """
    hokhau = execute_query(query_hk, (mahokhau,), fetch_one=True)
    
    if not hokhau:
        flash('Không tìm thấy hộ khẩu!', 'danger')
        return redirect(url_for('hokhau_list'))
    
    # Lấy danh sách thành viên (không bao gồm chủ hộ - không cho phép tách chủ hộ)
    query_thanhvien = """
        SELECT 
            n.cccd,
            n.name,
            n.ngaysinh,
            n.gioitinh,
            tv.quanhechuho,
            tv.ngaybatdau
        FROM thanhvienhokhau tv
        JOIN nguoidung n ON tv.cccd = n.cccd
        WHERE tv.mahokhau = %s AND tv.ngayketthuc IS NULL
        ORDER BY 
            CASE WHEN tv.quanhechuho = 'Chủ hộ' THEN 0 ELSE 1 END,
            tv.ngaybatdau
    """
    thanhvien = execute_query(query_thanhvien, (mahokhau,), fetch_all=True)
    
    # Đếm số thành viên (không bao gồm chủ hộ)
    thanhvien_khong_chuho = [tv for tv in thanhvien if tv[4] != 'Chủ hộ']
    
    if len(thanhvien_khong_chuho) == 0:
        flash('Hộ khẩu chỉ có chủ hộ, không thể tách!', 'warning')
        return redirect(url_for('hokhau_detail', mahokhau=mahokhau))
    
    from datetime import datetime
    return render_template('hokhau_tach_ho.html', 
                         hokhau=hokhau, 
                         thanhvien=thanhvien,
                         mahokhau=mahokhau,
                         now=datetime.now())


@app.route('/tam-vang/add', methods=['GET', 'POST'])
@login_required
def tam_vang_add():
    """Cấp giấy tạm vắng"""
    
    if request.method == 'POST':
        cccd = request.form.get('cccd')
        ngaybatdau = request.form.get('ngaybatdau')
        ngayketthuc = request.form.get('ngayketthuc')
        lydo = request.form.get('lydo')
        noiden = request.form.get('noiden')
        
        # Lấy địa chỉ thường trú hiện tại
        query_diachi = """
            SELECT dc.madiachi, dc.xaphuong, dc.chitiet
            FROM diachinguoidung dcnd
            JOIN diachi dc ON dcnd.madiachi = dc.madiachi
            WHERE dcnd.cccd = %s AND dcnd.loaidiachi = 'CuTru' 
            AND dcnd.thoidiemketthuc IS NULL
            LIMIT 1
        """
        diachi_cutru = execute_query(query_diachi, (cccd.strip(),), fetch_one=True)
        
        if not diachi_cutru:
            flash('Không tìm thấy địa chỉ cư trú của người này!', 'warning')
            return redirect(url_for('tam_vang_add'))
        
        madiachi_cutru = diachi_cutru[0]
        
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            
            # Tạo địa chỉ tạm vắng (nơi đến)
            cursor.execute("""
                INSERT INTO diachi (chitiet, xaphuong)
                VALUES (%s, %s)
                RETURNING madiachi
            """, (noiden or 'Chưa xác định', lydo or 'Chưa rõ'))
            madiachi_tamvang = cursor.fetchone()[0]
            
            # Insert vào diachinguoidung với loaidiachi='TamVang'
            cursor.execute("""
                INSERT INTO diachinguoidung (madiachi, cccd, loaidiachi, thoidiemxacnhan, thoidiemketthuc)
                VALUES (%s, %s, 'TamVang', %s, %s)
            """, (madiachi_tamvang, cccd.strip(), ngaybatdau, ngayketthuc))
            
            connection.commit()
            cursor.close()
            connection.close()
            
            flash(f'Đã cấp giấy tạm vắng thành công cho CCCD {cccd}!', 'success')
            return redirect(url_for('tam_vang_tru_list'))
            
        except Exception as e:
            if connection:
                connection.rollback()
                connection.close()
            flash(f'Lỗi khi cấp giấy tạm vắng: {str(e)}', 'danger')
    
    # GET - Load danh sách người dân để chọn
    query_nguoidung = """
        SELECT cccd, name, ngaysinh, gioitinh
        FROM nguoidung
        ORDER BY name
    """
    nguoidung_list = execute_query(query_nguoidung, fetch_all=True)
    
    from datetime import datetime
    return render_template('tam_vang_add.html', 
                         nguoidung_list=nguoidung_list,
                         now=datetime.now())


@app.route('/tam-tru/add', methods=['GET', 'POST'])
@login_required
def tam_tru_add():
    """Cấp giấy tạm trú"""
    
    if request.method == 'POST':
        cccd = request.form.get('cccd')
        ngaybatdau = request.form.get('ngaybatdau')
        ngayketthuc = request.form.get('ngayketthuc')
        lydo = request.form.get('lydo')
        diachi_tamtru = request.form.get('diachi_tamtru')
        xaphuong = request.form.get('xaphuong')
        
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            
            # Tạo địa chỉ tạm trú
            cursor.execute("""
                INSERT INTO diachi (chitiet, xaphuong)
                VALUES (%s, %s)
                RETURNING madiachi
            """, (diachi_tamtru, xaphuong))
            madiachi_tamtru = cursor.fetchone()[0]
            
            # Insert vào diachinguoidung với loaidiachi='TamTru'
            cursor.execute("""
                INSERT INTO diachinguoidung (madiachi, cccd, loaidiachi, thoidiemxacnhan, thoidiemketthuc)
                VALUES (%s, %s, 'TamTru', %s, %s)
            """, (madiachi_tamtru, cccd.strip(), ngaybatdau, ngayketthuc))
            
            connection.commit()
            cursor.close()
            connection.close()
            
            flash(f'Đã cấp giấy tạm trú thành công cho CCCD {cccd}!', 'success')
            return redirect(url_for('tam_vang_tru_list'))
            
        except Exception as e:
            if connection:
                connection.rollback()
                connection.close()
            flash(f'Lỗi khi cấp giấy tạm trú: {str(e)}', 'danger')
    
    # GET - Load danh sách người dân
    query_nguoidung = """
        SELECT cccd, name, ngaysinh, gioitinh
        FROM nguoidung
        ORDER BY name
    """
    nguoidung_list = execute_query(query_nguoidung, fetch_all=True)
    
    from datetime import datetime
    return render_template('tam_tru_add.html', 
                         nguoidung_list=nguoidung_list,
                         now=datetime.now())


@app.route('/tam-vang-tru')
@login_required
def tam_vang_tru_list():
    """Danh sách tạm vắng/tạm trú"""
    
    # Lấy filter params
    loai = request.args.get('loai', '')  # TamVang, TamTru, hoặc tất cả
    xaphuong = request.args.get('xaphuong', '')
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Build query
    query = """
        SELECT 
            n.cccd,
            n.name,
            n.ngaysinh,
            dcnd.loaidiachi,
            dcnd.thoidiemxacnhan,
            dcnd.thoidiemketthuc,
            dc.chitiet,
            dc.xaphuong
        FROM diachinguoidung dcnd
        JOIN nguoidung n ON dcnd.cccd = n.cccd
        JOIN diachi dc ON dcnd.madiachi = dc.madiachi
        WHERE dcnd.loaidiachi IN ('TamVang', 'TamTru')
    """
    
    params = []
    
    if loai:
        query += " AND dcnd.loaidiachi = %s"
        params.append(loai)
    
    if xaphuong:
        query += " AND dc.xaphuong ILIKE %s"
        params.append(f'%{xaphuong}%')
    
    query += " ORDER BY dcnd.thoidiemxacnhan DESC"
    
    # Count total
    count_query = f"SELECT COUNT(*) FROM ({query}) AS subquery"
    total = execute_query(count_query, tuple(params), fetch_one=True)[0]
    
    # Pagination
    offset = (page - 1) * per_page
    query += f" LIMIT {per_page} OFFSET {offset}"
    
    records = execute_query(query, tuple(params), fetch_all=True)
    records = records if records else []
    
    total_pages = (total + per_page - 1) // per_page
    
    return render_template('tam_vang_tru.html',
                         records=records,
                         page=page,
                         total_pages=total_pages,
                         total=total,
                         loai=loai,
                         xaphuong=xaphuong)


@app.route('/hokhau/<int:mahokhau>/lich-su')
@login_required
def hokhau_lich_su(mahokhau):
    """Lịch sử biến động nhân khẩu của hộ"""
    
    # Lấy thông tin hộ khẩu
    query_hk = """
        SELECT hk.mahokhau, hk.ghichu, dc.chitiet, dc.xaphuong, hk.ngaycap
        FROM hokhau hk
        LEFT JOIN diachi dc ON hk.madiachi = dc.madiachi
        WHERE hk.mahokhau = %s
    """
    hokhau = execute_query(query_hk, (mahokhau,), fetch_one=True)
    
    if not hokhau:
        flash('Không tìm thấy hộ khẩu!', 'danger')
        return redirect(url_for('hokhau_list'))
    
    # Lấy thành viên hiện tại
    query_hientai = """
        SELECT 
            n.cccd,
            n.name,
            n.ngaysinh,
            n.gioitinh,
            tv.quanhechuho,
            tv.ngaybatdau
        FROM thanhvienhokhau tv
        JOIN nguoidung n ON tv.cccd = n.cccd
        WHERE tv.mahokhau = %s AND tv.ngayketthuc IS NULL
        ORDER BY 
            CASE WHEN tv.quanhechuho = 'Chủ hộ' THEN 0 ELSE 1 END,
            tv.ngaybatdau
    """
    thanhvien_hientai = execute_query(query_hientai, (mahokhau,), fetch_all=True)
    thanhvien_hientai = thanhvien_hientai if thanhvien_hientai else []
    
    # Lấy lịch sử biến động (người đã rời khỏi hộ)
    query_lichsu = """
        SELECT 
            n.cccd,
            n.name,
            n.ngaysinh,
            tv.quanhechuho,
            tv.ngaybatdau,
            tv.ngayketthuc,
            tv.lydochuyen,
            tv.noichuyenden,
            tv.ghichu
        FROM thanhvienhokhau tv
        JOIN nguoidung n ON tv.cccd = n.cccd
        WHERE tv.mahokhau = %s AND tv.ngayketthuc IS NOT NULL
        ORDER BY tv.ngayketthuc DESC, tv.ngaybatdau DESC
    """
    lichsu = execute_query(query_lichsu, (mahokhau,), fetch_all=True)
    lichsu = lichsu if lichsu else []
    
    # Lấy lịch sử thay đổi chủ hộ
    query_doichuho = """
        SELECT 
            ls.ngaythaydoi,
            n1.name as ten_cu,
            n2.name as ten_moi,
            ls.lydothaydoi,
            ls.noidung,
            ls.nguoithuchien
        FROM lichsuthaydoichuho ls
        LEFT JOIN nguoidung n1 ON ls.cccd_cu = n1.cccd
        LEFT JOIN nguoidung n2 ON ls.cccd_moi = n2.cccd
        WHERE ls.mahokhau = %s
        ORDER BY ls.ngaythaydoi DESC
    """
    lichsu_doichuho = execute_query(query_doichuho, (mahokhau,), fetch_all=True)
    lichsu_doichuho = lichsu_doichuho if lichsu_doichuho else []
    
    return render_template('hokhau_lich_su.html',
                         hokhau=hokhau,
                         thanhvien_hientai=thanhvien_hientai,
                         lichsu=lichsu,
                         lichsu_doichuho=lichsu_doichuho,
                         mahokhau=mahokhau)


@app.route('/thong-ke/dan-so')
@login_required
def thongke_danso():
    """Thống kê dân số theo giới tính, độ tuổi và địa bàn"""
    
    # Lấy tham số filter
    xaphuong = request.args.get('xaphuong', '').strip()
    
    # Query tổng quan
    query_total = """
        SELECT 
            COUNT(DISTINCT n.cccd) as tong,
            COUNT(DISTINCT CASE WHEN n.gioitinh = 'Nam' THEN n.cccd END) as nam,
            COUNT(DISTINCT CASE WHEN n.gioitinh = 'Nữ' THEN n.cccd END) as nu
        FROM nguoidung n
        INNER JOIN thanhvienhokhau tv ON n.cccd = tv.cccd
        INNER JOIN hokhau hk ON tv.mahokhau = hk.mahokhau
        INNER JOIN diachi dc ON hk.madiachi = dc.madiachi
        WHERE tv.ngayketthuc IS NULL
    """
    params = []
    
    if xaphuong:
        query_total += " AND LOWER(dc.xaphuong) LIKE LOWER(%s)"
        params.append(f'%{xaphuong}%')
    
    stats_total = execute_query(query_total, tuple(params) if params else None, fetch_all=False)
    
    # Query phân nhóm tuổi (0-5, 6-10, 11-14, 15-17, 18-59, 60+)
    query_age = """
        SELECT 
            CASE 
                WHEN DATE_PART('year', AGE(CURRENT_DATE, n.ngaysinh)) BETWEEN 0 AND 5 THEN '0-5'
                WHEN DATE_PART('year', AGE(CURRENT_DATE, n.ngaysinh)) BETWEEN 6 AND 10 THEN '6-10'
                WHEN DATE_PART('year', AGE(CURRENT_DATE, n.ngaysinh)) BETWEEN 11 AND 14 THEN '11-14'
                WHEN DATE_PART('year', AGE(CURRENT_DATE, n.ngaysinh)) BETWEEN 15 AND 17 THEN '15-17'
                WHEN DATE_PART('year', AGE(CURRENT_DATE, n.ngaysinh)) BETWEEN 18 AND 59 THEN '18-59'
                ELSE '60+'
            END as nhom_tuoi,
            COUNT(DISTINCT n.cccd) as soluong
        FROM nguoidung n
        INNER JOIN thanhvienhokhau tv ON n.cccd = tv.cccd
        INNER JOIN hokhau hk ON tv.mahokhau = hk.mahokhau
        INNER JOIN diachi dc ON hk.madiachi = dc.madiachi
        WHERE tv.ngayketthuc IS NULL
    """
    
    if xaphuong:
        query_age += " AND LOWER(dc.xaphuong) LIKE LOWER(%s)"
    
    query_age += """
        GROUP BY nhom_tuoi
        ORDER BY 
            CASE nhom_tuoi
                WHEN '0-5' THEN 1
                WHEN '6-10' THEN 2
                WHEN '11-14' THEN 3
                WHEN '15-17' THEN 4
                WHEN '18-59' THEN 5
                WHEN '60+' THEN 6
            END
    """
    
    stats_age = execute_query(query_age, tuple(params) if params else None, fetch_all=True)
    
    # Query phân nhóm tuổi theo giới tính
    query_age_gender = """
        SELECT 
            CASE 
                WHEN DATE_PART('year', AGE(CURRENT_DATE, n.ngaysinh)) BETWEEN 0 AND 5 THEN '0-5'
                WHEN DATE_PART('year', AGE(CURRENT_DATE, n.ngaysinh)) BETWEEN 6 AND 10 THEN '6-10'
                WHEN DATE_PART('year', AGE(CURRENT_DATE, n.ngaysinh)) BETWEEN 11 AND 14 THEN '11-14'
                WHEN DATE_PART('year', AGE(CURRENT_DATE, n.ngaysinh)) BETWEEN 15 AND 17 THEN '15-17'
                WHEN DATE_PART('year', AGE(CURRENT_DATE, n.ngaysinh)) BETWEEN 18 AND 59 THEN '18-59'
                ELSE '60+'
            END as nhom_tuoi,
            n.gioitinh,
            COUNT(DISTINCT n.cccd) as soluong
        FROM nguoidung n
        INNER JOIN thanhvienhokhau tv ON n.cccd = tv.cccd
        INNER JOIN hokhau hk ON tv.mahokhau = hk.mahokhau
        INNER JOIN diachi dc ON hk.madiachi = dc.madiachi
        WHERE tv.ngayketthuc IS NULL
    """
    
    if xaphuong:
        query_age_gender += " AND LOWER(dc.xaphuong) LIKE LOWER(%s)"
    
    query_age_gender += """
        GROUP BY nhom_tuoi, n.gioitinh
        ORDER BY 
            CASE nhom_tuoi
                WHEN '0-5' THEN 1
                WHEN '6-10' THEN 2
                WHEN '11-14' THEN 3
                WHEN '15-17' THEN 4
                WHEN '18-59' THEN 5
                WHEN '60+' THEN 6
            END, n.gioitinh
    """
    
    stats_age_gender = execute_query(query_age_gender, tuple(params) if params else None, fetch_all=True)
    
    # Query thống kê theo địa bàn (top 10)
    query_diaban = """
        SELECT 
            dc.xaphuong,
            COUNT(DISTINCT n.cccd) as tong,
            COUNT(DISTINCT CASE WHEN n.gioitinh = 'Nam' THEN n.cccd END) as nam,
            COUNT(DISTINCT CASE WHEN n.gioitinh = 'Nữ' THEN n.cccd END) as nu
        FROM nguoidung n
        INNER JOIN thanhvienhokhau tv ON n.cccd = tv.cccd
        INNER JOIN hokhau hk ON tv.mahokhau = hk.mahokhau
        INNER JOIN diachi dc ON hk.madiachi = dc.madiachi
        WHERE tv.ngayketthuc IS NULL
    """
    
    if xaphuong:
        query_diaban += " AND LOWER(dc.xaphuong) LIKE LOWER(%s)"
    
    query_diaban += """
        GROUP BY dc.xaphuong
        ORDER BY tong DESC
        LIMIT 10
    """
    
    stats_diaban = execute_query(query_diaban, tuple(params) if params else None, fetch_all=True)
    
    return render_template('thongke_danso.html',
                         stats_total=stats_total,
                         stats_age=stats_age,
                         stats_age_gender=stats_age_gender,
                         stats_diaban=stats_diaban,
                         xaphuong=xaphuong)

@app.route('/thong-ke/tam-vang-tru')
@login_required
def thongke_tamvangtru():
    """Báo cáo thống kê tạm vắng/tạm trú"""
    
    # Lấy tham số filter
    thang = request.args.get('thang', '')
    nam = request.args.get('nam', '')
    loai = request.args.get('loai', '')
    xaphuong = request.args.get('xaphuong', '').strip()
    
    # Build query
    query = """
        SELECT 
            dn.loaidiachi,
            dc.xaphuong,
            COUNT(*) as soluong,
            COUNT(CASE WHEN dn.ngayketthuc >= CURRENT_DATE THEN 1 END) as dang_hieuluc,
            COUNT(CASE WHEN dn.ngayketthuc < CURRENT_DATE THEN 1 END) as da_hethan
        FROM diachinguoidung dn
        INNER JOIN diachi dc ON dn.madiachi = dc.madiachi
        WHERE dn.loaidiachi IN ('TamVang', 'TamTru')
    """
    
    params = []
    
    # Filter by month/year
    if thang and nam:
        query += " AND EXTRACT(MONTH FROM dn.ngaybatdau) = %s AND EXTRACT(YEAR FROM dn.ngaybatdau) = %s"
        params.extend([int(thang), int(nam)])
    elif nam:
        query += " AND EXTRACT(YEAR FROM dn.ngaybatdau) = %s"
        params.append(int(nam))
    
    # Filter by type
    if loai:
        query += " AND dn.loaidiachi = %s"
        params.append(loai)
    
    # Filter by district
    if xaphuong:
        query += " AND LOWER(dc.xaphuong) LIKE LOWER(%s)"
        params.append(f'%{xaphuong}%')
    
    query += """
        GROUP BY dn.loaidiachi, dc.xaphuong
        ORDER BY dn.loaidiachi, dc.xaphuong
    """
    
    stats = execute_query(query, tuple(params) if params else None, fetch_all=True)
    
    # Query chi tiết
    query_detail = """
        SELECT 
            n.cccd,
            n.hoten,
            n.ngaysinh,
            n.gioitinh,
            dn.loaidiachi,
            dc.xaphuong,
            dc.chitiet,
            dn.ngaybatdau,
            dn.ngayketthuc,
            dn.lydo
        FROM diachinguoidung dn
        INNER JOIN diachi dc ON dn.madiachi = dc.madiachi
        INNER JOIN nguoidung n ON dn.cccd = n.cccd
        WHERE dn.loaidiachi IN ('TamVang', 'TamTru')
    """
    
    params_detail = []
    
    if thang and nam:
        query_detail += " AND EXTRACT(MONTH FROM dn.ngaybatdau) = %s AND EXTRACT(YEAR FROM dn.ngaybatdau) = %s"
        params_detail.extend([int(thang), int(nam)])
    elif nam:
        query_detail += " AND EXTRACT(YEAR FROM dn.ngaybatdau) = %s"
        params_detail.append(int(nam))
    
    if loai:
        query_detail += " AND dn.loaidiachi = %s"
        params_detail.append(loai)
    
    if xaphuong:
        query_detail += " AND LOWER(dc.xaphuong) LIKE LOWER(%s)"
        params_detail.append(f'%{xaphuong}%')
    
    query_detail += " ORDER BY dn.ngaybatdau DESC"
    
    details = execute_query(query_detail, tuple(params_detail) if params_detail else None, fetch_all=True)
    
    # Tổng hợp
    tong_tamvang = sum(row[2] for row in stats if row[0] == 'TamVang')
    tong_tamtru = sum(row[2] for row in stats if row[0] == 'TamTru')
    
    return render_template('thongke_tamvangtru.html',
                         stats=stats,
                         details=details,
                         tong_tamvang=tong_tamvang,
                         tong_tamtru=tong_tamtru,
                         thang=thang,
                         nam=nam,
                         loai=loai,
                         xaphuong=xaphuong,
                         openpyxl_available=OPENPYXL_AVAILABLE)


@app.route('/thong-ke/tam-vang-tru/export')
@login_required
def export_tamvangtru():
    """Export báo cáo tạm vắng/tạm trú ra Excel"""
    
    if not OPENPYXL_AVAILABLE:
        flash('Vui lòng cài đặt thư viện openpyxl để sử dụng tính năng này', 'error')
        return redirect(url_for('thongke_tamvangtru'))
    
    # Lấy tham số filter (same as report view)
    thang = request.args.get('thang', '')
    nam = request.args.get('nam', '')
    loai = request.args.get('loai', '')
    xaphuong = request.args.get('xaphuong', '').strip()
    
    # Query chi tiết
    query_detail = """
        SELECT 
            n.cccd,
            n.hoten,
            n.ngaysinh,
            n.gioitinh,
            dn.loaidiachi,
            dc.xaphuong,
            dc.chitiet,
            dn.ngaybatdau,
            dn.ngayketthuc,
            dn.lydo
        FROM diachinguoidung dn
        INNER JOIN diachi dc ON dn.madiachi = dc.madiachi
        INNER JOIN nguoidung n ON dn.cccd = n.cccd
        WHERE dn.loaidiachi IN ('TamVang', 'TamTru')
    """
    
    params = []
    
    if thang and nam:
        query_detail += " AND EXTRACT(MONTH FROM dn.ngaybatdau) = %s AND EXTRACT(YEAR FROM dn.ngaybatdau) = %s"
        params.extend([int(thang), int(nam)])
    elif nam:
        query_detail += " AND EXTRACT(YEAR FROM dn.ngaybatdau) = %s"
        params.append(int(nam))
    
    if loai:
        query_detail += " AND dn.loaidiachi = %s"
        params.append(loai)
    
    if xaphuong:
        query_detail += " AND LOWER(dc.xaphuong) LIKE LOWER(%s)"
        params.append(f'%{xaphuong}%')
    
    query_detail += " ORDER BY dn.loaidiachi, dn.ngaybatdau DESC"
    
    details = execute_query(query_detail, tuple(params) if params else None, fetch_all=True)
    
    # Create workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Báo cáo Tạm vắng Tạm trú"
    
    # Styles
    header_font = Font(bold=True, size=12, color="FFFFFF")
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center")
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    # Title
    ws.merge_cells('A1:J1')
    title_cell = ws['A1']
    title_cell.value = "BÁO CÁO TẠM VẮNG/TẠM TRÚ"
    title_cell.font = Font(bold=True, size=14)
    title_cell.alignment = Alignment(horizontal="center", vertical="center")
    
    # Filter info
    filter_info = f"Thời gian: {thang}/{nam}" if thang and nam else (f"Năm: {nam}" if nam else "Tất cả")
    if loai:
        filter_info += f" - Loại: {loai}"
    if xaphuong:
        filter_info += f" - Xã/Phường: {xaphuong}"
    
    ws.merge_cells('A2:J2')
    filter_cell = ws['A2']
    filter_cell.value = filter_info
    filter_cell.alignment = Alignment(horizontal="center")
    
    # Headers
    headers = ['STT', 'CCCD', 'Họ tên', 'Ngày sinh', 'Giới tính', 'Loại', 'Xã/Phường', 
               'Địa chỉ', 'Ngày bắt đầu', 'Ngày kết thúc', 'Lý do']
    
    for col, header in enumerate(headers, start=1):
        cell = ws.cell(row=4, column=col)
        cell.value = header
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = border
    
    # Data rows
    for idx, row in enumerate(details, start=1):
        ws_row = idx + 4
        ws.cell(row=ws_row, column=1, value=idx).border = border
        ws.cell(row=ws_row, column=2, value=row[0]).border = border
        ws.cell(row=ws_row, column=3, value=row[1]).border = border
        ws.cell(row=ws_row, column=4, value=row[2].strftime('%d/%m/%Y') if row[2] else '').border = border
        ws.cell(row=ws_row, column=5, value=row[3]).border = border
        ws.cell(row=ws_row, column=6, value='Tạm vắng' if row[4] == 'TamVang' else 'Tạm trú').border = border
        ws.cell(row=ws_row, column=7, value=row[5]).border = border
        ws.cell(row=ws_row, column=8, value=row[6]).border = border
        ws.cell(row=ws_row, column=9, value=row[7].strftime('%d/%m/%Y') if row[7] else '').border = border
        ws.cell(row=ws_row, column=10, value=row[8].strftime('%d/%m/%Y') if row[8] else '').border = border
        ws.cell(row=ws_row, column=11, value=row[9]).border = border
    
    # Column widths
    ws.column_dimensions['A'].width = 5
    ws.column_dimensions['B'].width = 13
    ws.column_dimensions['C'].width = 25
    ws.column_dimensions['D'].width = 12
    ws.column_dimensions['E'].width = 10
    ws.column_dimensions['F'].width = 12
    ws.column_dimensions['G'].width = 15
    ws.column_dimensions['H'].width = 30
    ws.column_dimensions['I'].width = 13
    ws.column_dimensions['J'].width = 13
    ws.column_dimensions['K'].width = 25
    
    # Save to BytesIO
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    # Generate filename with timestamp
    filename = f"BaoCao_TamVangTamTru_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )


@app.route('/nguoidung')
@login_required  
def nguoidung_list():
    """Danh sách người dùng/nhân khẩu với phân trang, tìm kiếm và lọc"""
    
    # ========== CẤU HÌNH PHÂN TRANG ==========
    per_page = 20  # Số bản ghi mỗi trang
    
    # Lấy số trang từ URL, mặc định là 1
    try:
        page = int(request.args.get('page', 1))
        if page < 1:
            page = 1
    except (ValueError, TypeError):
        page = 1
    
    # Tính offset
    offset = (page - 1) * per_page
    
    # ========== LẤY THAM SỐ TÌM KIẾM VÀ LỌC ==========
    search = request.args.get('search', '').strip()
    gioitinh = request.args.get('gioitinh', '').strip()
    vaitro = request.args.get('vaitro', '').strip()
    dantoc = request.args.get('dantoc', '').strip()
    
    # ========== XÂY DỰNG ĐIỀU KIỆN WHERE ==========
    where_conditions = []
    params = []
    
    if search:
        where_conditions.append("(cccd LIKE %s OR name ILIKE %s OR sdt LIKE %s)")
        search_pattern = f"%{search}%"
        params.extend([search_pattern, search_pattern, search_pattern])
    
    if gioitinh:
        where_conditions.append("LOWER(gioitinh) = LOWER(%s)")
        params.append(gioitinh)
    
    if vaitro:
        where_conditions.append("vaitro = %s")
        params.append(vaitro)
    
    if dantoc:
        where_conditions.append("dantoc ILIKE %s")
        params.append(dantoc)
    
    where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
    
    # ========== ĐẾM TỔNG SỐ NGƯỜI DÙNG ==========
    query_count = f"SELECT COUNT(*) FROM nguoidung WHERE {where_clause}"
    total_count = execute_query(query_count, tuple(params), fetch_one=True)
    total_count = total_count[0] if total_count else 0
    
    # Tính tổng số trang
    import math
    total_pages = math.ceil(total_count / per_page) if total_count > 0 else 1
    
    # Đảm bảo page không vượt quá total_pages
    if page > total_pages and total_pages > 0:
        page = total_pages
    
    # ========== QUERY DANH SÁCH NGƯỜI DÙNG VỚI PHÂN TRANG ==========
    query = f"""
        SELECT 
            cccd,
            name,
            sdt,
            ngaysinh,
            gioitinh,
            dantoc,
            vaitro
        FROM nguoidung
        WHERE {where_clause}
        ORDER BY name
        LIMIT %s OFFSET %s
    """
    params.extend([per_page, offset])
    ds_nguoidung = execute_query(query, tuple(params), fetch_all=True)
    ds_nguoidung = ds_nguoidung if ds_nguoidung else []
    
    return render_template('nguoidung.html', 
                         ds_nguoidung=ds_nguoidung,
                         page=page,
                         per_page=per_page,
                         total_pages=total_pages,
                         total_count=total_count,
                         search=search,
                         gioitinh=gioitinh,
                         vaitro=vaitro,
                         dantoc=dantoc)


@app.route('/nguoidung/add', methods=['GET', 'POST'])
@login_required
def nguoidung_add():
    """Thêm nhân khẩu mới"""
    if request.method == 'POST':
        # Lấy dữ liệu từ form - Thông tin cơ bản
        cccd = request.form.get('cccd', '').strip()
        name = request.form.get('name', '').strip()
        user_name = request.form.get('user_name', '').strip()
        matkhau = request.form.get('matkhau', '').strip()
        bidanh = request.form.get('bidanh', '').strip()
        sdt = request.form.get('sdt', '').strip()
        ngaysinh = request.form.get('ngaysinh', '').strip()
        gioitinh = request.form.get('gioitinh', '').strip()
        dantoc = request.form.get('dantoc', '').strip()
        vaitro = request.form.get('vaitro', '').strip()
        nghenghiep = request.form.get('nghenghiep', '').strip()
        noilamviec = request.form.get('noilamviec', '').strip()
        noisinh = request.form.get('noisinh', '').strip()
        nguyenquan = request.form.get('nguyenquan', '').strip()
        
        # Thông tin CCCD
        ngaycapcccd = request.form.get('ngaycapcccd', '').strip()
        noicapcccd = request.form.get('noicapcccd', '').strip()
        
        # Địa chỉ thường trú
        ngaydangkythuongtru = request.form.get('ngaydangkythuongtru', '').strip()
        diachitruoc = request.form.get('diachitruoc', '').strip()
        
        # Validate
        if not cccd or not name or not user_name or not matkhau:
            flash('Vui lòng nhập đầy đủ thông tin bắt buộc (CCCD, Họ tên, Tên đăng nhập, Mật khẩu)!', 'danger')
            return render_template('nguoidung_add.html')
        
        # Kiểm tra CCCD đã tồn tại chưa
        check_query = "SELECT cccd FROM nguoidung WHERE cccd = %s"
        existing = execute_query(check_query, (cccd,), fetch_one=True)
        if existing:
            flash('CCCD đã tồn tại trong hệ thống!', 'danger')
            return render_template('nguoidung_add.html')
        
        # Kiểm tra username đã tồn tại chưa
        check_username = "SELECT user_name FROM nguoidung WHERE user_name = %s"
        existing_username = execute_query(check_username, (user_name,), fetch_one=True)
        if existing_username:
            flash('Tên đăng nhập đã tồn tại!', 'danger')
            return render_template('nguoidung_add.html')
        
        # Insert vào database
        insert_query = """
            INSERT INTO nguoidung (
                cccd, name, user_name, matkhau, sdt, ngaysinh, gioitinh, dantoc, vaitro, nghenghiep,
                bidanh, noilamviec, noisinh, nguyenquan, ngaycapcccd, noicapcccd, 
                ngaydangkythuongtru, diachitruoc
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        result = execute_query(insert_query, (
            cccd, name, user_name, matkhau, 
            sdt or None, ngaysinh or None, gioitinh or None, dantoc or None, 
            vaitro or 'NguoiDan', nghenghiep or None,
            bidanh or None, noilamviec or None, noisinh or None, nguyenquan or None,
            ngaycapcccd or None, noicapcccd or None, ngaydangkythuongtru or None, diachitruoc or None
        ))
        
        if result:
            flash(f'Đã thêm nhân khẩu {name} thành công!', 'success')
            return redirect(url_for('nguoidung_list'))
        else:
            flash('Có lỗi xảy ra khi thêm nhân khẩu!', 'danger')
    
    return render_template('nguoidung_add.html')


@app.route('/nguoidung/edit/<string:cccd>', methods=['GET', 'POST'])
@login_required
def nguoidung_edit(cccd):
    """Sửa thông tin nhân khẩu"""
    
    if request.method == 'POST':
        # Lấy dữ liệu từ form
        name = request.form.get('name', '').strip()
        user_name = request.form.get('user_name', '').strip()
        bidanh = request.form.get('bidanh', '').strip()
        sdt = request.form.get('sdt', '').strip()
        ngaysinh = request.form.get('ngaysinh', '').strip()
        gioitinh = request.form.get('gioitinh', '').strip()
        dantoc = request.form.get('dantoc', '').strip()
        vaitro = request.form.get('vaitro', '').strip()
        nghenghiep = request.form.get('nghenghiep', '').strip()
        noilamviec = request.form.get('noilamviec', '').strip()
        noisinh = request.form.get('noisinh', '').strip()
        nguyenquan = request.form.get('nguyenquan', '').strip()
        ngaycapcccd = request.form.get('ngaycapcccd', '').strip()
        noicapcccd = request.form.get('noicapcccd', '').strip()
        ngaydangkythuongtru = request.form.get('ngaydangkythuongtru', '').strip()
        diachitruoc = request.form.get('diachitruoc', '').strip()
        
        # Validate
        if not name or not user_name:
            flash('Vui lòng nhập đầy đủ họ tên và tên đăng nhập!', 'danger')
            return redirect(url_for('nguoidung_edit', cccd=cccd))
        
        # Kiểm tra username đã tồn tại chưa (trừ chính nó)
        check_username = "SELECT user_name FROM nguoidung WHERE user_name = %s AND cccd != %s"
        existing_username = execute_query(check_username, (user_name, cccd), fetch_one=True)
        if existing_username:
            flash('Tên đăng nhập đã tồn tại!', 'danger')
            return redirect(url_for('nguoidung_edit', cccd=cccd))
        
        # Update database
        update_query = """
            UPDATE nguoidung 
            SET name = %s, user_name = %s, sdt = %s, ngaysinh = %s, gioitinh = %s, 
                dantoc = %s, vaitro = %s, nghenghiep = %s, bidanh = %s, noilamviec = %s,
                noisinh = %s, nguyenquan = %s, ngaycapcccd = %s, noicapcccd = %s,
                ngaydangkythuongtru = %s, diachitruoc = %s
            WHERE cccd = %s
        """
        result = execute_query(update_query, (
            name, user_name, sdt or None, ngaysinh or None, gioitinh or None,
            dantoc or None, vaitro or 'NguoiDan', nghenghiep or None, bidanh or None, noilamviec or None,
            noisinh or None, nguyenquan or None, ngaycapcccd or None, noicapcccd or None,
            ngaydangkythuongtru or None, diachitruoc or None, cccd
        ))
        
        if result:
            flash(f'Đã cập nhật thông tin nhân khẩu {name} thành công!', 'success')
            return redirect(url_for('nguoidung_list'))
        else:
            flash('Có lỗi xảy ra khi cập nhật!', 'danger')
    
    # GET: Load dữ liệu hiện tại
    query = """
        SELECT cccd, name, user_name, sdt, ngaysinh, gioitinh, dantoc, vaitro, nghenghiep,
               bidanh, noilamviec, noisinh, nguyenquan, ngaycapcccd, noicapcccd,
               ngaydangkythuongtru, diachitruoc
        FROM nguoidung WHERE cccd = %s
    """
    nguoidung = execute_query(query, (cccd,), fetch_one=True)
    
    if not nguoidung:
        flash('Không tìm thấy nhân khẩu!', 'danger')
        return redirect(url_for('nguoidung_list'))
    
    return render_template('nguoidung_edit.html', nguoidung=nguoidung)


@app.route('/nguoidung/delete/<string:cccd>', methods=['POST'])
@login_required
def nguoidung_delete(cccd):
    """Xóa nhân khẩu"""
    
    # Kiểm tra xem người này có trong hộ khẩu nào không
    check_hokhau = "SELECT COUNT(*) FROM thanhvienhokhau WHERE cccd = %s AND ngayketthuc IS NULL"
    count = execute_query(check_hokhau, (cccd,), fetch_one=True)
    
    if count and count[0] > 0:
        flash('Không thể xóa! Nhân khẩu này đang thuộc hộ khẩu. Vui lòng xóa khỏi hộ khẩu trước.', 'danger')
        return redirect(url_for('nguoidung_list'))
    
    # Lấy tên để hiển thị thông báo
    query_name = "SELECT name FROM nguoidung WHERE cccd = %s"
    nguoidung = execute_query(query_name, (cccd,), fetch_one=True)
    name = nguoidung[0] if nguoidung else cccd
    
    # Xóa
    delete_query = "DELETE FROM nguoidung WHERE cccd = %s"
    result = execute_query(delete_query, (cccd,))
    
    if result:
        flash(f'Đã xóa nhân khẩu {name} thành công!', 'success')
    else:
        flash('Có lỗi xảy ra khi xóa!', 'danger')
    
    return redirect(url_for('nguoidung_list'))


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
