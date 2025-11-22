from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Fake database (tài khoản mẫu)
users = {
    "admin": "123456"
}

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    # Kiểm tra tài khoản
    if username in users and users[username] == password:
        return f"Xin chào {username}, bạn đã đăng nhập thành công!"
    else:
        return "Sai tài khoản hoặc mật khẩu!"

if __name__ == "__main__":
    app.run(debug=True)