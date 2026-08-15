# UniSweet — Storyline và Metric Framework

## 1. Phạm vi dữ liệu

Storyline chỉ sử dụng ba nguồn hiện có:

| Nguồn | Cách sử dụng | Grain thực tế |
|---|---|---|
| `outputs/sales_master.csv` | Dùng script để gộp Sales và Mapping | Month × Customer × Brand × Pack Type × Pack Size |
| `inputs/pnl/P&L Table.xlsx` | Mở và đọc trực tiếp trong Excel | Brand × Year |
| `inputs/market/Market Report MAT Nov'24.xlsx` | Mở và đọc trực tiếp trong Excel | MAT Period × Channel × Segment × Manufacturer × Brand |

Không có script xử lý P&L hoặc Market. Hai file này được giữ nguyên để tham khảo trực tiếp.

## 2. Sườn storyline ngắn

> **Sales thay đổi thế nào → Brand/Channel/Customer/Product nào tạo ra thay đổi → Discount tác động thế nào đến Turnover → P&L cho thấy chất lượng lợi nhuận ra sao → Market cho thấy vị thế giá trị của từng Brand thế nào → cần ưu tiên hành động ở đâu?**

Report nên có ba phần:

1. **Sales performance and drivers** — lấy từ Sales master.
2. **Profit and Market context** — đọc trực tiếp từ hai file Excel.
3. **Management actions** — kết nối evidence của ba nguồn.

---

## 3. Sales performance and drivers

### 3.1 Filter dữ liệu

Phân tích chính dùng:

```text
certified_for_analysis = True
```

Các dòng `REVIEW` vẫn được giữ trong tập certified nhưng cần đọc `data_quality_flags`. Các dòng `INVALID` không dùng trong headline.

### 3.2 Dimension có thể dùng

| Dimension | Cột trong Sales master |
|---|---|
| Time | `reporting_month`, `reporting_year`, `month_number` |
| Customer | `customer_code`, `customer_name` |
| Channel | `channel_code` |
| Brand | `brand_code`, `brand_name` |
| Exact Product | `product_key`, `product_name` |
| Pack | `pack_type`, `pack_size`, `product_group_lv1`, `product_group_lv2` |

### 3.3 Turnover

Turnover là headline Sales chính.

```text
TO Current = SUM(turnover_keur) trong kỳ hiện tại
TO Prior = SUM(turnover_keur) trong kỳ so sánh
TO Variance = TO Current - TO Prior
TO Growth % = TO Current / TO Prior - 1
```

Dimension:

- Total
- Brand
- Channel
- Customer
- Exact Product hoặc Pack

Kỳ so sánh ưu tiên: tháng mới nhất so với cùng tháng năm trước. Có thể dùng full-year so với full-year nếu tất cả 12 tháng đều đủ.

### 3.4 Gross Sales Value

```text
GSV Current = SUM(gsv_keur) trong kỳ hiện tại
GSV Prior = SUM(gsv_keur) trong kỳ so sánh
GSV Variance = GSV Current - GSV Prior
GSV Growth % = GSV Current / GSV Prior - 1
```

Dimension giống Turnover.

GSV cho biết giá trị trước Discount; Turnover cho biết giá trị sau Discount.

### 3.5 Driver contribution

```text
Entity TO Variance = Entity TO Current - Entity TO Prior
Variance Contribution % = Entity TO Variance / Total TO Variance
```

Tính riêng cho từng dimension:

- Brand contribution
- Channel contribution
- Customer contribution
- Product contribution

Không cộng contribution giữa các dimension vì chúng cùng giải thích một Total TO Variance.

### 3.6 Product và Pack mix

```text
Product TO Mix % = Product TO / Total TO
Pack Type TO Mix % = Pack Type TO / Total TO
Brand–Product Mix % = Brand × Product TO / Total Brand TO
Product TO Growth % = Product TO Current / Product TO Prior - 1
```

Dimension:

- Pack Type
- Pack Size
- Exact Product
- Brand × Product
- Channel × Product

Cách diễn giải phù hợp:

- Product/Pack nào có sell-in value lớn nhất.
- Mix doanh thu đang chuyển sang hoặc rời khỏi Product/Pack nào.
- Product/Pack nào đóng góp tăng hoặc giảm Turnover.

Pack Size chỉ định danh format sản phẩm. Không dùng Pack Size để tự tính số pack hoặc tổng trọng lượng bán ra.

### 3.7 Active customer và customer penetration

```text
Active Customer = Customer có turnover_keur > 0 trong kỳ
Product Active Customers = COUNT DISTINCT customer_code có Product TO > 0
Product Customer Penetration % =
    Product Active Customers / Total Active Customers trong cùng kỳ
```

Dimension:

- Product
- Brand × Product
- Channel × Product

Đây là độ phủ trong tập khách hàng có dữ liệu của UniSweet, không phải độ phủ toàn thị trường.

### 3.8 Discount và Gross-to-Net

Các cột đã có trong Sales master:

```text
Discount = GSV - Turnover
```

Khi tổng hợp lại phải dùng:

```text
Discount Amount = SUM(discount_keur)
Discount % TO = SUM(discount_keur) / SUM(turnover_keur)
Discount % GSV = SUM(discount_keur) / SUM(gsv_keur)

Discount Rate Movement bps =
    (Current Discount Rate - Prior Discount Rate) × 10,000
```

Không average trực tiếp các cột `discount_pct_to` hoặc `discount_pct_gsv` theo dòng.

