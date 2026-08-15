# UniSweet — Storyline và Metric Contract

## 1. Mục đích

Tài liệu này là sườn phân tích cho một báo cáo quản trị ngắn, đi theo chuỗi câu hỏi:

> Kết quả thay đổi thế nào → thay đổi tập trung ở đâu → chất lượng doanh thu ra sao → lợi nhuận có bền vững không → management nên làm gì tiếp theo?

Tài liệu chỉ định nghĩa storyline, metric, công thức, dimension và giới hạn diễn giải. Chưa điền số và không mặc định bất kỳ kết luận kinh doanh nào trước khi chạy dữ liệu.

## 2. Nguồn dữ liệu và grain được hỗ trợ

| Nguồn | Grain hỗ trợ | Trường chính | Vai trò |
|---|---|---|---|
| Sales master | Month × Customer × Brand × exact Product | GSV, Turnover, Discount, mapping, quality flags | Growth, driver, pack mix và Gross-to-Net |
| Customer Mapping | Customer | Customer Name, Channel | Customer/Channel cut |
| Brand Mapping | Brand | Brand Name | Brand cut |
| Product Mapping | Pack Type × Pack Size | Product Group LV1/LV2/LV3 | Exact product và pack mix |
| P&L | Brand × Year | GSV, Discount, TO, Supply Chain Cost, GP, Marketing, PBO | Profit quality |
| Market | MAT Period × Channel × Segment × Manufacturer × Brand | Sales Value, Value Share | Directional market context |

### 2.1 Dimension chuẩn

| Dimension | Giá trị sử dụng | Lưu ý |
|---|---|---|
| Time | Month, Year | Sales dùng monthly; P&L dùng annual; Market dùng MAT |
| Customer | Customer Code, Customer Name | Customer Code là khóa chính |
| Channel | Channel Code | Hiện được suy ra từ Customer Mapping |
| Brand | Brand Code, Brand Name | Sales join bằng Brand Code; P&L/Market dùng Brand Name |
| Product | Product Key = Pack Type + Pack Size | Grain sản phẩm chính xác nhất của Sales |
| Pack | Pack Type, Pack Size, Product Group LV1/LV2 | Dùng cho product mix, không phải physical volume |
| Market | Channel, Segment, Manufacturer, Brand | Không nối trực tiếp xuống Customer/Product nội bộ |

### 2.2 Quy tắc kỳ so sánh

1. Sales headline mặc định dùng tháng mới nhất so với cùng tháng năm trước.
2. Nếu không có cùng tháng năm trước, mới dùng tháng liền trước và phải ghi rõ `MoM`.
3. P&L so sánh full year hiện tại với full year liền trước.
4. Market giữ đúng kỳ MAT ghi trong nguồn.
5. Không trình bày Sales calendar month/year và Market MAT như hai kỳ hoàn toàn đồng nhất.
6. Mọi chart/table phải ghi rõ kỳ, basis so sánh và đơn vị.

## 3. Executive storyline

### Headline template

> Turnover thay đổi **[X]%** so với **[comparison period]**, với mức thay đổi tập trung tại **[Brand]**, **[Channel]** và **[Product/Pack]**. Chất lượng Gross-to-Net **[cải thiện/suy yếu]**, nhưng diễn biến không đồng nhất giữa các phân khúc. Ở cấp P&L, **[GP/GM/PBO]** cho thấy lợi nhuận **[được hỗ trợ bởi hoạt động lõi/được bảo vệ chủ yếu nhờ giảm chi phí]**. Management nên ưu tiên **[2–3 hành động có owner và evidence]**.

### Logic kể chuyện

1. **What changed?** — TO/GSV thay đổi bao nhiêu?
2. **Where did it change?** — Brand, Channel, Customer và Pack nào đóng góp chính?
3. **Is the revenue quality healthy?** — Discount intensity và Gross-to-Net thay đổi thế nào?
4. **Is profit quality sustainable?** — GM/PBO thay đổi do GP hay do Marketing Expense?
5. **What should management do?** — Hành động nào được hỗ trợ trực tiếp bởi dữ liệu và cần kiểm chứng gì thêm?

---

## 4. Section 1 — Growth & Market

### Câu hỏi quyết định

> Kết quả kinh doanh thay đổi thế nào, và thay đổi tập trung ở đâu?

### 4.1 Turnover Growth

**Công thức**

```text
TO Growth % = Current Period TO / Prior Comparable Period TO - 1
TO Variance = Current Period TO - Prior Comparable Period TO
```

