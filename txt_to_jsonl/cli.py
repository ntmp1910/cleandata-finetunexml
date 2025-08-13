import argparse
import json
import os
from pathlib import Path
from typing import Generator, Iterable, List, Optional


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Quét thư mục chứa file .txt và xuất ra 1 hoặc nhiều file .jsonl "
            "với các trường: title, category, summary."
        )
    )
    parser.add_argument(
        "--input-dirs",
        nargs="+",
        required=True,
        help="Một hoặc nhiều thư mục đầu vào để quét .txt (hỗ trợ đệ quy).",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Thư mục để ghi các file .jsonl đầu ra.",
    )
    parser.add_argument(
        "--prefix",
        default="dataset",
        help="Tiền tố tên file .jsonl (mặc định: dataset).",
    )
    parser.add_argument(
        "--max-records-per-file",
        type=int,
        default=50000,
        help="Số bản ghi tối đa mỗi file .jsonl trước khi tách file mới (mặc định: 50000).",
    )
    parser.add_argument(
        "--summary-chars",
        type=int,
        default=1024,
        help="Số ký tự đầu tiên của nội dung file để làm summary (mặc định: 1024).",
    )
    parser.add_argument(
        "--title-source",
        choices=["filename", "firstline"],
        default="filename",
        help="Nguồn lấy title: từ tên file (filename) hoặc dòng đầu của file (firstline).",
    )
    parser.add_argument(
        "--title-max-chars",
        type=int,
        default=20,
        help="Giới hạn ký tự cho title (mặc định: 20).",
    )
    parser.add_argument(
        "--no-subdirs",
        action="store_true",
        help="Không quét thư mục con (mặc định có quét đệ quy).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Chỉ đếm file và hiển thị ví dụ 1-2 bản ghi, không ghi file.",
    )
    return parser.parse_args(argv)


def collect_txt_files(input_dirs: Iterable[str], recursive: bool = True) -> List[Path]:
    collected: List[Path] = []
    for directory in input_dirs:
        base = Path(directory)
        if not base.exists() or not base.is_dir():
            continue
        if recursive:
            for root, _dirs, files in os.walk(base):
                root_path = Path(root)
                for name in files:
                    if name.lower().endswith(".txt"):
                        collected.append(root_path / name)
        else:
            for path in base.iterdir():
                if path.is_file() and path.name.lower().endswith(".txt"):
                    collected.append(path)
    collected = sorted(set(p.resolve() for p in collected))
    return collected


def read_first_n_chars(file_path: Path, limit: int) -> str:
    if limit <= 0:
        return ""
    chars_remaining = limit
    parts: List[str] = []
    with file_path.open("r", encoding="utf-8", errors="replace") as f:
        while chars_remaining > 0:
            chunk = f.read(min(8192, chars_remaining))
            if not chunk:
                break
            parts.append(chunk)
            chars_remaining -= len(chunk)
    return "".join(parts)


def read_first_line(file_path: Path) -> str:
    with file_path.open("r", encoding="utf-8", errors="replace") as f:
        line = f.readline()
        return line.strip("\r\n")


def build_title(file_path: Path, title_source: str, title_max_chars: int) -> str:
    if title_source == "firstline":
        raw = read_first_line(file_path)
        if not raw:
            raw = file_path.stem
    else:
        raw = file_path.stem
    if title_max_chars > 0:
        return raw[:title_max_chars]
    return raw


def generate_records(
    files: Iterable[Path],
    summary_chars: int,
    title_source: str,
    title_max_chars: int,
) -> Generator[dict, None, None]:
    for file_path in files:
        try:
            title = build_title(file_path, title_source, title_max_chars)
            category = file_path.parent.name
            summary = read_first_n_chars(file_path, summary_chars)
            yield {
                "title": title,
                "category": category,
                "summary": summary,
            }
        except Exception as exc:  # noqa: BLE001
            # Bỏ qua file lỗi, có thể in cảnh báo nếu cần
            print(f"[WARN] Lỗi khi xử lý {file_path}: {exc}")
            continue


def ensure_output_dir(path: str) -> Path:
    out = Path(path)
    out.mkdir(parents=True, exist_ok=True)
    return out


def write_sharded_jsonl(
    records: Iterable[dict],
    output_dir: Path,
    prefix: str,
    max_records_per_file: int,
) -> int:
    shard_index = 1
    record_in_shard = 0
    file_handle = None
    written_total = 0

    def open_new_shard(idx: int):
        filename = f"{prefix}_{idx:05d}.jsonl"
        return (output_dir / filename).open("w", encoding="utf-8", errors="replace")

    try:
        file_handle = open_new_shard(shard_index)
        for rec in records:
            if max_records_per_file > 0 and record_in_shard >= max_records_per_file:
                file_handle.close()
                shard_index += 1
                record_in_shard = 0
                file_handle = open_new_shard(shard_index)

            json_line = json.dumps(rec, ensure_ascii=False)
            file_handle.write(json_line + "\n")
            record_in_shard += 1
            written_total += 1
    finally:
        if file_handle is not None and not file_handle.closed:
            file_handle.close()

    return written_total


def run(argv: Optional[List[str]] = None) -> None:
    args = parse_args(argv)

    files = collect_txt_files(args.input_dirs, recursive=not args.no_subdirs)
    print(f"Tìm thấy {len(files)} file .txt")

    if args.dry_run:
        # In thử 2 bản ghi ví dụ
        preview_files = files[:2]
        for rec in generate_records(
            preview_files,
            summary_chars=args.summary_chars,
            title_source=args.title_source,
            title_max_chars=args.title_max_chars,
        ):
            print(json.dumps(rec, ensure_ascii=False))
        return

    output_dir = ensure_output_dir(args.output_dir)
    total = write_sharded_jsonl(
        generate_records(
            files,
            summary_chars=args.summary_chars,
            title_source=args.title_source,
            title_max_chars=args.title_max_chars,
        ),
        output_dir=output_dir,
        prefix=args.prefix,
        max_records_per_file=args.max_records_per_file,
    )

    print(
        f"Đã ghi {total} bản ghi vào thư mục '{output_dir}'. "
        f"Tiền tố: '{args.prefix}', dung lượng mỗi file: {args.max_records_per_file} bản ghi."
    )
