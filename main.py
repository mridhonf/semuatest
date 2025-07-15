import streamlit as st
import sqlite3
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

# ====== FUNGSI DATABASE ======

def buat_tabel_user():
    conn = sqlite3.connect('user.db')
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()

def daftar_user(username, password):
    conn = sqlite3.connect('user.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False  # Username sudah ada

def cek_login(username, password):
    conn = sqlite3.connect('user.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    hasil = c.fetchone()
    conn.close()
    return hasil is not None

# ====== SETUP HALAMAN ======

st.set_page_config("Login App", "🔐")
buat_tabel_user()

if 'login' not in st.session_state:
    st.session_state.login = False
if 'username' not in st.session_state:
    st.session_state.username = ""

# ====== MENU NAVIGASI ======
menu = st.sidebar.selectbox("Navigasi", ["Login", "Daftar", "Beranda"])

# ====== FORM LOGIN ======
if menu == "Login":
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Masuk"):
        if cek_login(username, password):
            st.success(f"Selamat datang, {username}!")
            st.session_state.login = True
            st.session_state.username = username
        else:
            st.error("Username atau password salah.")

# ====== FORM REGISTER ======
elif menu == "Daftar":
    st.title("📝 Registrasi Pengguna Baru")
    new_user = st.text_input("Buat Username")
    new_pass = st.text_input("Buat Password", type="password")

    if st.button("Daftar"):
        if daftar_user(new_user, new_pass):
            st.success("✅ Akun berhasil dibuat. Silakan login.")
        else:
            st.warning("⚠️ Username sudah digunakan.")

# ====== HALAMAN BERANDA ======
elif menu == "Beranda":
    if st.session_state.login:
        st.title("🏠 Beranda")
        st.write(f"Halo, **{st.session_state.username}**! Kamu sudah login.")
        if st.button("Logout"):
            st.session_state.login = False
            st.session_state.username = ""
            st.success("Kamu telah logout.")
    else:
        st.warning("❌ Kamu belum login. Silakan login dulu.")