**Dimension áp dụng**

- Total
- Brand
- Channel
- Customer
- Exact Product (`Pack Type × Pack Size`)

**Cách diễn giải**

- Dùng TO làm headline vì đây là doanh thu sau Discount.
- Luôn trình bày đồng thời giá trị hiện tại, variance tuyệt đối và growth %.
- Không gọi TO Growth là Volume Growth.

### 4.2 GSV Growth

**Công thức**

```text
GSV Growth % = Current Period GSV / Prior Comparable Period GSV - 1
GSV Variance = Current Period GSV - Prior Comparable Period GSV
```

**Dimension áp dụng**

- Total, Brand, Channel, Customer, Exact Product

**Vai trò trong storyline**

- So sánh tốc độ thay đổi GSV và TO để hiểu biến động trước/sau Discount.
- GSV không phải price effect và không được dùng để thay thế price realization.

### 4.3 Growth Contribution

**Công thức**

```text
Entity TO Variance = Entity Current TO - Entity Prior TO
Variance Contribution % = Entity TO Variance / Total TO Variance
```

**Dimension áp dụng riêng rẽ**

- Brand
- Channel
- Customer
- Exact Product

**Quy tắc kiểm soát**

- Mỗi dimension là một cách phân rã của cùng Total variance.
- Không cộng contribution của Brand với Channel hoặc Product.
- Contribution có thể lớn hơn 100% nếu một entity giảm mạnh và entity khác bù tăng.

### 4.4 Product Demand & Pack Mix Proxy

Đây là chỉ số thay thế cho Volume khi nguồn chưa có unit/case/kg bán ra.

#### A. TO Mix

```text
Product TO Mix % = Product TO / Total TO
Brand–Product Mix % = Brand × Product TO / Total Brand TO
```

#### B. Product Growth

```text
Product TO Growth % = Product Current TO / Product Prior TO - 1
```

#### C. Customer Penetration Proxy

```text
Active Customer = Customer có TO > 0 trong kỳ
Product Customer Penetration % =
    Số Active Customer mua Product / Tổng Active Customer trong cùng kỳ
```

#### D. Customer–Month Recurrence

```text
Customer–Month Recurrence % =
    Số Customer × Month có TO > 0 / Tổng Customer × Month khả dụng
```

#### E. Discount Dependency by Product

```text
Product Discount % TO = Product Discount / Product TO
Product Discount Movement bps =
    (Current Product Discount % TO - Prior Product Discount % TO) × 10,000
```

**Dimension áp dụng**

- Pack Type
- Pack Size
- Exact Product
- Brand × Pack Type
- Brand × Exact Product
- Channel × Exact Product
- Customer × Exact Product

**Ngôn ngữ được phép**

- “Format có giá trị sell-in lớn nhất.”
- “Pack mix đang dịch chuyển sang/khỏi format X.”
- “Format có độ phủ trong tập khách hàng UniSweet cao hơn.”
- “Product demand proxy tăng/giảm.”

**Ngôn ngữ không được phép**

- “Physical volume tăng/giảm.”
- “Người tiêu dùng mua nhiều/ít pack hơn.”
- “Realized price per gram tăng/giảm.”
- “Numeric Distribution toàn thị trường tăng/giảm.”

### 4.5 Market Value Growth và Value Share

**Công thức**

```text
Market Value Growth % = Sales Value MAT / Sales Value MAT-1 - 1
Value Share = Brand or Manufacturer Sales Value / Category Sales Value
Share Movement pp = Value Share MAT - Value Share MAT-1
```

Nếu nguồn đã cung cấp Value Share, dùng trực tiếp giá trị nguồn và kiểm tra công thức thay vì tính lại để thay thế source.

**Dimension áp dụng**

- Total Market
- Channel
- Segment
- Manufacturer
- Brand

**Directional growth gap**

```text
Internal vs Market Growth Gap pp =
    Internal Calendar-Year TO Growth % - Market MAT Value Growth %
```

**Caveat bắt buộc**

- Growth gap chỉ là directional context vì calendar-year sell-in và MAT market khác kỳ.
- Value Share không chứng minh Numeric/Weighted Distribution.
- Share movement không tự động chứng minh đối thủ “đẩy” UniSweet khỏi điểm bán.

### Output đề xuất cho Section 1

1. Headline TO/GSV card.
2. Một bar chart Top positive/negative TO drivers.
3. Một bảng Brand × Product/Pack gồm TO Mix, Growth và Contribution.
4. Một bảng Market signal ngắn theo Brand.

