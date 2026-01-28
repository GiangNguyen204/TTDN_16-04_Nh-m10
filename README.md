<h2 align="center">
    <a href="https://dainam.edu.vn/vi/khoa-cong-nghe-thong-tin">
    🎓 Faculty of Information Technology (DaiNam University)
    </a>
</h2>

<h2 align="center">
   🚀 Hệ thống quản lý tiền lương và bảo hiểm y tế (BHYT) trên Odoo 19
</h2>

<div align="center">
    <p align="center">
        <img width="170"  alt="AIoTLab Logo" src="https://github.com/user-attachments/assets/722ef6fe-9b09-41f4-9d58-a752e2be9da4" />
        <img width="170" alt="FIT DNU Logo" src="https://github.com/user-attachments/assets/38f342e5-4c81-4d22-b1d0-985cf91c702c" />
        <img width="200" alt="DaiNam University" src="https://github.com/user-attachments/assets/11138726-5355-4c53-9fdb-bec177681ae0" />
    </p>

<div align="center">

[![Odoo](https://img.shields.io/badge/Odoo-19-purple?style=for-the-badge)](https://www.odoo.com/)
[![BJ Payroll](https://img.shields.io/badge/BJ%20Payroll-Custom-blue?style=for-the-badge)](#)
[![DaiNam University](https://img.shields.io/badge/DaiNam%20University-orange?style=for-the-badge)](https://dainam.edu.vn)

</div>
</div>

---

## 1. Giới thiệu hệ thống

Đây là **hệ thống quản lý tiền lương và bảo hiểm y tế (BHYT)** được xây dựng trên nền tảng **Odoo 19**, theo hướng **module hóa và tùy biến**, phục vụ mục tiêu **nghiên cứu học thuật và đồ án tốt nghiệp**.

Hệ thống **không sử dụng module payroll mặc định của Odoo**, mà triển khai một giải pháp tính lương riêng (BJ Payroll), cho phép chủ động trong thiết kế nghiệp vụ và mở rộng trong tương lai.

---

### 🎯 Mục tiêu chính

- Xây dựng hệ thống **tính lương tùy biến** dựa trên dữ liệu chấm công  
- Tích hợp **bảo hiểm y tế (BHYT)** cho người lao động và doanh nghiệp  
- Đảm bảo **tính chính xác – minh bạch – nhất quán dữ liệu**  
- Phù hợp cho **đào tạo, nghiên cứu và mô phỏng nghiệp vụ doanh nghiệp**

---

### 🧩 Các chức năng chính

- 👤 **Quản lý nhân viên**
- ⏱ **Chấm công và tổng hợp theo tháng**
- 💰 **Quản lý bảng lương (Payslip)**
- 🏥 **Tích hợp bảo hiểm y tế (BHYT)**

---

## ⚙️ 2. Công nghệ sử dụng

### 💻 Nền tảng chính
- **Odoo 19**
- **Python (Odoo ORM)**
- **PostgreSQL**

### 🧩 Kiến trúc hệ thống
- Module lõi: `bj_payroll_core`
- Module mở rộng: `bj_health_insurance`
- Custom model: `bj.hr.payslip`

---

## 3. Một số hình ảnh hệ thống

<p align="center">
    <em>Danh sách bảng lương (Payslip List View)</em><br/>
    <img src="docs/payslip_list.png" width="900"/>
</p>

<p align="center">
    <em>Chi tiết bảng lương và bảo hiểm y tế (BHYT)</em><br/>
    <img src="docs/payslip_form_bhyt.png" width="900"/>
</p>

<p align="center">
    <em>Chức năng chấm công và tổng hợp theo tháng</em><br/>
    <img src="docs/attendance_report.png" width="900"/>
</p>

---

## 🛠️ 4. Hướng dẫn cài đặt & triển khai

### 4.1. Yêu cầu hệ thống
- 🐍 Python >= 3.10  
- 🐘 PostgreSQL  
- 🐳 Docker (khuyến nghị)  
- 🌐 Trình duyệt web hiện đại

---

### 📦 4.2. Clone dự án

```bash
git clone https://github.com/<username>/bj-payroll-odoo19.git
cd bj-payroll-odoo19
```

---

### 🔧 4.3. Cài đặt module

1. Sao chép các module sau vào thư mục `addons` của Odoo:
   - `bj_payroll_core`
   - `bj_health_insurance`

2. Cập nhật module trong cơ sở dữ liệu:

```bash
./odoo-bin -d your_database -u bj_payroll_core,bj_health_insurance
```

---

### ▶️ 4.4. Chạy hệ thống

```bash
./odoo-bin -c odoo.conf
```

Truy cập hệ thống tại:

```
http://localhost:8069
```

---

### ✅ 4.5. Kiểm tra hoạt động

1. Tạo nhân viên  
2. Chấm công cho nhân viên  
3. Tạo payslip theo tháng  
4. Nạp dữ liệu chấm công  
5. Compute lương  
6. Kiểm tra kết quả BHYT  

---

## 📞 5. Thông tin sinh viên thực hiện

- 👤 **Sinh viên:** Giang Nguyễn, Bắc Nguyễn, Thu Hồng
- 🎓 **Khoa:** Công nghệ Thông tin – Đại học Đại Nam  
- 📧 **Email:** giangnguyen27112k4@gmail.com  
- 📞 **SĐT:** 0353397306  

---

<p align="center">
✨ <em>README được xây dựng cho kết thúc môn: Hệ thống quản lý tiền lương và bảo hiểm y tế trên nền tảng Odoo 19.</em>
</p>
