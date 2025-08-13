## txt → JSONL rút gọn

Công cụ này duyệt qua các thư mục chứa file `.txt` (có thể lồng nhau), và gom lại thành 1 hoặc nhiều file `.jsonl` với mỗi dòng là 1 object:
- **title**: ~20 ký tự đầu tiên của tiêu đề (mặc định lấy theo tên file, không gồm phần mở rộng)
- **category**: tên thư mục chứa trực tiếp file `.txt`
- **summary**: 1024 ký tự đầu tiên của nội dung file

### Cài đặt
- Yêu cầu: Python 3.8+
- Không cần cài thêm thư viện ngoài

### Cách chạy nhanh
Ví dụ: gom tất cả `.txt` trong thư mục `data` thành các file JSONL ở thư mục `out`:

```powershell
cd D:\Viettel\cleandata-finetunexml\cleandata-finetunexml
python -m txt_to_jsonl --input-dirs data --output-dir out --prefix dataset --max-records-per-file 50000 --summary-chars 1024 --title-source filename --title-max-chars 20
```

Hoặc dùng line continuation với backtick:
```powershell
cd D:\Viettel\cleandata-finetunexml\cleandata-finetunexml
python -m txt_to_jsonl `
  --input-dirs data `
  --output-dir out `
  --prefix dataset `
  --max-records-per-file 50000 `
  --summary-chars 1024 `
  --title-source filename `
  --title-max-chars 20
```

- Kết quả sẽ là các file: `out\dataset_00001.jsonl`, `out\dataset_00002.jsonl`, ...
- Mỗi dòng là một JSON object: `{ "title": ..., "category": ..., "summary": ... }`

### Tham số CLI
- **--input-dirs**: 1 hoặc nhiều thư mục đầu vào. Công cụ sẽ duyệt đệ quy các thư mục con và lấy tất cả `.txt`.
- **--output-dir**: thư mục để ghi file `.jsonl`.
- **--prefix**: tiền tố tên file output. Mặc định: `dataset`.
- **--max-records-per-file**: số dòng tối đa mỗi file `.jsonl` trước khi tách sang file tiếp theo. Mặc định: `50000`.
- **--summary-chars**: số ký tự đầu tiên của nội dung để làm `summary`. Mặc định: `1024`.
- **--title-source**: `filename` (mặc định) hoặc `firstline`.
  - `filename`: dùng tên file (bỏ `.txt`) làm tiêu đề, sau đó cắt còn `--title-max-chars` ký tự.
  - `firstline`: dùng dòng đầu tiên trong file làm tiêu đề, sau đó cắt còn `--title-max-chars` ký tự.
- **--title-max-chars**: số ký tự tối đa cho `title`. Mặc định: `20`.
- **--no-subdirs**: chỉ quét thư mục cấp hiện tại, không quét thư mục con.

### Ghi chú
- Mặc định mở file với mã hóa `utf-8` và `errors=replace` để an toàn với các trường hợp mã hóa không chuẩn.
- Nếu bạn muốn thay đổi logic lấy `title` (ví dụ: ưu tiên dòng đầu không rỗng trong file), có thể chỉnh trong `txt_to_jsonl/cli.py`.

### Ví dụ thêm
Chỉ quét thư mục hiện tại, không quét thư mục con, lấy `title` từ dòng đầu tiên của file:
```powershell
cd D:\Viettel\cleandata-finetunexml\cleandata-finetunexml
python -m txt_to_jsonl --input-dirs . --output-dir out --no-subdirs --title-source firstline
```

### Cấu trúc thư mục hiện tại
```
D:\Viettel\cleandata-finetunexml\
└── cleandata-finetunexml\
    ├── data\           # Thư mục chứa các file .txt cần xử lý
    ├── out\            # Thư mục chứa kết quả .jsonl
    ├── txt_to_jsonl\   # Package CLI
    └── README.md       # Hướng dẫn sử dụng
```
