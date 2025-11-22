# tests/test_login.py
# Bộ unit test dùng pytest để kiểm tra chức năng đăng nhập trong app.py
# Các test sử dụng Flask test_client để gửi request tới endpoint /login
# Chạy bằng: pytest -q
# Yêu cầu: pip install flask pytest

import pytest
from app import app

@pytest.fixture
def client():
    """
    Fixture tạo Flask test_client.
    - Bật TESTING để Flask trả lỗi rõ ràng trong môi trường test.
    - Trả về client để dùng ở các test case.
    """
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

# ---------- Test case cơ bản (hợp lệ / không hợp lệ) ----------
def test_login_valid(client):
    # Case: username và password đúng (theo users dict trong app.py)
    rv = client.post("/login", data={"username": "admin", "password": "123456"})
    assert rv.status_code == 200
    assert "Xin chào admin, bạn đã đăng nhập thành công!" in rv.get_data(as_text=True)

def test_login_wrong_username(client):
    # Case: username không tồn tại -> trả về thông báo chung lỗi
    rv = client.post("/login", data={"username": "unknown", "password": "123456"})
    assert rv.status_code == 200
    assert "Sai tài khoản hoặc mật khẩu!" in rv.get_data(as_text=True)

def test_login_wrong_password(client):
    # Case: username đúng nhưng password sai
    rv = client.post("/login", data={"username": "admin", "password": "wrongpass"})
    assert rv.status_code == 200
    assert "Sai tài khoản hoặc mật khẩu!" in rv.get_data(as_text=True)

# ---------- Test các trường rỗng / whitespace / case ----------
def test_username_empty(client):
    # Username để trống
    rv = client.post("/login", data={"username": "", "password": "123456"})
    assert "Sai tài khoản hoặc mật khẩu!" in rv.get_data(as_text=True)

def test_password_empty(client):
    # Password để trống
    rv = client.post("/login", data={"username": "admin", "password": ""})
    assert "Sai tài khoản hoặc mật khẩu!" in rv.get_data(as_text=True)

def test_both_empty(client):
    # Cả username và password đều trống
    rv = client.post("/login", data={"username": "", "password": ""})
    assert "Sai tài khoản hoặc mật khẩu!" in rv.get_data(as_text=True)

def test_whitespace_in_username(client):
    # Username có khoảng trắng thừa (code hiện tại không strip -> sẽ fail)
    rv = client.post("/login", data={"username": " admin ", "password": "123456"})
    assert "Sai tài khoản hoặc mật khẩu!" in rv.get_data(as_text=True)

def test_case_sensitivity_username(client):
    # Kiểm tra phân biệt hoa thường (case-sensitive)
    rv = client.post("/login", data={"username": "Admin", "password": "123456"})
    assert "Sai tài khoản hoặc mật khẩu!" in rv.get_data(as_text=True)

# ---------- Test ký tự đặc biệt / unicode / control chars ----------
def test_special_characters_in_username(client):
    # Username chứa ký tự đặc biệt
    rv = client.post("/login", data={"username": "user!@#", "password": "123456"})
    assert "Sai tài khoản hoặc mật khẩu!" in rv.get_data(as_text=True)

def test_special_characters_in_password(client):
    # Password chứa ký tự đặc biệt
    rv = client.post("/login", data={"username": "admin", "password": "123!@#"})
    assert "Sai tài khoản hoặc mật khẩu!" in rv.get_data(as_text=True)

def test_unicode_in_username(client):
    # Username với ký tự unicode/accent
    rv = client.post("/login", data={"username": "admín", "password": "123456"})
    assert "Sai tài khoản hoặc mật khẩu!" in rv.get_data(as_text=True)

def test_unicode_in_password(client):
    # Password chứa ký tự unicode
    rv = client.post("/login", data={"username": "admin", "password": "pässw0rd"})
    assert "Sai tài khoản hoặc mật khẩu!" in rv.get_data(as_text=True)

def test_null_byte_in_username(client):
    # Username chứa null byte / ký tự điều khiển
    rv = client.post("/login", data={"username": "admin\0", "password": "123456"})
    assert "Sai tài khoản hoặc mật khẩu!" in rv.get_data(as_text=True)

def test_newline_and_tab_in_input(client):
    # Username/password chứa newline hoặc tab
    rv = client.post("/login", data={"username": "ad\nmin", "password": "12\t3456"})
    assert "Sai tài khoản hoặc mật khẩu!" in rv.get_data(as_text=True)

# ---------- Test boundary / performance-like ----------
def test_very_long_input(client):
    # Chuỗi dài rất lớn để kiểm tra giới hạn/hiệu năng
    long_user = "a" * 10000
    long_pass = "b" * 10000
    rv = client.post("/login", data={"username": long_user, "password": long_pass})
    assert "Sai tài khoản hoặc mật khẩu!" in rv.get_data(as_text=True)

# ---------- Test bảo mật (mô phỏng) ----------
def test_sql_injection_like_input(client):
    # Với dữ liệu hiện tại (in-memory dict) không có SQLi,
    # nhưng test này đảm bảo ứng dụng trả về lỗi chung
    payload = "' OR '1'='1"
    rv = client.post("/login", data={"username": payload, "password": "anything"})
    assert "Sai tài khoản hoặc mật khẩu!" in rv.get_data(as_text=True)

def test_xss_payload_in_username(client):
    # XSS reflected: nếu ứng dụng phản chiếu username ra HTML mà không escape,
    # đây sẽ là trường hợp cần kiểm tra (hiện không có account chứa payload)
    payload = "<script>alert(1)</script>"
    rv = client.post("/login", data={"username": payload, "password": "123"})
    assert "Sai tài khoản hoặc mật khẩu!" in rv.get_data(as_text=True)

# ---------- Test phương thức HTTP / content type ----------
def test_get_on_login_route_not_allowed(client):
    # /login chỉ chấp nhận POST -> GET sẽ trả 405 Method Not Allowed
    rv = client.get("/login")
    assert rv.status_code == 405

def test_json_body_instead_of_form(client):
    # Gửi JSON thay vì form-encoded -> request.form sẽ rỗng -> login thất bại
    rv = client.post("/login", json={"username": "admin", "password": "123456"})
    assert "Sai tài khoản hoặc mật khẩu!" in rv.get_data(as_text=True)

# ---------- Test hành vi sau nhiều lần thất bại ----------
def test_multiple_failed_attempts_then_success(client):
    # Hiện app không có cơ chế khóa/tạm dừng -> sau nhiều lần thất bại vẫn có thể login thành công
    for _ in range(20):
        rv = client.post("/login", data={"username": "admin", "password": "bad"})
        assert "Sai tài khoản hoặc mật khẩu!" in rv.get_data(as_text=True)
    rv = client.post("/login", data={"username": "admin", "password": "123456"})
    assert "Xin chào admin, bạn đã đăng nhập thành công!" in rv.get_data(as_text=True)
