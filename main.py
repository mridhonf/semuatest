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
        st.title("📦 Model Persediaan EOQ (Economic Order Quantity) Gasoline Motor")
st.markdown("<hr>", unsafe_allow_html=True)

st.markdown("#### ℹ️ Apa itu EOQ?")
st.markdown("""
EOQ (Economic Order Quantity) adalah jumlah unit optimal yang harus dipesan setiap kali agar biaya persediaan total (biaya pesan + simpan) minimal. 
Perhitungan menggunakan rumus:

\[
EOQ = (2 * D * S) / H
\]
""", unsafe_allow_html=True)


st.markdown("### 📘 Masukkan Data Persediaan:")

# =====================
# Input
# =====================
col1, col2 = st.columns(2)
with col1:
    D = st.number_input("⛽ Kebutuhan Gasoline (Liter/Tahun)", min_value=1, value=12000)
    S = st.number_input("📥 Total Biaya per pesanan (Rp)", min_value=1, value=100000)
with col2:
    H = st.number_input("🛢️ Biaya simpan Gasoline (Liter/Tahun) (Rp)", min_value=1, value=2500)

# Keterangan input
st.markdown("#### ℹ️ Keterangan:")
st.markdown("""
- **D** = Permintaan/Kebutuhan Gasoline dalam 1 tahun
- **S** = Biaya setiap kali melakukan pemesanan
- **H** = Biaya menyimpan 1 Liter Gasoline selama 1 tahun
""")

# =====================
# Perhitungan EOQ
# =====================
EOQ = np.sqrt((2 * D * S) / H)
jumlah_pemesanan = D / EOQ
biaya_pesan_EOQ = jumlah_pemesanan * S
biaya_simpan_EOQ = (EOQ / 2) * H
total_biaya_EOQ = biaya_pesan_EOQ + biaya_simpan_EOQ

# =====================
# OUTPUT UTAMA
# =====================
st.markdown("### ✅ Hasil Perhitungan:")
st.success(f"1. 🛢️ EOQ (Jumlah optimal per pemesanan produk Gasoline) : {EOQ:.2f} Liter")
st.info(f"2. Jumlah Pemesanan dalam Setahun: {jumlah_pemesanan:.2f} kali")


# =====================
# DETAIL BIAYA
# =====================
st.markdown("### 🔍 Rincian Biaya di Titik EOQ:")
st.write(f"🔵 **Biaya Pemesanan Tahunan:** Rp {biaya_pesan_EOQ:,.0f}")
st.write(f"🟢 **Biaya Penyimpanan Tahunan:** Rp {biaya_simpan_EOQ:,.0f}")
st.write(f"🟠 **Total Biaya Persediaan:** Rp {total_biaya_EOQ:,.0f}")


# =====================
# VISUALISASI GRAFIK
# =====================
st.markdown("### 📈 Grafik Komponen Biaya Persediaan (EOQ)")

# Hitung range jumlah pemesanan Q
Q_range = np.linspace(100, D, 300)
biaya_pesan = (D / Q_range) * S
biaya_simpan = (Q_range / 2) * H
biaya_total = biaya_pesan + biaya_simpan

# Buat grafik
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(Q_range, biaya_pesan, label="Biaya Pemesanan", color='blue', linestyle='--')
ax.plot(Q_range, biaya_simpan, label="Biaya Penyimpanan", color='green', linestyle='-.')
ax.plot(Q_range, biaya_total, label="Total Biaya Persediaan", color='orange', linewidth=2)

# Garis vertikal EOQ
ax.axvline(EOQ, color='red', linestyle=':', label=f'EOQ ≈ {EOQ:.0f} Liter')

# Titik-titik biaya pada EOQ
ax.plot(EOQ, biaya_pesan_EOQ, 'bo')  # titik biru biaya pesan
ax.plot(EOQ, biaya_simpan_EOQ, 'go')  # titik hijau biaya simpan
ax.plot(EOQ, total_biaya_EOQ, 'ro')  # titik merah total biaya

# Keterangan titik
ax.annotate(f'Biaya Pesan\nRp {biaya_pesan_EOQ:,.0f}',
            (EOQ, biaya_pesan_EOQ),
            textcoords="offset points", xytext=(-70,10), ha='center', color='blue')

ax.annotate(f'Biaya Simpan\nRp {biaya_simpan_EOQ:,.0f}',
            (EOQ, biaya_simpan_EOQ),
            textcoords="offset points", xytext=(70,10), ha='center', color='green')

ax.annotate(f'Total Biaya\nRp {total_biaya_EOQ:,.0f}',
            (EOQ, total_biaya_EOQ),
            textcoords="offset points", xytext=(0,-40), ha='center', color='darkorange')

# Label grafik
ax.set_xlabel("Jumlah Pemesanan Sekali Order (Q)", fontsize=11)
ax.set_ylabel("Biaya (Rp)", fontsize=11)
ax.set_title("📊 Grafik EOQ: Biaya Pemesanan, Penyimpanan, dan Total Biaya", fontsize=13)
ax.legend()
ax.grid(True)
fig.tight_layout()

# Tampilkan grafik di Streamlit
st.pyplot(fig)
        if st.button("Logout"):
            st.session_state.login = False
            st.session_state.username = ""
            st.success("Kamu telah logout.")
    else:
        st.warning("❌ Kamu belum login. Silakan login dulu.")