Dimension:

- Total
- Brand
- Channel
- Customer
- Product

### 3.9 Sales storyline template

> Turnover **[tăng/giảm X%]** so với **[kỳ so sánh]**. Thay đổi tập trung tại **[Brand]**, **[Channel]**, **[Customer]** và **[Product/Pack]**. Product mix cho thấy **[format tăng/giảm đóng góp]**. Discount % **[TO/GSV]** thay đổi **[X bps]**, cho biết Gross-to-Net **[cải thiện/suy yếu]** tại **[dimension]**.

---

## 4. P&L — đọc trực tiếp trong Excel

Nguồn: `inputs/pnl/P&L Table.xlsx`, sheet `PnL table`.

Không join hoặc phân bổ P&L xuống Customer, Channel hay Product. Dimension được hỗ trợ chỉ gồm:

- Brand
- Total
- Year

### 4.1 Metrics dùng được

| Metric | Công thức/nguồn |
|---|---|
| GSV Growth % | Current GSV / Prior GSV - 1 |
| Discount | Dòng Discount trong P&L |
| Turnover Growth % | Current TO / Prior TO - 1 |
| Supply Chain Cost | Dòng Total Supply Chain Cost |
| Gross Profit | Turnover - Supply Chain Cost |
| Gross Margin % | Gross Profit / Turnover |
| GM Movement bps | (Current GM % - Prior GM %) × 10,000 |
| Marketing Expense | Dòng Marketing Expense |
| PBO | Gross Profit - Marketing Expense |
| PBO Margin % | PBO / Turnover |
| PBO Margin Movement bps | (Current PBO Margin % - Prior PBO Margin %) × 10,000 |

### 4.2 Profit quality logic

```text
PBO Variance = Gross Profit Variance - Marketing Expense Variance
```

Đọc theo thứ tự:

1. Turnover tăng hay giảm?
2. Gross Profit và Gross Margin thay đổi thế nào?
3. Marketing Expense thay đổi bao nhiêu?
4. PBO thay đổi do Gross Profit hay do Marketing Expense?
5. Brand nào có GM/PBO Margin mạnh hoặc yếu nhất?

### 4.3 P&L storyline template

> Trong năm **[Year]**, Turnover **[tăng/giảm]**, Gross Margin thay đổi **[X bps]** và Gross Profit **[tăng/giảm]**. PBO **[tăng/giảm]** chủ yếu do **[Gross Profit/Marketing Expense]**. Diễn biến tập trung tại Brand **[X]**.

---

## 5. Market — đọc trực tiếp trong Excel

Nguồn: `inputs/market/Market Report MAT Nov'24.xlsx`, sheet `Market Data`.

Dimension được hỗ trợ:

- Channel
- Segment
- Manufacturer
- Brand
- MAT period

### 5.1 Metrics dùng được

```text
Market Value Growth % = Sales Value MAT / Sales Value MAT-1 - 1
Sales Value Movement = Sales Value MAT - Sales Value MAT-1
Value Share MAT = giá trị Value Share trong source
Share Movement pp = Value Share MAT - Value Share MAT-1
```

Nếu source đã có `Gain/Loss`, dùng để kiểm tra lại phép tính.

### 5.2 Cách đọc

1. Total Category Sales Value tăng hay giảm?
2. UniSweet Sales Value và Value Share tăng hay giảm?
3. Brand nào tăng/giảm Sales Value mạnh nhất?
4. Brand nào tăng/giảm Value Share?
5. Kết quả khác nhau thế nào giữa Total, MT và DT?

Market là MAT; Sales master là calendar month/year. Trình bày hai nguồn thành hai khối riêng và ghi rõ kỳ.

### 5.3 Market storyline template

> Trong kỳ **[MAT period]**, Category Sales Value **[tăng/giảm]**. UniSweet Value Share thay đổi **[X điểm phần trăm]**, với biến động tập trung tại Brand **[X]** và Channel **[X]**.

---

## 6. Management actions

Chỉ đề xuất action từ các bằng chứng có trong ba nguồn.

### Action 1 — Sales recovery

Ưu tiên Brand–Channel–Customer–Product có:

- TO Variance âm lớn.
- Variance Contribution cao.
- Product/Pack mix giảm.
- Active customer count giảm.

### Action 2 — Discount review

Ưu tiên dimension có:

- Turnover giảm.
- Discount % TO hoặc Discount % GSV tăng.
- Discount amount material.

### Action 3 — Brand investment review

Đối chiếu thủ công:

- Sales master: Brand TO Growth và Product mix.
- P&L: Brand GM, Marketing Expense và PBO.
- Market Excel: Brand Sales Value và Value Share.

Mỗi action cần ghi rõ:

- Evidence.
- Financial impact đang quan sát được.
- Owner.
- Timing.
- Điều cần management xác minh thêm.

## 7. Cấu trúc report đề xuất

### Trang 1 — Executive summary

- TO/GSV headline.
- Ba Sales drivers lớn nhất.
- Discount rate movement.
- Một câu P&L.
- Một câu Market.
- Ba actions.

### Trang 2 — Sales drivers

- TO trend.
- Brand/Channel/Customer/Product contribution.
- Product/Pack mix.
- Discount by dimension.

### Trang 3 — P&L and Market context

- P&L table theo Brand và Total, đọc trực tiếp từ Excel.
- Market Value Growth và Value Share theo Brand/Channel, đọc trực tiếp từ Excel.
- Management actions và caveat về kỳ dữ liệu.