---

## 5. Section 2 — How We Sell / Gross-to-Net Quality

### Câu hỏi quyết định

> Doanh thu đang được tạo ra với chất lượng thương mại tốt hơn hay phụ thuộc nhiều hơn vào Discount?

### 5.1 Discount Amount

```text
Discount = GSV - Turnover
Discount Variance = Current Discount - Prior Discount
Discount Growth % = Current Discount / Prior Discount - 1
```

**Dimension áp dụng**

- Total, Brand, Channel, Customer, Exact Product

### 5.2 Discount Intensity

Nên công bố cả hai mẫu số để tránh nhầm nghĩa.

```text
Discount % TO = Discount / Turnover
Discount % GSV = Discount / GSV

Discount % TO Movement bps =
    (Current Discount % TO - Prior Discount % TO) × 10,000

Discount % GSV Movement bps =
    (Current Discount % GSV - Prior Discount % GSV) × 10,000
```

**Quy tắc**

- Ratio phải tính từ tổng numerator chia tổng denominator.
- Không average tỷ lệ từng dòng.
- Ghi rõ denominator trong mọi title/label.

### 5.3 Gross-to-Net Bridge

```text
Prior TO
+ GSV Change
- Discount Change
= Current TO
```

Tương đương:

```text
Current TO - Prior TO = (Current GSV - Prior GSV) - (Current Discount - Prior Discount)
```

**Cách diễn giải**

- Bridge cho biết thay đổi trước và sau Discount.
- Bridge không phải Price–Volume–Mix.

### 5.4 Discount Leakage Diagnostic

**Bốn quadrant**

| TO movement | Discount rate movement | Diễn giải |
|---|---|---|
| Down | Up | Ưu tiên điều tra leakage |
| Up | Up | Kiểm tra tăng trưởng có đủ bù chiết khấu không |
| Down | Down | Doanh thu giảm dù đã giảm rate; tìm driver phi-discount |
| Up | Down | Tín hiệu Gross-to-Net tích cực |

**Recovery proxy**

```text
Recovery Proxy = MAX(
    (Current Discount % TO - Prior Discount % TO) × Current TO,
    0
)
```

**Dimension áp dụng**

- Brand
- Channel
- Customer
- Exact Product
- Nên bổ sung Brand × Channel và Customer × Product trong phân tích chi tiết

**Caveat bắt buộc**

- Recovery Proxy là diagnostic opportunity.
- Không phải target, forecast, saving đã cam kết hoặc Promotion ROI.
- Chỉ chuyển thành action value sau khi xác minh hợp đồng/promotion mechanic.

### 5.5 Commercial Efficiency Proxy

Khi chưa có promotion spend và incremental volume, chỉ sử dụng rule-based diagnostic:

```text
High-risk commercial cell =
    TO Growth < 0 AND Discount Rate Movement > 0
```

Có thể xếp hạng bằng:

```text
Priority Score =
    Revenue-at-Risk Rank
    + Discount Rate Deterioration Rank
    + Recovery Proxy Rank
```

Không gọi chỉ số này là elasticity hoặc ROI.

### Output đề xuất cho Section 2

1. Gross-to-Net bridge.
2. Discount % TO và % GSV: current, prior, movement.
3. Top 5 leakage cells với dimension, TO variance, rate movement và proxy.
4. Một câu caveat ngay dưới bảng.

---

## 6. Section 3 — P&L and Profit Quality

### Câu hỏi quyết định

> Lợi nhuận thay đổi do hoạt động lõi tốt hơn hay do giảm đầu tư/chi phí?

### 6.1 Gross Profit và Gross Margin

```text
Gross Profit = Turnover - Total Supply Chain Cost
Gross Margin % = Gross Profit / Turnover
Gross Margin Movement bps =
    (Current GM % - Prior GM %) × 10,000
```

**Dimension áp dụng**

- Total
- Brand
- Year

Không phân bổ GP xuống Channel/Customer/Product nếu source P&L chưa hỗ trợ.

### 6.2 PBO và PBO Margin

```text
PBO = Gross Profit - Marketing Expense
PBO Margin % = PBO / Turnover
PBO Margin Movement bps =
    (Current PBO Margin % - Prior PBO Margin %) × 10,000
```

**Tên metric bắt buộc**

- Dùng `PBO Margin`.
- Không đổi tên thành `Operating Margin` vì PBO chưa bao gồm overhead treatment đầy đủ.

### 6.3 Profit Quality Bridge

