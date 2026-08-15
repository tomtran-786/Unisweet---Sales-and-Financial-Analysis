# PLAN — UniSweet Sales Master and Story Framework

## 1. Kiến trúc

```text
Customer Sales Excel + Master Mapping
                 ↓
       Sales master generator
                 ↓
       outputs/sales_master.csv
                 ↓
       User-owned analysis scripts
```

P&L và Market Data tiếp tục là nguồn độc lập, không bị chỉnh sửa hoặc đưa vào Sales master.

Luồng analysis pack/story hiện hữu được giữ lại để tham chiếu, nhưng Excel dashboard đã bị loại bỏ.

## 2. Sales master contract

### Input

- Mọi file `inputs/sales/Cust *.xlsx` có schema Sales tám cột.
- `inputs/mapping/Master Mapping.xlsx` với Customer, Brand và Product Mapping.

### Grain

```text
Month × Customer × Brand × exact Product
```

`exact Product = Pack Type × Pack Size`.

### Output

```text
outputs/sales_master.csv
```

Master là bảng wide: GSV và Turnover nằm trên cùng một grain. Discount và rate là derived fields; mapping và source lineage nằm cùng dòng.

## 3. Data-quality policy

Master không xóa grain lỗi. Mọi grain được giữ lại và phân loại:

- `VALID`: dùng được, không warning.
- `REVIEW`: dùng được nhưng cần disclosure.
- `INVALID`: không dùng mặc định trong governed analysis.

Filter governed:

```text
certified_for_analysis = True
```

Blocking conditions:

- GSV/Turnover record count khác 1.
- Turnover lớn hơn GSV.
- Customer/Brand/Product mapping thiếu.

Review conditions:

- Giá trị âm.
- Product mapping được đánh dấu cần business review.

## 4. Storyline contract

Nguồn chuẩn là `STORYLINE_METRIC_FRAMEWORK.md`.

Bốn section:

1. Growth & Market.
2. How We Sell / Gross-to-Net Quality.
3. P&L and Profit Quality.
4. Call to Action.

Storyline sử dụng Product Demand & Pack Mix Proxy thay cho physical Volume và không đưa ra kết luận PVM, distribution, promotion ROI hoặc channel contribution margin khi chưa có nguồn tương ứng.

## 5. Output policy

Được duy trì:

- `sales_master.csv`
- `analysis_pack.json`
- `story_review.md`
- `run_summary.json`
- Approved PowerPoint nếu cần

Không còn tạo:

- `finance_dashboard.xlsx`

## 6. Definition of done

- Script tự phát hiện toàn bộ Customer Sales files.
- Master join đầy đủ Customer, Channel, Brand và exact Product.
- GSV/Turnover/Discount cùng nằm trên một grain.
- Master có lineage và quality flags.
- P&L và Market hashes không đổi sau khi chạy.
- Storyline `.md` có metric, công thức, dimension, caveat và report flow.
- Pipeline không tạo Excel dashboard.
- Automated tests pass.
