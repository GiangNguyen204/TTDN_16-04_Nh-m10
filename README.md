# 📊 BÁO CÁO HỆ THỐNG CHẤM CÔNG – TÍNH LƯƠNG TỰ ĐỘNG  
## Trên nền tảng Odoo 19

![Odoo Banner](https://github.com/user-attachments/assets/d1572174-b9a5-44f7-b7c8-769db9bdac3e)

---

## 🧭 Giới thiệu chung

Quản trị nhân sự là **nòng cốt của sự ổn định và phát triển doanh nghiệp**.  
Việc áp dụng hệ thống tự động hóa trong chấm công và tính lương giúp:

- Tối ưu hóa quy trình vận hành  
- Giảm thiểu sai sót thủ công  
- Đảm bảo tính **minh bạch – chính xác – kịp thời** trong chi trả quyền lợi cho người lao động  

Đề tài tập trung xây dựng **giải pháp quản trị nhân sự tập trung** trên nền tảng **ERP Odoo 19**, tích hợp chặt chẽ giữa chấm công, tiền lương và báo cáo phân tích.

---

## 📌 Giới thiệu hệ thống

Hệ thống chấm công – tính lương trên nền tảng **Odoo ERP** là một giải pháp **khép kín**, bao phủ toàn bộ quy trình từ quản lý hồ sơ nhân sự đến xuất phiếu lương.

### Các chức năng chính:
- 🗂️ **Quản lý nhân sự**  
  Lưu trữ tập trung hồ sơ nhân viên, phòng ban, chức vụ và vòng đời hợp đồng.

- 🕒 **Ghi nhận chấm công**  
  Hỗ trợ nhiều nguồn dữ liệu: nhập tay, camera, API thiết bị ngoại vi.

- ⚖️ **Tự động tính lương**  
  Tính lương dựa trên công thực tế, hệ số tăng ca và các khoản phụ cấp.

- 🛡️ **Bảo hiểm & Thuế**  
  Khấu trừ tự động BHXH, BHYT, BHTN và thuế TNCN theo quy định pháp luật.

- 📊 **Báo cáo thông minh**  
  Dashboard trực quan theo dõi quỹ lương và hiệu suất làm việc.

---

## 🏗️ Cấu trúc hệ thống

Hệ thống được thiết kế theo **kiến trúc module**, liên kết chặt chẽ thông qua cơ sở dữ liệu tập trung:

1. **Module Nhân sự (Core)**  
   Quản lý thông tin nhân viên, hợp đồng và khung lương cơ bản.

2. **Module Chấm công (Center)**  
   Xử lý dữ liệu hiện diện, đối chiếu ca làm việc và phát hiện đi muộn/về sớm.

3. **Module Tính lương (Payroll)**  
   Tính toán lương Gross/Net, áp dụng biểu thuế lũy tiến và sinh phiếu lương điện tử.

---

## 🛠️ Công cụ và công nghệ sử dụng

- **Ngôn ngữ**: Python (xử lý logic nghiệp vụ, ORM)
- **Nền tảng**: Odoo 19 (ERP mã nguồn mở)
- **Cơ sở dữ liệu**: PostgreSQL
- **Công cụ hỗ trợ**:
  - GitHub (quản lý mã nguồn)
  - PlantUML (thiết kế sơ đồ)
- **Tích hợp dữ liệu**:
  - Google Sheets
  - Microsoft Excel

---

# 🚀 Hướng dẫn cài đặt và vận hành hệ thống

## 1. Cài đặt môi trường Odoo

### 🔧 Yêu cầu hệ thống
- **Python**: phiên bản 3.10 trở lên
- **Cơ sở dữ liệu**: PostgreSQL
- **Hệ điều hành**: Linux / WSL / macOS (khuyến nghị)

### 📦 Cài đặt thư viện cần thiết
Sau khi clone source code, chạy lệnh:

```bash
pip install -r requirements.txt
```
## 2. Cấu hình quy định Tăng ca (OT)
Dữ liệu tăng ca (Overtime – OT) được hệ thống tự động xác định dựa trên thời điểm làm việc thực tế:

Ngày thường: Hệ số 150%

Cuối tuần: Hệ số 200%

Ngày Lễ / Tết: Hệ số 300%

## 3. Chạy hệ thống
Khởi động Odoo Server và cài đặt module tùy chỉnh của nhóm:
```bash ./odoo-bin -c odoo.conf -i hr_payroll_custom```
<li>📘 Hướng dẫn sử dụng hệ thống</li>
a) Thiết lập ban đầu
Nhập hồ sơ nhân viên

Thiết lập phòng ban

Cấu hình mức lương cơ bản trong module Nhân sự (HR)

b) Phân ca làm việc
Tạo các loại ca:

Ca sáng : 8h-17h

Ca đêm : 22h-6h

Gán ca cho từng nhân viên

c) Chấm công
Nhân viên Check-in / Check-out qua:

Giao diện Web

Thiết bị chấm công

Hệ thống tự động

Đối chiếu ca làm việc

Phát hiện đi muộn / về sớm

d) Kết xuất bảng lương
Cuối kỳ, bộ phận kế toán:

Kiểm tra bảng tổng hợp công

Nhấn “Sinh phiếu lương” (Payslip)

⚙️ Công thức tính toán cốt lõi
1. Lương thực tế
Lương thực tế = (Lương cơ bản / Công chuẩn) × Công thực tế
Công chuẩn: 26 ngày/tháng

2. Khấu trừ bảo hiểm
Tổng mức khấu trừ: 10.5% lương đóng bảo hiểm, bao gồm:

<li>BHXH: 8%</li>

<li>BHYT: 1.5%</li>

<li>BHTN: 1%</li>

3. Lương Net
Lương Net = Lương Gross - Bảo hiểm - Thuế TNCN
📰 Báo cáo & Phân tích dữ liệu
Hệ thống hỗ trợ:

Phát hiện bất thường (Anomaly Detection) bằng AI

Gắn cờ các trường hợp:

Quên chấm công

Quỹ lương dự báo vượt mức cho phép

🤝 Đóng góp & Thông tin nhóm
Dự án được thực hiện bởi:

Nhóm 10 – CNTT 16-04

Trường Đại học Đại Nam

Thành viên:

Nguyễn Văn Bắc – 1671020038

Nguyễn Văn Giang – 1671020094

Nguyễn Thu Hồng – 1671020131

Giảng viên hướng dẫn:
TS. Trần Đăng Công

© 2026 AIoTLab, Khoa Công nghệ Thông tin, Đại học Đại Nam. Mọi quyền được bảo lưu.