```text
PBO Variance = Gross Profit Variance - Marketing Expense Variance
```

**Logic diễn giải**

- GP tăng và PBO tăng: hoạt động lõi và bottom-line cùng cải thiện.
- GP giảm nhưng PBO tăng nhờ Marketing giảm: lợi nhuận được bảo vệ bằng giảm đầu tư.
- GM tăng nhưng TO giảm: economics/unit mix có thể tốt hơn nhưng scale suy yếu.
- PBO Margin tăng không tự động có nghĩa tăng trưởng bền vững.

### 6.4 Brand Economics

**Bảng metric theo Brand**

- TO và TO Growth
- GP và GP Growth
- GM % và movement bps
- Marketing Expense và variance
- PBO và PBO Growth
- PBO Margin % và movement bps
- Market Value Growth/Share như directional context

**Không sử dụng**

- Contribution Margin theo Channel/Product.
- Customer profitability.
- Operating Margin.

Các chỉ số trên chỉ được bổ sung khi có direct trade spend, variable logistics, cost-to-serve và overhead allocation tương ứng.

### Output đề xuất cho Section 3

1. Total P&L bridge: GP variance → Marketing variance → PBO variance.
2. Bảng Brand economics tối đa 3–5 dòng.
3. Một callout phân biệt core improvement với cost reduction.

---

## 7. Section 4 — Call to Action

### Câu hỏi quyết định

> Management nên can thiệp ở đâu trước, dựa trên bằng chứng nào và cần xác minh điều gì?

### 7.1 Action 1 — Revenue Recovery

**Chọn đối tượng ưu tiên bằng**

- TO Variance âm lớn.
- Variance Contribution cao.
- Tập trung tại tổ hợp Brand–Channel–Product cụ thể.
- Customer Penetration hoặc Recurrence suy yếu nếu đã tính.

**Dimension khuyến nghị**

- Brand × Channel
- Channel × Customer
- Brand × Exact Product
- Customer × Exact Product

**Action template**

> Phục hồi **[Brand–Channel–Product]** bằng cách xác minh availability, customer inventory, assortment, sell-in timing và customer execution trước kỳ review tiếp theo.

### 7.2 Action 2 — Discount Control

**Chọn đối tượng ưu tiên bằng**

- TO giảm.
- Discount % TO/GSV tăng.
- Recovery Proxy lớn.
- Discount dependency cao so với prior period.

**Action template**

> Rà soát **[Customer/Product]** có TO giảm và discount rate tăng; phân loại contract, promotion, listing support, rebate và invoice exception trước khi xác nhận saving.

### 7.3 Action 3 — Portfolio and Investment Allocation

**Chọn đối tượng ưu tiên bằng**

- Brand growth và Brand economics.
- Pack Mix, Product Growth và Customer Penetration Proxy.
- Internal vs Market directional gap.
- GM/PBO margin theo Brand.

**Action template**

> Bảo vệ investment ở các Brand/Pack có demand proxy và market signal tích cực; yêu cầu recovery plan cho các Brand/Pack có sell-in giảm hoặc mất Value Share.

### 7.4 Trường bắt buộc của mỗi action

| Trường | Nội dung |
|---|---|
| Evidence | 2–3 số liệu trực tiếp hỗ trợ hành động |
| Financial impact | TO at risk hoặc diagnostic recovery proxy |
| Owner | Role chịu trách nhiệm |
| Timing | Mốc review hoặc thời hạn |
| Validation needed | Dữ liệu/giả thuyết cần kiểm tra |
| Caveat | Điều metric hiện tại chưa chứng minh |

---

## 8. Metric contract tổng hợp

