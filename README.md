## txt → JSONL rút gọn

Công cụ này duyệt qua các thư mục chứa file `.txt` (có thể lồng nhau), và gom lại thành 1 hoặc nhiều file `.jsonl` với mỗi dòng là 1 object:

**Chế độ single (mặc định):**
- **title**: ~20 ký tự đầu tiên của tiêu đề (mặc định lấy theo tên file, không gồm phần mở rộng)
- **category**: tên thư mục con trực tiếp của thư mục input 
- **summary**: 1024 ký tự đầu tiên của nội dung file

**Chế độ chunked (chia đoạn):**
- **title**: ~20 ký tự đầu tiên của tiêu đề
- **category**: tên thư mục con trực tiếp của thư mục input
- **summary**: một đoạn nội dung (1024 ký tự mặc định)
- **chunk_index**: số thứ tự đoạn (1, 2, 3...)
- **total_chunks**: tổng số đoạn của file

### Cài đặt
- Yêu cầu: Python 3.8+
- Không cần cài thêm thư viện ngoài

### Cách chạy nhanh

**Chế độ single (1 file = 1 object):**
```powershell
python -m txt_to_jsonl --input-dirs data --output-dir out --prefix dataset --split-mode single
```

**Chế độ chunked (1 file = nhiều object theo đoạn):**
```powershell
python -m txt_to_jsonl --input-dirs data --output-dir out --prefix dataset --split-mode chunked --summary-chars 2048 --chunk-overlap 204
```

Hoặc dùng line continuation với backtick:
```powershell
python -m txt_to_jsonl `
  --input-dirs data `
  --output-dir out `
  --prefix dataset `
  --split-mode chunked `
  --summary-chars 1024 `
  --chunk-overlap 50 `
  --title-source filename `
  --title-max-chars 20
```

- Kết quả sẽ là các file: `out\dataset_00001.jsonl`, `out\dataset_00002.jsonl`, ...
- Mỗi dòng là một JSON object với các trường tương ứng theo chế độ đã chọn

### Tham số CLI
- **--input-dirs**: 1 hoặc nhiều thư mục đầu vào. Công cụ sẽ duyệt đệ quy các thư mục con và lấy tất cả `.txt`.
- **--output-dir**: thư mục để ghi file `.jsonl`.
- **--prefix**: tiền tố tên file output. Mặc định: `dataset`.
- **--max-records-per-file**: số dòng tối đa mỗi file `.jsonl` trước khi tách sang file tiếp theo. Mặc định: `50000`.
- **--summary-chars**: số ký tự cho mỗi đoạn summary. Mặc định: `1024`.
- **--title-source**: `filename` (mặc định) hoặc `firstline`.
  - `filename`: dùng tên file (bỏ `.txt`) làm tiêu đề, sau đó cắt còn `--title-max-chars` ký tự.
  - `firstline`: dùng dòng đầu tiên trong file làm tiêu đề, sau đó cắt còn `--title-max-chars` ký tự.
- **--title-max-chars**: số ký tự tối đa cho `title`. Mặc định: `20`.
- **--no-subdirs**: chỉ quét thư mục cấp hiện tại, không quét thư mục con.
- **--split-mode**: `single` (mặc định) hoặc `chunked`.
  - `single`: 1 file .txt = 1 object JSONL
  - `chunked`: 1 file .txt = nhiều object JSONL theo đoạn
- **--chunk-overlap**: số dòng chồng lấp giữa các đoạn khi dùng `split-mode=chunked`. Mặc định: `50`.

### Ghi chú
- Mặc định mở file với mã hóa `utf-8` và `errors=replace` để an toàn với các trường hợp mã hóa không chuẩn.
- Nếu bạn muốn thay đổi logic lấy `title` (ví dụ: ưu tiên dòng đầu không rỗng trong file), có thể chỉnh trong `txt_to_jsonl/cli.py`.

### Ví dụ thêm
Chỉ quét thư mục hiện tại, không quét thư mục con, lấy `title` từ dòng đầu tiên của file:
```powershell
python -m txt_to_jsonl --input-dirs . --output-dir out --no-subdirs --title-source firstline
```

**Ví dụ chia đoạn với khoảng chồng lấp 100 dòng:**
```powershell
python -m txt_to_jsonl --input-dirs data --output-dir out --split-mode chunked --summary-chars 2048 --chunk-overlap 100
```

**Test trước với dry-run:**
```powershell
python -m txt_to_jsonl --input-dirs data --output-dir out --split-mode chunked --dry-run
```

### Cấu trúc thư mục và cách lấy category

**Ví dụ cấu trúc thư mục:**
```
data/
├── Tâm Lý Học/
│   ├── file1.txt
│   └── file2.txt
├── Sinh Học/
│   ├── file3.txt
│   └── file4.txt
└── Triết Học/
    ├── file5.txt
    └── file6.txt
```

**Khi chạy lệnh:**
```powershell
python -m txt_to_jsonl --input-dirs data --output-dir out --prefix dataset
```

**Kết quả category sẽ là:**
- `data/Tâm Lý Học/file1.txt` → category: "Tâm Lý Học"
- `data/Sinh Học/file3.txt` → category: "Sinh Học"  
- `data/Triết Học/file5.txt` → category: "Triết Học"

### Cấu trúc thư mục hiện tại
```
└── cleandata-finetunexml\
    ├── data\           # Thư mục chứa các file .txt cần xử lý
    ├── out\            # Thư mục chứa kết quả .jsonl
    ├── txt_to_jsonl\   # Package CLI
    └── README.md       # Hướng dẫn sử dụng
```
