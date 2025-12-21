"""
Ứng dụng Quản lý Dân cư Tổ dân phố
Backend: Flask + PostgreSQL (psycopg2)
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, jsonify
import psycopg2
from psycopg2 import Error
from functools import wraps
import os
import math
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


def role_required(allowed_roles):
    """
    Decorator kiểm tra vai trò người dùng (RBAC)
    
    Args:
        allowed_roles (list): Danh sách vai trò được phép truy cập
                             VD: ['CanBo', 'QuanLy']
    
    Returns:
        Redirect về dashboard với thông báo lỗi nếu không đủ quyền
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Kiểm tra đăng nhập
            if 'user' not in session:
                flash('Vui lòng đăng nhập để truy cập!', 'warning')
                return redirect(url_for('login'))
            
            # Kiểm tra vai trò
            user_role = session['user'].get('vaitro')
            
            if user_role not in allowed_roles:
                flash('Bạn không có quyền truy cập chức năng này!', 'danger')
                return redirect(url_for('dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


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
@role_required(['CanBo', 'QuanLy'])
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
@role_required(['CanBo', 'QuanLy'])
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
@role_required(['CanBo', 'QuanLy'])
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
@role_required(['CanBo', 'QuanLy'])
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
@role_required(['CanBo', 'QuanLy'])
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


@role_required(['CanBo', 'QuanLy'])
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


@role_required(['CanBo', 'QuanLy'])
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
            COUNT(DISTINCT CASE WHEN LOWER(n.gioitinh) = 'nam' THEN n.cccd END) as nam,
            COUNT(DISTINCT CASE WHEN LOWER(n.gioitinh) = 'nu' THEN n.cccd END) as nu
        FROM nguoidung n
        INNER JOIN thanhvienhokhau tv ON n.cccd = tv.cccd
        INNER JOIN hokhau hk ON tv.mahokhau = hk.mahokhau
        INNER JOIN diachi dc ON hk.madiachi = dc.madiachi
        WHERE tv.ngayketthuc IS NULL
    """
    params_total = []
    
    if xaphuong:
        query_total += " AND LOWER(dc.xaphuong) LIKE LOWER(%s)"
        params_total.append(f'%{xaphuong}%')
    
    stats_total = execute_query(query_total, tuple(params_total) if params_total else None, fetch_one=True)
    stats_total = stats_total or (0, 0, 0)
    
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
        WHERE tv.ngayketthuc IS NULL AND n.ngaysinh IS NOT NULL
    """
    
    params_age = []
    if xaphuong:
        query_age += " AND LOWER(dc.xaphuong) LIKE LOWER(%s)"
        params_age.append(f'%{xaphuong}%')
    
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
    
    stats_age = execute_query(query_age, tuple(params_age) if params_age else None, fetch_all=True)
    stats_age = stats_age or []
    
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
        WHERE tv.ngayketthuc IS NULL AND n.ngaysinh IS NOT NULL
    """
    
    params_age_gender = []
    if xaphuong:
        query_age_gender += " AND LOWER(dc.xaphuong) LIKE LOWER(%s)"
        params_age_gender.append(f'%{xaphuong}%')
    
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
    
    stats_age_gender = execute_query(query_age_gender, tuple(params_age_gender) if params_age_gender else None, fetch_all=True)
    stats_age_gender = stats_age_gender or []
    
    # Query thống kê theo địa bàn (top 10)
    query_diaban = """
        SELECT 
            dc.xaphuong,
            COUNT(DISTINCT n.cccd) as tong,
            COUNT(DISTINCT CASE WHEN LOWER(n.gioitinh) = 'nam' THEN n.cccd END) as nam,
            COUNT(DISTINCT CASE WHEN LOWER(n.gioitinh) = 'nu' THEN n.cccd END) as nu
        FROM nguoidung n
        INNER JOIN thanhvienhokhau tv ON n.cccd = tv.cccd
        INNER JOIN hokhau hk ON tv.mahokhau = hk.mahokhau
        INNER JOIN diachi dc ON hk.madiachi = dc.madiachi
        WHERE tv.ngayketthuc IS NULL
    """
    
    params_diaban = []
    if xaphuong:
        query_diaban += " AND LOWER(dc.xaphuong) LIKE LOWER(%s)"
        params_diaban.append(f'%{xaphuong}%')
    
    query_diaban += """
        GROUP BY dc.xaphuong
        ORDER BY tong DESC
        LIMIT 10
    """
    
    stats_diaban = execute_query(query_diaban, tuple(params_diaban) if params_diaban else None, fetch_all=True)
    stats_diaban = stats_diaban or []
    
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
    
    # Đảm bảo stats không phải None để tránh lỗi for qua NoneType
    stats = stats or []
    tong_tamvang = sum(row[2] for row in stats if row[0] == 'TamVang')
    tong_tamtru = sum(row[2] for row in stats if row[0] == 'TamTru')
    
    # Đảm bảo details không phải None để tránh lỗi len(None)
    details = details or []
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


@role_required(['CanBo', 'QuanLy'])
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


@role_required(['CanBo', 'QuanLy'])
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


@app.route('/nguoidung/<string:cccd>')
@login_required
def nguoidung_detail(cccd):
    """Xem chi tiết nhân khẩu"""
    
    # Lấy thông tin nhân khẩu
    query = """
        SELECT cccd, name, user_name, sdt, ngaysinh, gioitinh, dantoc, vaitro, nghenghiep
        FROM nguoidung WHERE cccd = %s
    """
    nguoidung = execute_query(query, (cccd,), fetch_one=True)
    
    if not nguoidung:
        flash('Không tìm thấy nhân khẩu!', 'danger')
        return redirect(url_for('nguoidung_list'))
    
    # Lấy danh sách hộ khẩu mà người này tham gia (hiện tại và quá khứ)
    query_hokhau = """
        SELECT 
            hk.mahokhau,
            dc.xaphuong,
            dc.chitiet,
            tv.quanhechuho,
            tv.ngaybatdau,
            tv.ngayketthuc,
            hk.ghichu
        FROM thanhvienhokhau tv
        INNER JOIN hokhau hk ON tv.mahokhau = hk.mahokhau
        LEFT JOIN diachi dc ON hk.madiachi = dc.madiachi
        WHERE tv.cccd = %s
        ORDER BY tv.ngaybatdau DESC
    """
    ds_hokhau = execute_query(query_hokhau, (cccd,), fetch_all=True)
    ds_hokhau = ds_hokhau or []
    
    # Lấy lịch sử tạm vắng/tạm trú
    query_tamvangtru = """
        SELECT 
            dn.loaidiachi,
            dc.xaphuong,
            dc.chitiet,
            dn.ngaybatdau,
            dn.ngayketthuc,
            dn.lydo
        FROM diachinguoidung dn
        LEFT JOIN diachi dc ON dn.madiachi = dc.madiachi
        WHERE dn.cccd = %s AND dn.loaidiachi IN ('TamVang', 'TamTru')
        ORDER BY dn.ngaybatdau DESC
    """
    ds_tamvangtru = execute_query(query_tamvangtru, (cccd,), fetch_all=True)
    ds_tamvangtru = ds_tamvangtru or []
    
    return render_template('nguoidung_detail.html', 
                         nguoidung=nguoidung,
                         ds_hokhau=ds_hokhau,
                         ds_tamvangtru=ds_tamvangtru)

@role_required(['CanBo', 'QuanLy'])

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
        SELECT cccd, name, user_name, sdt, ngaysinh, gioitinh, dantoc, vaitro, nghenghiep
        FROM nguoidung WHERE cccd = %s
    """
    nguoidung = execute_query(query, (cccd,), fetch_one=True)
    
    if not nguoidung:
        flash('Không tìm thấy nhân khẩu!', 'danger')
        return redirect(url_for('nguoidung_list'))
    
    # Tạo tuple mở rộng với các giá trị mặc định cho các cột chưa có trong DB
    # Thứ tự: cccd, name, user_name, sdt, ngaysinh, gioitinh, dantoc, vaitro, nghenghiep,
    #         bidanh, noilamviec, noisinh, nguyenquan, ngaycapcccd, noicapcccd,
    #         ngaydangkythuongtru, diachitruoc
    nguoidung_extended = nguoidung + ('', '', '', '', None, '', None, '')  # Thêm 8 cột mặc định
    
    return render_template('nguoidung_edit.html', nguoidung=nguoidung_extended)

@role_required(['CanBo', 'QuanLy'])

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
    """Danh sách phản ánh - Phân quyền theo vai trò"""
    
    # Người dân chỉ xem phản ánh của mình
    # Cán bộ/Quản lý xem tất cả
    user_role = session['user'].get('vaitro')
    user_cccd = session['user'].get('cccd')
    
    if user_role == 'NguoiDan':
        # Người dân chỉ xem phản ánh của mình
        query = """
            SELECT 
                p.maphananh,
                p.tieude,
                p.loaiphananh,
                p.trangthaiphananh,
                p.mota,
                p.thoigiantao,
                p.is_public,
                p.like_count,
                p.comment_count,
                p.view_count,
                v.tenvande,
                v.trangthai as trangthai_vande
            FROM phananh p
            LEFT JOIN vande v ON p.mavande = v.mavande
            WHERE p.cccd = %s
            ORDER BY p.thoigiantao DESC
        """
        ds_phananh = execute_query(query, (user_cccd,), fetch_all=True)
    else:
        # Cán bộ/Quản lý xem tất cả
        query = """
            SELECT 
                p.maphananh,
                n.name as nguoiphan,
                p.tieude,
                p.loaiphananh,
                p.trangthaiphananh,
                p.mota,
                p.thoigiantao,
                p.is_public,
                p.like_count,
                p.comment_count,
                p.view_count,
                v.tenvande,
                v.trangthai as trangthai_vande,
                d.xaphuong,
                d.chitiet
            FROM phananh p
            LEFT JOIN nguoidung n ON p.cccd = n.cccd
            LEFT JOIN vande v ON p.mavande = v.mavande
            LEFT JOIN diachi d ON p.madiachi = d.madiachi
            ORDER BY p.thoigiantao DESC
        """
        ds_phananh = execute_query(query, fetch_all=True)
    
    ds_phananh = ds_phananh if ds_phananh else []
    
    return render_template('phananh.html', ds_phananh=ds_phananh)


@app.route('/phananh/add', methods=['GET', 'POST'])
@login_required
def phananh_add():
    """Tạo phản ánh mới - Người dân có thể tạo phản ánh"""
    
    if request.method == 'POST':
        tieude = request.form.get('tieude', '').strip()
        mota = request.form.get('mota', '').strip()
        loaiphananh = request.form.get('loaiphananh', '').strip()
        is_public = request.form.get('is_public') == 'on'
        allow_comment = request.form.get('allow_comment') == 'on'
        
        # Địa chỉ (optional)
        tinh = request.form.get('tinh', '').strip()
        xaphuong = request.form.get('xaphuong', '').strip()
        chitiet = request.form.get('chitiet', '').strip()
        
        # Validate
        if not tieude or not mota:
            flash('Vui lòng nhập đầy đủ tiêu đề và mô tả!', 'warning')
            return redirect(url_for('phananh_add'))
        
        # Tạo địa chỉ nếu có
        madiachi = None
        if tinh or xaphuong or chitiet:
            query_diachi = """
                INSERT INTO diachi (tinh, xaphuong, chitiet)
                VALUES (%s, %s, %s)
                RETURNING madiachi
            """
            result = execute_query(query_diachi, (tinh, xaphuong, chitiet), fetch_one=True)
            if result:
                madiachi = result[0]
        
        # Tạo phản ánh
        query_phananh = """
            INSERT INTO phananh (
                cccd, madiachi, loaiphananh, trangthaiphananh,
                mota, tieude, is_public, allow_comment,
                thoigiantao
            )
            VALUES (%s, %s, %s, 'ChuaXuLy', %s, %s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING maphananh
        """
        
        result = execute_query(
            query_phananh,
            (session['user']['cccd'], madiachi, loaiphananh, mota, tieude, is_public, allow_comment),
            fetch_one=True
        )
        
        if result:
            maphananh = result[0]
            
            # Tự động tạo boxchat nếu phản ánh riêng tư
            if not is_public:
                query_boxchat = """
                    INSERT INTO boxchat (maphananh, cccd_nguoidan)
                    VALUES (%s, %s)
                """
                execute_query(query_boxchat, (maphananh, session['user']['cccd']))
            
            flash(f'Đã tạo phản ánh thành công! Mã phản ánh: {maphananh}', 'success')
            return redirect(url_for('phananh_detail', maphananh=maphananh))
        else:
            flash('Có lỗi xảy ra khi tạo phản ánh!', 'danger')
    
    return render_template('phananh_add.html')


@app.route('/phananh/<int:maphananh>')
@login_required
def phananh_detail(maphananh):
    """Xem chi tiết phản ánh - Tăng view count"""
    
    # Query thông tin phản ánh đầy đủ
    query = """
        SELECT 
            p.maphananh,
            p.cccd,
            n.name AS nguoi_tao,
            n.sdt AS sdt_nguoi_tao,
            p.tieude,
            p.mota,
            p.loaiphananh,
            p.trangthaiphananh,
            p.is_public,
            p.allow_comment,
            p.like_count,
            p.comment_count,
            p.view_count,
            p.thoigiantao,
            p.thoigianxuly,
            p.mavande,
            v.tenvande,
            v.phanloai AS phanloai_vande,
            v.trangthai AS trangthai_vande,
            v.ketqua AS ketqua_vande,
            d.tinh,
            d.xaphuong,
            d.chitiet AS diachi_chitiet,
            t.duongdan AS hinh_anh
        FROM phananh p
        LEFT JOIN nguoidung n ON p.cccd = n.cccd
        LEFT JOIN vande v ON p.mavande = v.mavande
        LEFT JOIN diachi d ON p.madiachi = d.madiachi
        LEFT JOIN tepdinhkem t ON p.matepdinhkem = t.matepdinhkem
        WHERE p.maphananh = %s
    """
    
    phananh = execute_query(query, (maphananh,), fetch_one=True)
    
    if not phananh:
        flash('Không tìm thấy phản ánh!', 'danger')
        return redirect(url_for('phananh_list'))
    
    # Kiểm tra quyền xem (Phản ánh riêng tư chỉ chủ nhân và Cán bộ/Quản lý xem được)
    user_role = session['user'].get('vaitro')
    user_cccd = session['user'].get('cccd')
    phananh_cccd = phananh[1]  # cccd của người tạo
    is_public = phananh[8]  # is_public
    
    if not is_public and user_role == 'NguoiDan' and user_cccd != phananh_cccd:
        flash('Bạn không có quyền xem phản ánh này!', 'danger')
        return redirect(url_for('phananh_list'))
    
    # Tăng view count
    update_view = "UPDATE phananh SET view_count = view_count + 1 WHERE maphananh = %s"
    execute_query(update_view, (maphananh,))
    
    # Lấy danh sách bình luận (nếu cho phép)
    comments = []
    if phananh[9]:  # allow_comment
        query_comments = """
            SELECT 
                b.id,
                b.cccd_nguoidung,
                n.name AS ten_nguoi_binh_luan,
                n.avatar_url,
                b.noidung,
                b.thoigian,
                b.parent_id,
                b.is_hidden
            FROM binhluan b
            LEFT JOIN nguoidung n ON b.cccd_nguoidung = n.cccd
            WHERE b.maphananh = %s AND b.is_hidden = FALSE
            ORDER BY b.thoigian DESC
        """
        comments = execute_query(query_comments, (maphananh,), fetch_all=True)
        comments = comments if comments else []
    
    # Kiểm tra user đã like chưa
    user_liked = False
    if is_public:
        query_like = "SELECT 1 FROM like_post WHERE maphananh = %s AND cccd = %s"
        like_result = execute_query(query_like, (maphananh, user_cccd), fetch_one=True)
        user_liked = like_result is not None
    
    # Lấy boxchat_id nếu có
    query_boxchat = "SELECT maboxchat FROM boxchat WHERE maphananh = %s LIMIT 1"
    boxchat_result = execute_query(query_boxchat, (maphananh,), fetch_one=True)
    boxchat_id = boxchat_result[0] if boxchat_result else None
    
    # Lấy tên người dùng và tên vấn đề từ phananh tuple
    nguoidung_name = phananh[2]  # nguoi_tao từ query
    vande_name = phananh[16] if phananh[16] else None  # tenvande từ LEFT JOIN
    
    return render_template('phananh_detail.html', 
                         phananh=phananh, 
                         comments=comments,
                         user_liked=user_liked,
                         nguoidung_name=nguoidung_name,
                         vande_name=vande_name,
                         boxchat_id=boxchat_id)


@app.route('/phananh/edit/<int:maphananh>', methods=['GET', 'POST'])
@login_required
def phananh_edit(maphananh):
    """Chỉnh sửa phản ánh - Ownership check"""
    
    # Lấy thông tin phản ánh
    query_check = "SELECT cccd, trangthaiphananh FROM phananh WHERE maphananh = %s"
    phananh_check = execute_query(query_check, (maphananh,), fetch_one=True)
    
    if not phananh_check:
        flash('Không tìm thấy phản ánh!', 'danger')
        return redirect(url_for('phananh_list'))
    
    phananh_cccd = phananh_check[0]
    user_role = session['user'].get('vaitro')
    user_cccd = session['user'].get('cccd')
    
    # Kiểm tra quyền sở hữu
    if user_role == 'NguoiDan' and phananh_cccd != user_cccd:
        flash('Bạn chỉ có thể sửa phản ánh của chính mình!', 'danger')
        return redirect(url_for('phananh_detail', maphananh=maphananh))
    
    if request.method == 'POST':
        tieude = request.form.get('tieude', '').strip()
        mota = request.form.get('mota', '').strip()
        loaiphananh = request.form.get('loaiphananh', '').strip()
        
        # Cán bộ có thể cập nhật trạng thái
        if user_role in ['CanBo', 'QuanLy']:
            trangthaiphananh = request.form.get('trangthaiphananh', 'ChuaXuLy')
            query_update = """
                UPDATE phananh 
                SET tieude = %s, mota = %s, loaiphananh = %s, 
                    trangthaiphananh = %s, thoigianxuly = CURRENT_TIMESTAMP
                WHERE maphananh = %s
            """
            result = execute_query(query_update, (tieude, mota, loaiphananh, trangthaiphananh, maphananh))
        else:
            # Người dân chỉ sửa nội dung
            query_update = """
                UPDATE phananh 
                SET tieude = %s, mota = %s, loaiphananh = %s
                WHERE maphananh = %s
            """
            result = execute_query(query_update, (tieude, mota, loaiphananh, maphananh))
        
        if result:
            flash('Đã cập nhật phản ánh thành công!', 'success')
            return redirect(url_for('phananh_detail', maphananh=maphananh))
        else:
            flash('Có lỗi xảy ra khi cập nhật!', 'danger')
    
    # GET: Load dữ liệu
    query = """
        SELECT 
            p.maphananh,
            p.tieude,
            p.mota,
            p.loaiphananh,
            p.trangthaiphananh,
            p.is_public,
            p.allow_comment,
            d.tinh,
            d.xaphuong,
            d.chitiet
        FROM phananh p
        LEFT JOIN diachi d ON p.madiachi = d.madiachi
        WHERE p.maphananh = %s
    """
    phananh = execute_query(query, (maphananh,), fetch_one=True)
    
    return render_template('phananh_edit.html', phananh=phananh)


@app.route('/phananh/delete/<int:maphananh>', methods=['POST'])
@login_required
def phananh_delete(maphananh):
    """Xóa phản ánh - Ownership check"""
    
    # Lấy thông tin phản ánh
    query_check = "SELECT cccd, tieude FROM phananh WHERE maphananh = %s"
    phananh = execute_query(query_check, (maphananh,), fetch_one=True)
    
    if not phananh:
        flash('Không tìm thấy phản ánh!', 'danger')
        return redirect(url_for('phananh_list'))
    
    phananh_cccd = phananh[0]
    tieude = phananh[1]
    user_role = session['user'].get('vaitro')
    user_cccd = session['user'].get('cccd')
    
    # Kiểm tra quyền sở hữu
    if user_role == 'NguoiDan' and phananh_cccd != user_cccd:
        flash('Bạn chỉ có thể xóa phản ánh của chính mình!', 'danger')
        return redirect(url_for('phananh_list'))
    
    # Xóa phản ánh
    delete_query = "DELETE FROM phananh WHERE maphananh = %s"
    result = execute_query(delete_query, (maphananh,))
    
    if result:
        flash(f'Đã xóa phản ánh "{tieude}" thành công!', 'success')
    else:
        flash('Có lỗi xảy ra khi xóa!', 'danger')
    
    return redirect(url_for('phananh_list'))


# ========== PHASE 3: QUẢN LÝ VẤN ĐỀ ==========

@app.route('/vande')
@login_required
@role_required(['CanBo', 'QuanLy'])
def vande_list():
    """Danh sách vấn đề - Chỉ Cán bộ/Quản lý"""
    
    # Lấy tham số filter
    trangthai = request.args.get('trangthai', '').strip()
    phanloai = request.args.get('phanloai', '').strip()
    search = request.args.get('search', '').strip()
    
    # Pagination
    per_page = 20
    try:
        page = int(request.args.get('page', 1))
        if page < 1:
            page = 1
    except (ValueError, TypeError):
        page = 1
    
    offset = (page - 1) * per_page
    
    # Xây dựng điều kiện WHERE
    where_conditions = []
    params = []
    
    if trangthai:
        where_conditions.append("v.trangthai = %s")
        params.append(trangthai)
    
    if phanloai:
        where_conditions.append("v.phanloai = %s")
        params.append(phanloai)
    
    if search:
        where_conditions.append("v.tenvande ILIKE %s")
        params.append(f'%{search}%')
    
    where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
    
    # Đếm tổng số
    query_count = f"""
        SELECT COUNT(*) 
        FROM vande v
        WHERE {where_clause}
    """
    total_count = execute_query(query_count, tuple(params), fetch_one=True)
    total_count = total_count[0] if total_count else 0
    total_pages = math.ceil(total_count / per_page) if total_count > 0 else 1
    
    # Query danh sách vấn đề với thống kê
    query_list = f"""
        SELECT 
            v.mavande,
            v.tenvande,
            v.phanloai,
            v.trangthai,
            v.ngaytao,
            v.ngaycapnhat,
            n.name AS ten_canbo,
            COUNT(p.maphananh) AS so_phananh,
            COUNT(DISTINCT p.cccd) AS so_nguoi,
            COALESCE(SUM(p.like_count), 0) AS tong_like,
            COALESCE(SUM(p.comment_count), 0) AS tong_comment
        FROM vande v
        LEFT JOIN nguoidung n ON v.cccd_canbo_xuly = n.cccd
        LEFT JOIN phananh p ON v.mavande = p.mavande
        WHERE {where_clause}
        GROUP BY v.mavande, v.tenvande, v.phanloai, v.trangthai, 
                 v.ngaytao, v.ngaycapnhat, n.name
        ORDER BY v.ngaytao DESC
        LIMIT %s OFFSET %s
    """
    
    params_list = params + [per_page, offset]
    ds_vande = execute_query(query_list, tuple(params_list), fetch_all=True)
    ds_vande = ds_vande if ds_vande else []
    
    return render_template('vande_list.html',
                         ds_vande=ds_vande,
                         page=page,
                         per_page=per_page,
                         total_pages=total_pages,
                         trangthai=trangthai,
                         phanloai=phanloai,
                         search=search)


@app.route('/vande/add', methods=['GET', 'POST'])
@login_required
@role_required(['CanBo', 'QuanLy'])
def vande_add():
    """Tạo vấn đề mới và gộp phản ánh - Chỉ Cán bộ/Quản lý"""
    
    if request.method == 'POST':
        tenvande = request.form.get('tenvande', '').strip()
        phanloai = request.form.get('phanloai', 'Khac')
        
        # Lấy danh sách maphananh[] từ form
        list_maphananh = request.form.getlist('maphananh[]')
        
        # Validate
        if not tenvande:
            flash('Vui lòng nhập tên vấn đề!', 'warning')
            return redirect(url_for('vande_add'))
        
        if not list_maphananh:
            flash('Vui lòng chọn ít nhất 1 phản ánh để gộp!', 'warning')
            return redirect(url_for('vande_add'))
        
        # Kiểm tra các phản ánh chưa thuộc vấn đề nào
        placeholders = ','.join(['%s'] * len(list_maphananh))
        query_check = f"""
            SELECT maphananh, tieude 
            FROM phananh 
            WHERE maphananh IN ({placeholders}) AND mavande IS NOT NULL
        """
        da_gop = execute_query(query_check, tuple(list_maphananh), fetch_all=True)
        
        if da_gop:
            tieude_da_gop = ', '.join([str(row[1]) for row in da_gop])
            flash(f'Các phản ánh sau đã thuộc vấn đề khác: {tieude_da_gop}', 'danger')
            return redirect(url_for('vande_add'))
        
        # Tạo vấn đề mới
        query_vande = """
            INSERT INTO vande (tenvande, phanloai, trangthai, cccd_canbo_xuly)
            VALUES (%s, %s, 'Moi', %s)
            RETURNING mavande
        """
        result = execute_query(
            query_vande,
            (tenvande, phanloai, session['user']['cccd']),
            fetch_one=True
        )
        
        if result:
            mavande = result[0]
            
            # Gộp các phản ánh vào vấn đề
            query_update = f"""
                UPDATE phananh 
                SET mavande = %s 
                WHERE maphananh IN ({placeholders})
            """
            params_update = [mavande] + list_maphananh
            execute_query(query_update, tuple(params_update))
            
            flash(f'Đã tạo vấn đề "{tenvande}" và gộp {len(list_maphananh)} phản ánh thành công!', 'success')
            return redirect(url_for('vande_detail', mavande=mavande))
        else:
            flash('Có lỗi xảy ra khi tạo vấn đề!', 'danger')
    
    # GET: Lấy danh sách phản ánh chưa gộp
    query_phananh = """
        SELECT 
            p.maphananh,
            p.tieude,
            p.loaiphananh,
            n.name AS nguoi_tao,
            p.thoigiantao,
            d.xaphuong,
            p.like_count,
            p.comment_count
        FROM phananh p
        LEFT JOIN nguoidung n ON p.cccd = n.cccd
        LEFT JOIN diachi d ON p.madiachi = d.madiachi
        WHERE p.mavande IS NULL
        ORDER BY p.thoigiantao DESC
        LIMIT 100
    """
    ds_phananh_chua_gop = execute_query(query_phananh, fetch_all=True)
    ds_phananh_chua_gop = ds_phananh_chua_gop if ds_phananh_chua_gop else []
    
    return render_template('vande_add.html', ds_phananh_chua_gop=ds_phananh_chua_gop)


@app.route('/vande/<int:mavande>')
@login_required
def vande_detail(mavande):
    """Chi tiết vấn đề - Cán bộ xem tất cả, Người dân chỉ xem vấn đề của phản ánh mình"""
    
    # Query thông tin vấn đề
    query_vande = """
        SELECT 
            v.mavande,
            v.tenvande,
            v.phanloai,
            v.trangthai,
            v.ketqua,
            v.ngaytao,
            v.ngaycapnhat,
            v.cccd_canbo_xuly,
            n.name AS ten_canbo,
            n.sdt AS sdt_canbo
        FROM vande v
        LEFT JOIN nguoidung n ON v.cccd_canbo_xuly = n.cccd
        WHERE v.mavande = %s
    """
    vande = execute_query(query_vande, (mavande,), fetch_one=True)
    
    if not vande:
        flash('Không tìm thấy vấn đề!', 'danger')
        return redirect(url_for('vande_list'))
    
    # Kiểm tra quyền xem
    user_role = session['user'].get('vaitro')
    user_cccd = session['user'].get('cccd')
    
    if user_role == 'NguoiDan':
        # Người dân chỉ xem được vấn đề của phản ánh mình
        query_check = """
            SELECT 1 FROM phananh 
            WHERE mavande = %s AND cccd = %s
        """
        has_permission = execute_query(query_check, (mavande, user_cccd), fetch_one=True)
        
        if not has_permission:
            flash('Bạn không có quyền xem vấn đề này!', 'danger')
            return redirect(url_for('phananh_list'))
    
    # Query danh sách phản ánh thuộc vấn đề
    query_phananh = """
        SELECT 
            p.maphananh,
            p.cccd,
            n.name AS nguoi_tao,
            p.tieude,
            p.loaiphananh,
            p.trangthaiphananh,
            p.thoigiantao,
            p.like_count,
            p.comment_count,
            p.view_count,
            d.xaphuong,
            d.chitiet
        FROM phananh p
        LEFT JOIN nguoidung n ON p.cccd = n.cccd
        LEFT JOIN diachi d ON p.madiachi = d.madiachi
        WHERE p.mavande = %s
        ORDER BY p.thoigiantao DESC
    """
    ds_phananh = execute_query(query_phananh, (mavande,), fetch_all=True)
    ds_phananh = ds_phananh if ds_phananh else []
    
    return render_template('vande_detail.html', vande=vande, ds_phananh=ds_phananh)


@app.route('/vande/<int:mavande>/update-status', methods=['POST'])
@login_required
@role_required(['CanBo', 'QuanLy'])
def vande_update_status(mavande):
    """
    Cập nhật trạng thái vấn đề và tự động:
    - Đồng bộ trạng thái sang tất cả phản ánh con
    - Gửi thông báo đến người dân
    - Gửi tin nhắn vào boxchat
    """
    
    trangthai_moi = request.form.get('trangthai', '').strip()
    ketqua = request.form.get('ketqua', '').strip()
    
    if not trangthai_moi:
        flash('Vui lòng chọn trạng thái!', 'warning')
        return redirect(url_for('vande_detail', mavande=mavande))
    
    # 1. Cập nhật vấn đề
    query_update_vande = """
        UPDATE vande 
        SET trangthai = %s, 
            ketqua = %s, 
            ngaycapnhat = CURRENT_TIMESTAMP 
        WHERE mavande = %s
        RETURNING tenvande
    """
    result = execute_query(query_update_vande, (trangthai_moi, ketqua, mavande), fetch_one=True)
    
    if not result:
        flash('Có lỗi xảy ra khi cập nhật vấn đề!', 'danger')
        return redirect(url_for('vande_detail', mavande=mavande))
    
    tenvande = result[0]
    
    # 2. Đồng bộ trạng thái sang tất cả phản ánh con
    query_update_phananh = """
        UPDATE phananh 
        SET trangthaiphananh = %s,
            thoigianxuly = CURRENT_TIMESTAMP
        WHERE mavande = %s
    """
    execute_query(query_update_phananh, (trangthai_moi, mavande))
    
    # 3. Lấy danh sách người dân bị ảnh hưởng
    query_affected_users = """
        SELECT DISTINCT p.cccd, n.name 
        FROM phananh p
        JOIN nguoidung n ON p.cccd = n.cccd
        WHERE p.mavande = %s
    """
    affected_users = execute_query(query_affected_users, (mavande,), fetch_all=True)
    affected_users = affected_users if affected_users else []
    
    # 4. Tạo nội dung thông báo
    noidung_thongbao = f"""
Vấn đề "{tenvande}" đã được cập nhật trạng thái: {trangthai_moi}.
"""
    
    if ketqua:
        noidung_thongbao += f"\nKết quả: {ketqua}"
    
    # 5. Gửi thông báo đến từng người
    for user in affected_users:
        cccd = user[0]
        
        # a) Insert vào bảng thông báo cá nhân
        query_notification = """
            INSERT INTO thongbao_nguoidung (cccd, noidung, loai, mavande)
            VALUES (%s, %s, 'VanDe', %s)
        """
        execute_query(query_notification, (cccd, noidung_thongbao, mavande))
        
        # b) Gửi tin nhắn vào boxchat (nếu tồn tại)
        query_boxchat = """
            SELECT b.maboxchat 
            FROM boxchat b
            JOIN phananh p ON b.maphananh = p.maphananh
            WHERE p.mavande = %s AND p.cccd = %s
            LIMIT 1
        """
        boxchat = execute_query(query_boxchat, (mavande, cccd), fetch_one=True)
        
        if boxchat:
            maboxchat = boxchat[0]
            query_insert_message = """
                INSERT INTO tinnhan (maboxchat, nguoigui, noidung, thoigiangui)
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            """
            execute_query(query_insert_message, (maboxchat, session['user']['cccd'], noidung_thongbao))
    
    flash(f'Đã cập nhật vấn đề và gửi thông báo đến {len(affected_users)} người dân!', 'success')
    return redirect(url_for('vande_detail', mavande=mavande))


@app.route('/vande/<int:mavande>/gop-them', methods=['POST'])
@login_required
@role_required(['CanBo', 'QuanLy'])
def vande_gop_them(mavande):
    """Gộp thêm phản ánh vào vấn đề đã có"""
    
    # Lấy danh sách maphananh[] từ form
    list_maphananh = request.form.getlist('maphananh[]')
    
    if not list_maphananh:
        flash('Vui lòng chọn ít nhất 1 phản ánh để gộp!', 'warning')
        return redirect(url_for('vande_detail', mavande=mavande))
    
    # Kiểm tra vấn đề tồn tại
    query_check_vande = "SELECT tenvande FROM vande WHERE mavande = %s"
    vande = execute_query(query_check_vande, (mavande,), fetch_one=True)
    
    if not vande:
        flash('Không tìm thấy vấn đề!', 'danger')
        return redirect(url_for('vande_list'))
    
    tenvande = vande[0]
    
    # Kiểm tra các phản ánh chưa thuộc vấn đề nào
    placeholders = ','.join(['%s'] * len(list_maphananh))
    query_check = f"""
        SELECT maphananh, tieude 
        FROM phananh 
        WHERE maphananh IN ({placeholders}) AND mavande IS NOT NULL
    """
    da_gop = execute_query(query_check, tuple(list_maphananh), fetch_all=True)
    
    if da_gop:
        tieude_da_gop = ', '.join([str(row[1]) for row in da_gop])
        flash(f'Các phản ánh sau đã thuộc vấn đề khác: {tieude_da_gop}', 'danger')
        return redirect(url_for('vande_detail', mavande=mavande))
    
    # Gộp các phản ánh vào vấn đề
    query_update = f"""
        UPDATE phananh 
        SET mavande = %s 
        WHERE maphananh IN ({placeholders})
    """
    params_update = [mavande] + list_maphananh
    result = execute_query(query_update, tuple(params_update))
    
    if result:
        flash(f'Đã gộp thêm {len(list_maphananh)} phản ánh vào vấn đề "{tenvande}"!', 'success')
    else:
        flash('Có lỗi xảy ra khi gộp phản ánh!', 'danger')
    
    return redirect(url_for('vande_detail', mavande=mavande))


@app.route('/vande/<int:mavande>/delete', methods=['POST'])
@login_required
@role_required(['CanBo', 'QuanLy'])
def vande_delete(mavande):
    """Xóa vấn đề - Chỉ Cán bộ/Quản lý"""
    
    # Lấy thông tin vấn đề
    query_vande = "SELECT tenvande FROM vande WHERE mavande = %s"
    vande = execute_query(query_vande, (mavande,), fetch_one=True)
    
    if not vande:
        flash('Không tìm thấy vấn đề!', 'danger')
        return redirect(url_for('vande_list'))
    
    tenvande = vande[0]
    
    # Hủy gộp các phản ánh (set mavande = NULL)
    query_ungop = "UPDATE phananh SET mavande = NULL WHERE mavande = %s"
    execute_query(query_ungop, (mavande,))
    
    # Xóa vấn đề
    query_delete = "DELETE FROM vande WHERE mavande = %s"
    result = execute_query(query_delete, (mavande,))
    
    if result:
        flash(f'Đã xóa vấn đề "{tenvande}" và hủy gộp các phản ánh!', 'success')
    else:
        flash('Có lỗi xảy ra khi xóa vấn đề!', 'danger')
    
    return redirect(url_for('vande_list'))


# ========== PHASE 4: SOCIAL FEATURES (LIKE, COMMENT, NEWS FEED) ==========

@app.route('/newsfeed')
@login_required
def newsfeed():
    """
    Hiển thị newsfeed - danh sách phản ánh công khai
    Sắp xếp theo hot_score (engagement) hoặc thoigiantao mới nhất
    """
    user = session.get('user')
    user_role = user['vaitro']
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page
    
    # Sort options: 'hot' (mặc định) hoặc 'new'
    sort_by = request.args.get('sort', 'hot')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Sử dụng view_newsfeed đã tạo trong Phase 1
        if sort_by == 'new':
            order_clause = "ORDER BY thoigiantao DESC"
        else:
            # Hot score: like_count*2 + comment_count + view_count*0.1
            order_clause = "ORDER BY hot_score DESC, thoigiantao DESC"
        
        # Lấy danh sách phản ánh
        cur.execute(f"""
            SELECT * FROM view_newsfeed
            {order_clause}
            LIMIT %s OFFSET %s
        """, (per_page, offset))
        
        phananh_list = cur.fetchall()
        
        # Đếm tổng số phản ánh công khai
        cur.execute("SELECT COUNT(*) FROM phananh WHERE is_public = TRUE")
        total = cur.fetchone()[0]
        total_pages = (total + per_page - 1) // per_page
        
        # Kiểm tra xem user đã like các post nào chưa
        if phananh_list:
            maphananh_list = [p[0] for p in phananh_list]  # Assuming maphananh is first column
            placeholders = ','.join(['%s'] * len(maphananh_list))
            cur.execute(f"""
                SELECT maphananh FROM like_post
                WHERE maphananh IN ({placeholders}) AND cccd = %s
            """, (*maphananh_list, user['cccd']))
            
            liked_posts = set(row[0] for row in cur.fetchall())
        else:
            liked_posts = set()
        
        conn.close()
        
        return render_template('newsfeed.html',
                             phananh_list=phananh_list,
                             liked_posts=liked_posts,
                             sort_by=sort_by,
                             page=page,
                             total_pages=total_pages)
    
    except Exception as e:
        conn.close()
        flash(f'Lỗi khi tải newsfeed: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))


@app.route('/phananh/<int:maphananh>/like', methods=['POST'])
@login_required
def phananh_like(maphananh):
    """
    Like một phản ánh
    """
    user = session.get('user')
    cccd = user['cccd']
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Kiểm tra phản ánh tồn tại
        cur.execute("SELECT maphananh FROM phananh WHERE maphananh = %s", (maphananh,))
        if not cur.fetchone():
            conn.close()
            flash('Phản ánh không tồn tại!', 'danger')
            return redirect(url_for('newsfeed'))
        
        # Kiểm tra đã like chưa
        cur.execute("""
            SELECT malike FROM like_post
            WHERE maphananh = %s AND cccd = %s
        """, (maphananh, cccd))
        
        if cur.fetchone():
            conn.close()
            flash('Bạn đã like phản ánh này rồi!', 'warning')
            return redirect(request.referrer or url_for('newsfeed'))
        
        # Thêm like
        cur.execute("""
            INSERT INTO like_post (maphananh, cccd, thoigian)
            VALUES (%s, %s, NOW())
        """, (maphananh, cccd))
        
        # Tăng like_count
        cur.execute("""
            UPDATE phananh
            SET like_count = like_count + 1
            WHERE maphananh = %s
        """, (maphananh,))
        
        conn.commit()
        conn.close()
        
        flash('Đã like phản ánh!', 'success')
        return redirect(request.referrer or url_for('newsfeed'))
    
    except Exception as e:
        conn.rollback()
        conn.close()
        flash(f'Lỗi khi like phản ánh: {str(e)}', 'danger')
        return redirect(request.referrer or url_for('newsfeed'))


@app.route('/phananh/<int:maphananh>/unlike', methods=['POST'])
@login_required
def phananh_unlike(maphananh):
    """
    Unlike một phản ánh
    """
    user = session.get('user')
    cccd = user['cccd']
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Kiểm tra đã like chưa
        cur.execute("""
            SELECT malike FROM like_post
            WHERE maphananh = %s AND cccd = %s
        """, (maphananh, cccd))
        
        if not cur.fetchone():
            conn.close()
            flash('Bạn chưa like phản ánh này!', 'warning')
            return redirect(request.referrer or url_for('newsfeed'))
        
        # Xóa like
        cur.execute("""
            DELETE FROM like_post
            WHERE maphananh = %s AND cccd = %s
        """, (maphananh, cccd))
        
        # Giảm like_count
        cur.execute("""
            UPDATE phananh
            SET like_count = GREATEST(like_count - 1, 0)
            WHERE maphananh = %s
        """, (maphananh,))
        
        conn.commit()
        conn.close()
        
        flash('Đã bỏ like phản ánh!', 'success')
        return redirect(request.referrer or url_for('newsfeed'))
    
    except Exception as e:
        conn.rollback()
        conn.close()
        flash(f'Lỗi khi unlike phản ánh: {str(e)}', 'danger')
        return redirect(request.referrer or url_for('newsfeed'))


@app.route('/phananh/<int:maphananh>/comment', methods=['POST'])
@login_required
def comment_add(maphananh):
    """
    Thêm bình luận cho phản ánh
    Support nested comments (parent_id)
    """
    user = session.get('user')
    cccd = user['cccd']
    noidung = request.form.get('noidung', '').strip()
    parent_id = request.form.get('parent_id', None)  # Cho nested reply
    
    if not noidung:
        flash('Nội dung bình luận không được để trống!', 'warning')
        return redirect(request.referrer or url_for('newsfeed'))
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Kiểm tra phản ánh tồn tại
        cur.execute("SELECT maphananh FROM phananh WHERE maphananh = %s", (maphananh,))
        if not cur.fetchone():
            conn.close()
            flash('Phản ánh không tồn tại!', 'danger')
            return redirect(url_for('newsfeed'))
        
        # Nếu có parent_id, kiểm tra comment cha tồn tại
        if parent_id:
            cur.execute("""
                SELECT mabinhluan FROM binhluan
                WHERE mabinhluan = %s AND maphananh = %s
            """, (parent_id, maphananh))
            if not cur.fetchone():
                conn.close()
                flash('Bình luận cha không tồn tại!', 'danger')
                return redirect(request.referrer or url_for('newsfeed'))
        
        # Thêm bình luận
        if parent_id:
            cur.execute("""
                INSERT INTO binhluan (maphananh, cccd, noidung, thoigian, parent_id)
                VALUES (%s, %s, %s, NOW(), %s)
            """, (maphananh, cccd, noidung, parent_id))
        else:
            cur.execute("""
                INSERT INTO binhluan (maphananh, cccd, noidung, thoigian)
                VALUES (%s, %s, %s, NOW())
            """, (maphananh, cccd, noidung))
        
        # Tăng comment_count
        cur.execute("""
            UPDATE phananh
            SET comment_count = comment_count + 1
            WHERE maphananh = %s
        """, (maphananh,))
        
        conn.commit()
        conn.close()
        
        flash('Đã thêm bình luận!', 'success')
        return redirect(request.referrer or url_for('phananh_detail', maphananh=maphananh))
    
    except Exception as e:
        conn.rollback()
        conn.close()
        flash(f'Lỗi khi thêm bình luận: {str(e)}', 'danger')
        return redirect(request.referrer or url_for('newsfeed'))


@app.route('/phananh/<int:maphananh>/comments')
@login_required
def comment_list(maphananh):
    """
    Lấy danh sách bình luận của phản ánh
    Trả về JSON cho AJAX loading
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Lấy comments (không bao gồm hidden comments)
        cur.execute("""
            SELECT 
                b.mabinhluan,
                b.noidung,
                b.thoigian,
                b.parent_id,
                b.is_hidden,
                n.cccd,
                n.hovaten
            FROM binhluan b
            JOIN nguoidung n ON b.cccd = n.cccd
            WHERE b.maphananh = %s AND b.is_hidden = FALSE
            ORDER BY b.thoigian ASC
        """, (maphananh,))
        
        comments = cur.fetchall()
        conn.close()
        
        # Format response
        comments_list = []
        for c in comments:
            comments_list.append({
                'mabinhluan': c[0],
                'noidung': c[1],
                'thoigian': c[2].strftime('%d/%m/%Y %H:%M') if c[2] else '',
                'parent_id': c[3],
                'cccd': c[5],
                'hovaten': c[6]
            })
        
        return jsonify({'success': True, 'comments': comments_list})
    
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'message': str(e)})


@app.route('/comment/<int:mabinhluan>/hide', methods=['POST'])
@login_required
@role_required(['CanBo', 'QuanLy'])
def comment_hide(mabinhluan):
    """
    Ẩn bình luận vi phạm (chỉ CanBo/QuanLy)
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Kiểm tra comment tồn tại
        cur.execute("""
            SELECT maphananh FROM binhluan
            WHERE mabinhluan = %s
        """, (mabinhluan,))
        
        result = cur.fetchone()
        if not result:
            conn.close()
            flash('Bình luận không tồn tại!', 'danger')
            return redirect(request.referrer or url_for('newsfeed'))
        
        maphananh = result[0]
        
        # Ẩn comment
        cur.execute("""
            UPDATE binhluan
            SET is_hidden = TRUE
            WHERE mabinhluan = %s
        """, (mabinhluan,))
        
        # Giảm comment_count
        cur.execute("""
            UPDATE phananh
            SET comment_count = GREATEST(comment_count - 1, 0)
            WHERE maphananh = %s
        """, (maphananh,))
        
        conn.commit()
        conn.close()
        
        flash('Đã ẩn bình luận vi phạm!', 'success')
        return redirect(request.referrer or url_for('phananh_detail', maphananh=maphananh))
    
    except Exception as e:
        conn.rollback()
        conn.close()
        flash(f'Lỗi khi ẩn bình luận: {str(e)}', 'danger')
        return redirect(request.referrer or url_for('newsfeed'))


# ========== PHASE 5: CHAT & NOTIFICATION SYSTEM ==========

@app.route('/chat')
@login_required
def chat_list():
    """
    Danh sách các boxchat của user
    Hiển thị tin nhắn cuối cùng và số tin chưa đọc
    """
    user = session.get('user')
    cccd = user['cccd']
    user_role = user['vaitro']
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Lấy danh sách boxchat mà user tham gia
        # JOIN với tin nhắn cuối cùng và đếm tin chưa đọc
        cur.execute("""
            WITH latest_messages AS (
                SELECT DISTINCT ON (maboxchat)
                    maboxchat,
                    noidung as last_message,
                    thoigiangui as last_time,
                    nguoigui as last_sender
                FROM tinnhan
                ORDER BY maboxchat, thoigiangui DESC
            ),
            unread_counts AS (
                SELECT 
                    maboxchat,
                    COUNT(*) as unread_count
                FROM tinnhan
                WHERE is_read = FALSE AND nguoigui != %s
                GROUP BY maboxchat
            )
            SELECT 
                b.maboxchat,
                b.maphananh,
                p.tieude as phananh_title,
                lm.last_message,
                lm.last_time,
                lm.last_sender,
                n.hovaten as last_sender_name,
                COALESCE(uc.unread_count, 0) as unread_count
            FROM boxchat b
            LEFT JOIN phananh p ON b.maphananh = p.maphananh
            LEFT JOIN latest_messages lm ON b.maboxchat = lm.maboxchat
            LEFT JOIN nguoidung n ON lm.last_sender = n.cccd
            LEFT JOIN unread_counts uc ON b.maboxchat = uc.maboxchat
            WHERE b.cccd_nguoidung = %s OR b.cccd_canbo = %s
            ORDER BY lm.last_time DESC NULLS LAST
        """, (cccd, cccd, cccd))
        
        boxchat_list = cur.fetchall()
        conn.close()
        
        return render_template('chat_list.html', boxchat_list=boxchat_list)
    
    except Exception as e:
        conn.close()
        flash(f'Lỗi khi tải danh sách chat: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))


@app.route('/chat/<int:maboxchat>')
@login_required
def chat_detail(maboxchat):
    """
    Chi tiết boxchat - hiển thị tất cả tin nhắn
    """
    user = session.get('user')
    cccd = user['cccd']
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Kiểm tra quyền truy cập boxchat
        cur.execute("""
            SELECT 
                b.maboxchat,
                b.maphananh,
                b.cccd_nguoidung,
                b.cccd_canbo,
                p.tieude,
                n1.hovaten as nguoidung_name,
                n2.hovaten as canbo_name
            FROM boxchat b
            LEFT JOIN phananh p ON b.maphananh = p.maphananh
            LEFT JOIN nguoidung n1 ON b.cccd_nguoidung = n1.cccd
            LEFT JOIN nguoidung n2 ON b.cccd_canbo = n2.cccd
            WHERE b.maboxchat = %s
        """, (maboxchat,))
        
        boxchat = cur.fetchone()
        
        if not boxchat:
            conn.close()
            flash('Boxchat không tồn tại!', 'danger')
            return redirect(url_for('chat_list'))
        
        # Kiểm tra quyền: chỉ người trong boxchat mới được xem
        cccd_nguoidung = boxchat[2]
        cccd_canbo = boxchat[3]
        
        if cccd not in [cccd_nguoidung, cccd_canbo]:
            conn.close()
            flash('Bạn không có quyền truy cập boxchat này!', 'danger')
            return redirect(url_for('chat_list'))
        
        # Lấy tất cả tin nhắn
        cur.execute("""
            SELECT 
                t.matinnhan,
                t.nguoigui,
                t.noidung,
                t.thoigiangui,
                t.is_read,
                n.hovaten as sender_name
            FROM tinnhan t
            JOIN nguoidung n ON t.nguoigui = n.cccd
            WHERE t.maboxchat = %s
            ORDER BY t.thoigiangui ASC
        """, (maboxchat,))
        
        messages = cur.fetchall()
        
        # Đánh dấu tất cả tin nhắn là đã đọc (trừ tin nhắn do mình gửi)
        cur.execute("""
            UPDATE tinnhan
            SET is_read = TRUE
            WHERE maboxchat = %s AND nguoigui != %s AND is_read = FALSE
        """, (maboxchat, cccd))
        
        conn.commit()
        conn.close()
        
        return render_template('chat_detail.html',
                             boxchat=boxchat,
                             messages=messages,
                             current_cccd=cccd)
    
    except Exception as e:
        conn.close()
        flash(f'Lỗi khi tải chat: {str(e)}', 'danger')
        return redirect(url_for('chat_list'))


@app.route('/chat/<int:maboxchat>/send', methods=['POST'])
@login_required
def chat_send_message(maboxchat):
    """
    Gửi tin nhắn trong boxchat
    """
    user = session.get('user')
    cccd = user['cccd']
    noidung = request.form.get('noidung', '').strip()
    
    if not noidung:
        flash('Nội dung tin nhắn không được để trống!', 'warning')
        return redirect(url_for('chat_detail', maboxchat=maboxchat))
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Kiểm tra quyền gửi tin nhắn (chỉ người trong boxchat)
        cur.execute("""
            SELECT cccd_nguoidung, cccd_canbo
            FROM boxchat
            WHERE maboxchat = %s
        """, (maboxchat,))
        
        boxchat = cur.fetchone()
        
        if not boxchat:
            conn.close()
            flash('Boxchat không tồn tại!', 'danger')
            return redirect(url_for('chat_list'))
        
        cccd_nguoidung = boxchat[0]
        cccd_canbo = boxchat[1]
        
        if cccd not in [cccd_nguoidung, cccd_canbo]:
            conn.close()
            flash('Bạn không có quyền gửi tin nhắn trong boxchat này!', 'danger')
            return redirect(url_for('chat_list'))
        
        # Thêm tin nhắn
        cur.execute("""
            INSERT INTO tinnhan (maboxchat, nguoigui, noidung, thoigiangui, is_read)
            VALUES (%s, %s, %s, NOW(), FALSE)
        """, (maboxchat, cccd, noidung))
        
        conn.commit()
        conn.close()
        
        flash('Đã gửi tin nhắn!', 'success')
        return redirect(url_for('chat_detail', maboxchat=maboxchat))
    
    except Exception as e:
        conn.rollback()
        conn.close()
        flash(f'Lỗi khi gửi tin nhắn: {str(e)}', 'danger')
        return redirect(url_for('chat_detail', maboxchat=maboxchat))


@app.route('/notifications')
@login_required
def notifications():
    """
    Danh sách thông báo của user
    """
    user = session.get('user')
    cccd = user['cccd']
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page
    
    # Filter: 'all' hoặc 'unread'
    filter_type = request.args.get('filter', 'all')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Build WHERE clause
        where_clause = "WHERE tn.cccd = %s"
        params = [cccd]
        
        if filter_type == 'unread':
            where_clause += " AND tn.trangthai_doc = FALSE"
        
        # Lấy danh sách thông báo
        cur.execute(f"""
            SELECT 
                tn.mathongbao_nguoidung,
                tn.noidung,
                tn.loai,
                tn.thoigian,
                tn.trangthai_doc,
                tn.mavande,
                tn.maphananh,
                v.tenvande,
                p.tieude as phananh_title
            FROM thongbao_nguoidung tn
            LEFT JOIN vande v ON tn.mavande = v.mavande
            LEFT JOIN phananh p ON tn.maphananh = p.maphananh
            {where_clause}
            ORDER BY tn.thoigian DESC
            LIMIT %s OFFSET %s
        """, params + [per_page, offset])
        
        notification_list = cur.fetchall()
        
        # Đếm tổng số thông báo
        cur.execute(f"""
            SELECT COUNT(*)
            FROM thongbao_nguoidung tn
            {where_clause}
        """, params)
        
        total = cur.fetchone()[0]
        total_pages = (total + per_page - 1) // per_page
        
        # Đếm số thông báo chưa đọc
        cur.execute("""
            SELECT COUNT(*)
            FROM thongbao_nguoidung
            WHERE cccd = %s AND trangthai_doc = FALSE
        """, (cccd,))
        
        unread_count = cur.fetchone()[0]
        
        conn.close()
        
        return render_template('notifications.html',
                             notification_list=notification_list,
                             unread_count=unread_count,
                             filter_type=filter_type,
                             page=page,
                             total_pages=total_pages)
    
    except Exception as e:
        conn.close()
        flash(f'Lỗi khi tải thông báo: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))


@app.route('/notification/<int:mathongbao_nguoidung>/read', methods=['POST'])
@login_required
def notification_mark_read(mathongbao_nguoidung):
    """
    Đánh dấu một thông báo là đã đọc
    """
    user = session.get('user')
    cccd = user['cccd']
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Kiểm tra quyền sở hữu
        cur.execute("""
            SELECT mathongbao_nguoidung
            FROM thongbao_nguoidung
            WHERE mathongbao_nguoidung = %s AND cccd = %s
        """, (mathongbao_nguoidung, cccd))
        
        if not cur.fetchone():
            conn.close()
            return jsonify({'success': False, 'message': 'Thông báo không tồn tại hoặc không thuộc về bạn!'})
        
        # Đánh dấu đã đọc
        cur.execute("""
            UPDATE thongbao_nguoidung
            SET trangthai_doc = TRUE
            WHERE mathongbao_nguoidung = %s
        """, (mathongbao_nguoidung,))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Đã đánh dấu đã đọc!'})
    
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'success': False, 'message': str(e)})


@app.route('/notifications/mark_all_read', methods=['POST'])
@login_required
def notifications_mark_all_read():
    """
    Đánh dấu tất cả thông báo là đã đọc
    """
    user = session.get('user')
    cccd = user['cccd']
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Đánh dấu tất cả thông báo chưa đọc
        cur.execute("""
            UPDATE thongbao_nguoidung
            SET trangthai_doc = TRUE
            WHERE cccd = %s AND trangthai_doc = FALSE
        """, (cccd,))
        
        rows_affected = cur.rowcount
        
        conn.commit()
        conn.close()
        
        flash(f'Đã đánh dấu {rows_affected} thông báo là đã đọc!', 'success')
        return redirect(url_for('notifications'))
    
    except Exception as e:
        conn.rollback()
        conn.close()
        flash(f'Lỗi khi đánh dấu thông báo: {str(e)}', 'danger')
        return redirect(url_for('notifications'))


# ========== PHASE 6: REPORTS & STATISTICS ==========

@app.route('/reports/overview')
@login_required
@role_required(['CanBo', 'QuanLy'])
def reports_overview():
    """
    Tổng quan thống kê về phản ánh và vấn đề
    """
    # Tham số thời gian
    from_date = request.args.get('from_date', '')
    to_date = request.args.get('to_date', '')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Build WHERE clause cho filter thời gian
        where_clause_phananh = ""
        where_clause_vande = ""
        params = []
        
        if from_date and to_date:
            where_clause_phananh = "WHERE thoigiantao BETWEEN %s AND %s"
            where_clause_vande = "WHERE ngaytao BETWEEN %s AND %s"
            params = [from_date, to_date]
        
        # 1. Thống kê phản ánh
        cur.execute(f"""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN trangthaiphananh = 'Mới' THEN 1 END) as moi,
                COUNT(CASE WHEN trangthaiphananh = 'Đang xử lý' THEN 1 END) as dangxuly,
                COUNT(CASE WHEN trangthaiphananh = 'Đã xử lý' THEN 1 END) as daxuly,
                COUNT(CASE WHEN trangthaiphananh = 'Đã từ chối' THEN 1 END) as tuchoi,
                COUNT(CASE WHEN is_public = TRUE THEN 1 END) as public_count,
                SUM(like_count) as total_likes,
                SUM(comment_count) as total_comments,
                SUM(view_count) as total_views
            FROM phananh
            {where_clause_phananh}
        """, params)
        
        phananh_stats = cur.fetchone()
        
        # 2. Thống kê vấn đề
        cur.execute(f"""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN trangthai = 'Mới' THEN 1 END) as moi,
                COUNT(CASE WHEN trangthai = 'Đang xử lý' THEN 1 END) as dangxuly,
                COUNT(CASE WHEN trangthai = 'Đã giải quyết' THEN 1 END) as dagiaiquyet,
                COUNT(CASE WHEN trangthai = 'Đóng' THEN 1 END) as dong
            FROM vande
            {where_clause_vande}
        """, params)
        
        vande_stats = cur.fetchone()
        
        # 3. Thống kê theo phân loại vấn đề
        cur.execute(f"""
            SELECT 
                phanloai,
                COUNT(*) as count
            FROM vande
            {where_clause_vande}
            GROUP BY phanloai
            ORDER BY count DESC
        """, params)
        
        phanloai_stats = cur.fetchall()
        
        # 4. Xu hướng theo tháng (12 tháng gần nhất)
        cur.execute("""
            SELECT 
                TO_CHAR(thoigiantao, 'YYYY-MM') as month,
                COUNT(*) as count
            FROM phananh
            WHERE thoigiantao >= NOW() - INTERVAL '12 months'
            GROUP BY month
            ORDER BY month DESC
            LIMIT 12
        """)
        
        monthly_trend = cur.fetchall()
        
        # 5. Top 5 cán bộ xử lý nhiều vấn đề nhất
        cur.execute(f"""
            SELECT 
                n.hovaten,
                n.cccd,
                COUNT(v.mavande) as solved_count
            FROM vande v
            JOIN nguoidung n ON v.cccd_canbo_xuly = n.cccd
            {where_clause_vande}
            GROUP BY n.hovaten, n.cccd
            ORDER BY solved_count DESC
            LIMIT 5
        """, params)
        
        top_canbo = cur.fetchall()
        
        conn.close()
        
        return render_template('reports_overview.html',
                             phananh_stats=phananh_stats,
                             vande_stats=vande_stats,
                             phanloai_stats=phanloai_stats,
                             monthly_trend=monthly_trend,
                             top_canbo=top_canbo,
                             from_date=from_date,
                             to_date=to_date)
    
    except Exception as e:
        conn.close()
        flash(f'Lỗi khi tải báo cáo: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))


@app.route('/reports/phananh')
@login_required
@role_required(['CanBo', 'QuanLy'])
def reports_phananh():
    """
    Thống kê chi tiết về phản ánh
    """
    # Tham số
    from_date = request.args.get('from_date', '')
    to_date = request.args.get('to_date', '')
    trangthai = request.args.get('trangthai', '')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Build WHERE clause
        where_parts = []
        params = []
        
        if from_date and to_date:
            where_parts.append("thoigiantao BETWEEN %s AND %s")
            params.extend([from_date, to_date])
        
        if trangthai:
            where_parts.append("trangthaiphananh = %s")
            params.append(trangthai)
        
        where_clause = "WHERE " + " AND ".join(where_parts) if where_parts else ""
        
        # 1. Thống kê theo trạng thái
        cur.execute(f"""
            SELECT 
                trangthaiphananh,
                COUNT(*) as count,
                ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
            FROM phananh
            {where_clause}
            GROUP BY trangthaiphananh
            ORDER BY count DESC
        """, params)
        
        status_stats = cur.fetchall()
        
        # 2. Thống kê theo ngày (7 ngày gần nhất)
        cur.execute(f"""
            SELECT 
                DATE(thoigiantao) as date,
                COUNT(*) as count,
                COUNT(CASE WHEN is_public = TRUE THEN 1 END) as public_count
            FROM phananh
            {where_clause}
            GROUP BY DATE(thoigiantao)
            ORDER BY date DESC
            LIMIT 30
        """, params)
        
        daily_stats = cur.fetchall()
        
        # 3. Top 10 phản ánh có engagement cao nhất
        cur.execute(f"""
            SELECT 
                maphananh,
                tieude,
                like_count,
                comment_count,
                view_count,
                (like_count * 2 + comment_count + view_count * 0.1) as engagement_score
            FROM phananh
            {where_clause}
            ORDER BY engagement_score DESC
            LIMIT 10
        """, params)
        
        top_engagement = cur.fetchall()
        
        # 4. Thống kê phản ánh công khai vs riêng tư
        cur.execute(f"""
            SELECT 
                CASE WHEN is_public THEN 'Công khai' ELSE 'Riêng tư' END as type,
                COUNT(*) as count
            FROM phananh
            {where_clause}
            GROUP BY is_public
        """, params)
        
        privacy_stats = cur.fetchall()
        
        conn.close()
        
        return render_template('reports_phananh.html',
                             status_stats=status_stats,
                             daily_stats=daily_stats,
                             top_engagement=top_engagement,
                             privacy_stats=privacy_stats,
                             from_date=from_date,
                             to_date=to_date,
                             trangthai=trangthai)
    
    except Exception as e:
        conn.close()
        flash(f'Lỗi khi tải báo cáo phản ánh: {str(e)}', 'danger')
        return redirect(url_for('reports_overview'))


@app.route('/reports/vande')
@login_required
@role_required(['CanBo', 'QuanLy'])
def reports_vande():
    """
    Thống kê hiệu suất xử lý vấn đề
    """
    from_date = request.args.get('from_date', '')
    to_date = request.args.get('to_date', '')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Build WHERE clause
        where_clause = ""
        params = []
        
        if from_date and to_date:
            where_clause = "WHERE ngaytao BETWEEN %s AND %s"
            params = [from_date, to_date]
        
        # 1. Tỷ lệ giải quyết
        cur.execute(f"""
            SELECT 
                trangthai,
                COUNT(*) as count,
                ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
            FROM vande
            {where_clause}
            GROUP BY trangthai
        """, params)
        
        resolution_rate = cur.fetchall()
        
        # 2. Thời gian xử lý trung bình (ngày)
        cur.execute(f"""
            SELECT 
                phanloai,
                COUNT(*) as total_issues,
                ROUND(AVG(EXTRACT(EPOCH FROM (ngaycapnhat - ngaytao)) / 86400), 1) as avg_days
            FROM vande
            {where_clause if where_clause else 'WHERE'} 
            {' AND ' if where_clause else ''} ngaycapnhat IS NOT NULL
            GROUP BY phanloai
            ORDER BY avg_days DESC
        """, params)
        
        avg_resolution_time = cur.fetchall()
        
        # 3. Thống kê theo cán bộ xử lý
        cur.execute(f"""
            SELECT 
                n.hovaten,
                n.cccd,
                COUNT(v.mavande) as total_handled,
                COUNT(CASE WHEN v.trangthai = 'Đã giải quyết' THEN 1 END) as resolved,
                COUNT(CASE WHEN v.trangthai = 'Đóng' THEN 1 END) as closed,
                ROUND(AVG(EXTRACT(EPOCH FROM (v.ngaycapnhat - v.ngaytao)) / 86400), 1) as avg_days
            FROM vande v
            JOIN nguoidung n ON v.cccd_canbo_xuly = n.cccd
            {where_clause}
            GROUP BY n.hovaten, n.cccd
            ORDER BY total_handled DESC
        """, params)
        
        canbo_performance = cur.fetchall()
        
        # 4. Thống kê theo phân loại
        cur.execute(f"""
            SELECT 
                phanloai,
                COUNT(*) as total,
                COUNT(CASE WHEN trangthai IN ('Đã giải quyết', 'Đóng') THEN 1 END) as resolved
            FROM vande
            {where_clause}
            GROUP BY phanloai
            ORDER BY total DESC
        """, params)
        
        category_stats = cur.fetchall()
        
        conn.close()
        
        return render_template('reports_vande.html',
                             resolution_rate=resolution_rate,
                             avg_resolution_time=avg_resolution_time,
                             canbo_performance=canbo_performance,
                             category_stats=category_stats,
                             from_date=from_date,
                             to_date=to_date)
    
    except Exception as e:
        conn.close()
        flash(f'Lỗi khi tải báo cáo vấn đề: {str(e)}', 'danger')
        return redirect(url_for('reports_overview'))


@app.route('/reports/engagement')
@login_required
@role_required(['CanBo', 'QuanLy'])
def reports_engagement():
    """
    Thống kê tương tác người dùng
    """
    from_date = request.args.get('from_date', '')
    to_date = request.args.get('to_date', '')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Build WHERE clause
        where_clause = ""
        params = []
        
        if from_date and to_date:
            where_clause = "WHERE thoigiantao BETWEEN %s AND %s"
            params = [from_date, to_date]
        
        # 1. Tổng quan tương tác
        cur.execute(f"""
            SELECT 
                SUM(like_count) as total_likes,
                SUM(comment_count) as total_comments,
                SUM(view_count) as total_views,
                AVG(like_count) as avg_likes,
                AVG(comment_count) as avg_comments,
                AVG(view_count) as avg_views
            FROM phananh
            {where_clause}
        """, params)
        
        engagement_overview = cur.fetchone()
        
        # 2. Top 10 bài viết hot nhất
        cur.execute(f"""
            SELECT 
                p.maphananh,
                p.tieude,
                p.like_count,
                p.comment_count,
                p.view_count,
                n.hovaten,
                (p.like_count * 2 + p.comment_count + p.view_count * 0.1) as hot_score
            FROM phananh p
            JOIN nguoidung n ON p.cccd = n.cccd
            {where_clause}
            ORDER BY hot_score DESC
            LIMIT 10
        """, params)
        
        top_posts = cur.fetchall()
        
        # 3. Top 10 người dùng tích cực nhất (nhiều phản ánh + like + comment)
        cur.execute(f"""
            SELECT 
                n.hovaten,
                n.cccd,
                COUNT(DISTINCT p.maphananh) as post_count,
                COUNT(DISTINCT l.malike) as like_count,
                COUNT(DISTINCT b.mabinhluan) as comment_count,
                (COUNT(DISTINCT p.maphananh) * 3 + 
                 COUNT(DISTINCT l.malike) + 
                 COUNT(DISTINCT b.mabinhluan) * 2) as activity_score
            FROM nguoidung n
            LEFT JOIN phananh p ON n.cccd = p.cccd {' AND p.thoigiantao BETWEEN %s AND %s' if params else ''}
            LEFT JOIN like_post l ON n.cccd = l.cccd
            LEFT JOIN binhluan b ON n.cccd = b.cccd
            WHERE n.vaitro = 'NguoiDan'
            GROUP BY n.hovaten, n.cccd
            ORDER BY activity_score DESC
            LIMIT 10
        """, params if params else [])
        
        top_users = cur.fetchall()
        
        # 4. Thống kê tương tác theo ngày
        cur.execute(f"""
            SELECT 
                DATE(thoigiantao) as date,
                SUM(like_count) as daily_likes,
                SUM(comment_count) as daily_comments,
                SUM(view_count) as daily_views
            FROM phananh
            {where_clause}
            GROUP BY DATE(thoigiantao)
            ORDER BY date DESC
            LIMIT 30
        """, params)
        
        daily_engagement = cur.fetchall()
        
        conn.close()
        
        return render_template('reports_engagement.html',
                             engagement_overview=engagement_overview,
                             top_posts=top_posts,
                             top_users=top_users,
                             daily_engagement=daily_engagement,
                             from_date=from_date,
                             to_date=to_date)
    
    except Exception as e:
        conn.close()
        flash(f'Lỗi khi tải báo cáo tương tác: {str(e)}', 'danger')
        return redirect(url_for('reports_overview'))


@app.route('/reports/export')
@login_required
@role_required(['CanBo', 'QuanLy'])
def reports_export():
    """
    Xuất báo cáo ra file Excel
    """
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    from io import BytesIO
    from datetime import datetime
    
    report_type = request.args.get('type', 'overview')  # overview, phananh, vande
    from_date = request.args.get('from_date', '')
    to_date = request.args.get('to_date', '')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        wb = Workbook()
        ws = wb.active
        
        # Header style
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF")
        
        if report_type == 'phananh':
            ws.title = "Báo cáo Phản ánh"
            
            # Build WHERE
            where_parts = []
            params = []
            if from_date and to_date:
                where_parts.append("thoigiantao BETWEEN %s AND %s")
                params.extend([from_date, to_date])
            where_clause = "WHERE " + " AND ".join(where_parts) if where_parts else ""
            
            # Headers
            headers = ["Mã PA", "Tiêu đề", "Người gửi", "Trạng thái", "Công khai", 
                      "Likes", "Comments", "Views", "Ngày tạo"]
            ws.append(headers)
            
            # Style headers
            for cell in ws[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal='center')
            
            # Data
            cur.execute(f"""
                SELECT 
                    p.maphananh,
                    p.tieude,
                    n.hovaten,
                    p.trangthaiphananh,
                    CASE WHEN p.is_public THEN 'Có' ELSE 'Không' END,
                    p.like_count,
                    p.comment_count,
                    p.view_count,
                    p.thoigiantao
                FROM phananh p
                JOIN nguoidung n ON p.cccd = n.cccd
                {where_clause}
                ORDER BY p.thoigiantao DESC
            """, params)
            
            for row in cur.fetchall():
                ws.append(row)
        
        elif report_type == 'vande':
            ws.title = "Báo cáo Vấn đề"
            
            where_clause = ""
            params = []
            if from_date and to_date:
                where_clause = "WHERE v.ngaytao BETWEEN %s AND %s"
                params = [from_date, to_date]
            
            headers = ["Mã VĐ", "Tên vấn đề", "Phân loại", "Trạng thái", 
                      "Cán bộ xử lý", "Kết quả", "Ngày tạo", "Ngày cập nhật"]
            ws.append(headers)
            
            for cell in ws[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal='center')
            
            cur.execute(f"""
                SELECT 
                    v.mavande,
                    v.tenvande,
                    v.phanloai,
                    v.trangthai,
                    n.hovaten,
                    v.ketqua,
                    v.ngaytao,
                    v.ngaycapnhat
                FROM vande v
                LEFT JOIN nguoidung n ON v.cccd_canbo_xuly = n.cccd
                {where_clause}
                ORDER BY v.ngaytao DESC
            """, params)
            
            for row in cur.fetchall():
                ws.append(row)
        
        else:  # overview
            ws.title = "Tổng quan"
            
            # Thống kê phản ánh
            ws.append(["BÁO CÁO TỔNG QUAN HỆ THỐNG PHẢN ÁNH & KIẾN NGHỊ"])
            ws.merge_cells('A1:E1')
            ws['A1'].font = Font(bold=True, size=14)
            ws['A1'].alignment = Alignment(horizontal='center')
            
            ws.append([])
            ws.append(["THỐNG KÊ PHẢN ÁNH"])
            ws['A3'].font = Font(bold=True, size=12)
            
            cur.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN trangthaiphananh = 'Mới' THEN 1 END) as moi,
                    COUNT(CASE WHEN trangthaiphananh = 'Đang xử lý' THEN 1 END) as dangxuly,
                    COUNT(CASE WHEN trangthaiphananh = 'Đã xử lý' THEN 1 END) as daxuly
                FROM phananh
            """)
            
            stats = cur.fetchone()
            ws.append(["Tổng số phản ánh:", stats[0]])
            ws.append(["Phản ánh mới:", stats[1]])
            ws.append(["Đang xử lý:", stats[2]])
            ws.append(["Đã xử lý:", stats[3]])
            
            ws.append([])
            ws.append(["THỐNG KÊ VẤN ĐỀ"])
            ws['A9'].font = Font(bold=True, size=12)
            
            cur.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN trangthai = 'Đã giải quyết' THEN 1 END) as resolved
                FROM vande
            """)
            
            vande_stats = cur.fetchone()
            ws.append(["Tổng số vấn đề:", vande_stats[0]])
            ws.append(["Đã giải quyết:", vande_stats[1]])
        
        # Auto-adjust column widths
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width
        
        conn.close()
        
        # Save to BytesIO
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        
        filename = f"BaoCao_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        conn.close()
        flash(f'Lỗi khi xuất báo cáo: {str(e)}', 'danger')
        return redirect(url_for('reports_overview'))


# ========== CHẠY ỨNG DỤNG ==========
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
