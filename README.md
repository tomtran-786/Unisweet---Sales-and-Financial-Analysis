# UniSweet Sales Master and Finance Story

Project chuẩn hóa các file Customer Sales và Master Mapping thành một file master duy nhất để làm nguồn cho các script phân tích tiếp theo.

```text
Customer Sales workbooks + Master Mapping
                    ↓
         outputs/sales_master.csv
                    ↓
        User-owned analysis scripts

P&L Table.xlsx và Market Report.xlsx được giữ nguyên như nguồn độc lập.
```

Storyline, metric definitions, công thức, dimension và guardrails nằm trong [STORYLINE_METRIC_FRAMEWORK.md](STORYLINE_METRIC_FRAMEWORK.md).

## Tạo Sales master

Chạy từ project root:

```bash
.venv/bin/python scripts/build_sales_master.py
```

Hoặc sau khi cài package/refresh environment:

```bash
unisweet-sales-master --project-root .
```

Output mặc định:

```text
outputs/sales_master.csv
```

Có thể chọn path khác:

```bash
.venv/bin/python scripts/build_sales_master.py --output /path/to/sales_master.csv
```

## Grain và cấu trúc master

Mỗi dòng là một grain:

```text
Reporting Month × Customer × Brand × Pack Type × Pack Size
```

Master đã:

- Ghép GSV và Turnover về cùng một dòng.
- Tính `discount_keur`, `discount_pct_to` và `discount_pct_gsv`.
- Join Customer, Channel, Brand và Product Mapping.
- Giữ exact `product_key = pack_type|pack_size`.
- Ghi source file/source row riêng cho GSV và Turnover.
- Giữ toàn bộ grain, kể cả grain cần review hoặc invalid.
- Đánh dấu `certified_for_analysis`, `data_quality_status` và `data_quality_flags`.

Filter mặc định cho phân tích governed:

```python
import pandas as pd

sales = pd.read_csv(
    "outputs/sales_master.csv",
    dtype={"customer_code": "string", "brand_code": "string"},
    parse_dates=["reporting_month"],
)
certified = sales[sales["certified_for_analysis"]]
```

`customer_code` phải được đọc như string để giữ số 0 ở đầu.

## Inputs

### Customer Sales

`inputs/sales/Cust <number>.xlsx` phải có đúng tám cột:

```text
Customer Code, Brand Code, Pack Type, Pack Size,
Month, Year, KPI, Values
```

Script tự phát hiện mọi file phù hợp `Cust *.xlsx`; không hardcode danh sách Customer.

### Mapping

`inputs/mapping/Master Mapping.xlsx` gồm:

- `Customer Mapping`
- `Brand Mapping`
- `Product Mapping`

### P&L và Market

Hai nguồn sau không được script Sales master chỉnh sửa:

- `inputs/pnl/P&L Table.xlsx`
- `inputs/market/Market Report MAT <Mon>'<YY>.xlsx`

## Data-quality contract

| Status | Ý nghĩa | Sử dụng mặc định |
|---|---|---|
| `VALID` | Không có quality flag | Có |
| `REVIEW` | Grain dùng được nhưng mapping/giá trị cần chú ý | Có, kèm disclosure |
| `INVALID` | KPI pair, mapping hoặc Gross-to-Net không đạt policy | Không |

Các flag chính:

- `GSV_MISSING`, `TURNOVER_MISSING`
- `GSV_DUPLICATE`, `TURNOVER_DUPLICATE`
- `TURNOVER_GT_GSV`
- `GSV_NEGATIVE`, `TURNOVER_NEGATIVE`
- `CUSTOMER_MAPPING_MISSING`, `BRAND_MAPPING_MISSING`, `PRODUCT_MAPPING_MISSING`
- `PRODUCT_MAPPING_REVIEW`

## Phạm vi project hiện tại

Project chỉ duy trì hai deliverable chính:

- `STORYLINE_METRIC_FRAMEWORK.md`: metric và storyline contract.
- `outputs/sales_master.csv`: nguồn Sales phẳng cho các script phân tích tiếp theo.

P&L và Market được giữ nguyên trong `inputs/` để bạn xử lý độc lập ở bước sau. Project không còn analysis pack, dashboard, story generator hoặc PowerPoint publisher.

## Kiểm thử

```bash
.venv/bin/pytest
```

Tests kiểm tra schema, mapping, row counts, certified/invalid policy và bảo toàn P&L/Market.
