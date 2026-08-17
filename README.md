# UniSweet Sales Master

Project chỉ có một chức năng xử lý dữ liệu: gộp toàn bộ Customer Sales với Master Mapping thành một file CSV duy nhất.

```text
inputs/sales/Cust *.xlsx
             +
inputs/mapping/Master Mapping.xlsx
             ↓
scripts/build_sales_master.py
             ↓
outputs/sales_master.csv
```

P&L và Market không được xử lý bằng code:

- `inputs/pnl/P&L Table.xlsx`: mở và đọc trực tiếp trong Excel.
- `inputs/market/Market Report MAT Nov'24.xlsx`: mở và đọc trực tiếp trong Excel.

Storyline và các metric phù hợp với ba nguồn hiện có nằm tại [STORYLINE_METRIC_FRAMEWORK.md](STORYLINE_METRIC_FRAMEWORK.md).

## Tài liệu tham chiếu

- **Storytelling with Data** (Cole Nussbaumer Knaflic, Wiley 2015): dùng làm project context cho phần trực quan hoá. Bản Markdown được chuyển đổi bằng `fastpdf4llm` và phần hình ảnh trích xuất chỉ lưu cục bộ tại `references/domain/`, **không commit** vì lý do bản quyền.

## Script Sales master

Toàn bộ logic được viết công khai trong một file duy nhất:

- [scripts/build_sales_master.py](scripts/build_sales_master.py)

Script thực hiện lần lượt:

1. Tự phát hiện mọi file `Cust *.xlsx`.
2. Kiểm tra đúng tám cột Sales nguồn.
3. Chuẩn hóa Customer Code, Brand Code, Month, Pack Type và Pack Size.
4. Ghép GSV và Turnover về cùng một grain.
5. Join Customer, Channel, Brand và Product Mapping.
6. Tính Discount và hai discount rates.
7. Gắn quality flags và source lineage.
8. Ghi một file `outputs/sales_master.csv`.

## Cài dependencies

```bash
python -m pip install -r requirements.txt
```

## Chạy script

Từ project root:

```bash
python scripts/build_sales_master.py
```

Chọn output khác nếu cần:

```bash
python scripts/build_sales_master.py --output /path/to/sales_master.csv
```

## Grain và cột chính

Mỗi dòng của master là:

```text
Reporting Month × Customer × Brand × Pack Type × Pack Size
```

Cột chính:

- Time: `reporting_month`, `reporting_year`, `month_number`.
- Customer/Channel: `customer_code`, `customer_name`, `channel_code`.
- Brand: `brand_code`, `brand_name`.
- Product: `product_key`, `product_name`, `pack_type`, `pack_size`.
- Values: `gsv_keur`, `turnover_keur`, `discount_keur`.
- Rates: `discount_pct_to`, `discount_pct_gsv`.
- Quality: `certified_for_analysis`, `data_quality_status`, `data_quality_flags`.
- Lineage: source file và source row cho GSV/Turnover.

Đọc file bằng pandas:

```python
import pandas as pd

sales = pd.read_csv(
    "outputs/sales_master.csv",
    dtype={"customer_code": "string", "brand_code": "string"},
    parse_dates=["reporting_month"],
)
sales = sales[sales["certified_for_analysis"]]
```

`customer_code` cần được đọc như string để giữ số 0 ở đầu.

## Kiểm thử

```bash
pytest -p no:cacheprovider
```

Tests chỉ kiểm tra Sales master và xác nhận script không làm thay đổi P&L/Market.