| Metric | Công thức lõi | Time | Dimension | Trạng thái nguồn hiện tại |
|---|---|---|---|---|
| TO Growth | Current TO / Prior TO - 1 | Month/Year | Total, Brand, Channel, Customer, Product | Supported |
| GSV Growth | Current GSV / Prior GSV - 1 | Month/Year | Total, Brand, Channel, Customer, Product | Supported |
| Growth Contribution | Entity ΔTO / Total ΔTO | Month | Brand/Channel/Customer/Product riêng rẽ | Supported |
| Product TO Mix | Product TO / Total TO | Month/Year | Product, Brand × Product | Supported |
| Customer Penetration Proxy | Active customers buying product / active customers | Month/Year | Product, Brand × Product | Derivable from master |
| Customer–Month Recurrence | Positive customer-months / available customer-months | Rolling period | Product, Brand × Product | Derivable from master |
| Market Value Growth | MAT / MAT-1 - 1 | MAT | Channel, Segment, Manufacturer, Brand | Supported |
| Value Share | Entity market value / Category market value | MAT | Channel, Segment, Manufacturer, Brand | Supported |
| Discount | GSV - TO | Month/Year | Total, Brand, Channel, Customer, Product | Supported |
| Discount % TO | Discount / TO | Month/Year | Total, Brand, Channel, Customer, Product | Supported |
| Discount % GSV | Discount / GSV | Month/Year | Total, Brand, Channel, Customer, Product | Supported |
| Recovery Proxy | MAX((Current rate - Prior rate) × Current TO, 0) | Month | Brand, Channel, Customer, Product | Supported as diagnostic |
| Gross Margin % | GP / TO | Year | Total, Brand | Supported |
| PBO Margin % | PBO / TO | Year | Total, Brand | Supported |
| Physical Volume Growth | Current units/kg / Prior units/kg - 1 | Month/Year | Product and cuts | Not supported |
| PVM | Price + Volume + Mix effects | Month/Year | Product/Brand | Not supported |
| Numeric/Weighted Distribution | Outlet presence and category-weighted presence | Period | Outlet/Product | Not supported |
| Promotion Elasticity/ROI | Incremental volume/value relative to promo input | Event/Period | Promotion/Product/Customer | Not supported |
| Contribution Margin by Channel | (TO - variable costs) / TO | Year/Month | Channel/Product/Customer | Not supported |
| Realized Price per Gram | TO / total grams sold | Month | Product | Not supported |

## 9. Data quality và filter contract cho Sales master

### Filter mặc định cho phân tích certified

```text
certified_for_analysis == True
```

### Quality flags cần theo dõi

- KPI GSV/Turnover thiếu hoặc duplicate.
- Turnover lớn hơn GSV.
- Giá trị âm.
- Customer/Brand/Product mapping thiếu.
- Product mapping cần business review.

### Quy tắc xử lý

1. Master giữ lại mọi grain để bảo toàn lineage.
2. Grain lỗi blocking được đánh dấu `INVALID`, không bị xóa khỏi master.
3. Grain hợp lệ nhưng có cảnh báo được đánh dấu `REVIEW`.
4. Báo cáo chính mặc định chỉ dùng `certified_for_analysis = True`.
5. Mọi loại trừ material phải được disclose trong caveat.

## 10. Cấu trúc report ngắn đề xuất

### Trang/Section 1 — Executive Summary

- Headline TO/GSV.
- Ba driver lớn nhất.
- Một câu về Gross-to-Net.
- Một câu về profit quality.
- Ba actions.

### Trang/Section 2 — Growth Drivers and Pack Mix

- TO trend.
- Brand/Channel/Product contribution.
- Product Demand & Pack Mix Proxy.
- Market signal theo Brand.

### Trang/Section 3 — Gross-to-Net and Profit Quality

- Gross-to-Net bridge.
- Leakage priority table.
- GP/GM/PBO bridge.
- Brand economics.

### Appendix nếu cần

- Metric definitions.
- Data quality/exclusions.
- Source periods và lineage.

## 11. Guardrails cho câu chữ

| Có thể kết luận | Không được kết luận từ nguồn hiện tại |
|---|---|
| TO/GSV tăng hoặc giảm | Physical volume tăng hoặc giảm |
| Product/Pack nào có sell-in value và mix cao | Người tiêu dùng thích sản phẩm hơn theo unit sell |
| Discount intensity tăng hoặc giảm | Promotion gây ra incremental volume |
| Recovery opportunity mang tính diagnostic | Promotion ROI hoặc committed saving |
| Brand Value Share thay đổi | Weighted/Numeric Distribution thay đổi |
| PBO tăng do GP hoặc Marketing Expense | Operating Profit nếu chưa có overhead đầy đủ |
| GM/PBO theo Brand | Contribution Margin theo Channel/Product |

## 12. Definition of done cho storyline cuối

- Mọi headline có metric, kỳ và dimension rõ ràng.
- Mọi total variance reconcile với các driver trong cùng dimension.
- Sales, P&L và Market được ghi đúng kỳ riêng.
- Không sử dụng Volume/PVM/Distribution/ROI/CM nếu chưa có nguồn tương ứng.
- Product preference luôn được gọi là sell-in/product-demand proxy.
- Mỗi action có evidence, owner, timing, validation và caveat.
- Report chính không quá ba section/trang ngoài appendix.
