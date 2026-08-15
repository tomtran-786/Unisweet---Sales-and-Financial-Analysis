Có. Tôi đã đối chiếu brief case này với cách Unilever thực tế mô tả và quản trị performance. Điểm quan trọng nhất là: **Financial Performance Analysis trong một case FBP không phải là “tính càng nhiều ratio càng tốt”**. Mục tiêu là xây một **driver tree** để trả lời:

> **Business đang tăng trưởng hay giảm → tăng/giảm vì đâu → growth đó có profitable không → value bị mất ở đâu → management nên làm gì.**

Đây cũng đúng với brief: vai trò FBP phải biến dữ liệu thành **actionable insights**, phát hiện risk/growth opportunity fileciteturn0file0L5-L12; case yêu cầu Sales Analysis theo brand/product/channel/customer và Discount, sau đó Financial Analysis 2023–2024 YoY, cuối cùng mới đưa ra 3 strategic actions. fileciteturn0file0L22-L35

Đáng chú ý, framework quản trị thật của Unilever cũng rất gần logic này: mục tiêu value creation được mô tả bằng **absolute profit growth**, với hai động cơ lớn là **volume growth** và **gross-margin expansion**. citeturn305857view0 Unilever đồng thời xem underlying operating profit/margin là thước đo chính để đánh giá segment và phân bổ nguồn lực. citeturn860837view2

---

# 1. Cách một FBP nên breakdown câu hỏi

Tôi sẽ không bắt đầu bằng P&L.

Tôi sẽ bắt đầu bằng **decision question**:

### Level 1 — Business có thực sự khỏe hơn không?

Ba câu đầu tiên:

**Are we growing?**

→ Turnover / Net Sales  
→ Volume  
→ Market share

**Is the growth profitable?**

→ Gross Profit  
→ Gross Margin  
→ Operating Profit  
→ Operating Margin

**Is the growth sustainable?**

→ Volume vs price  
→ Discount intensity  
→ Mix  
→ Investment level  
→ Cash / ROIC nếu có dữ liệu.

Sau đó mới hỏi:

### Level 2 — Tại sao performance thay đổi?

Financial driver tree nên giống:

```text
                         PROFITABLE GROWTH
                                │
             ┌──────────────────┴──────────────────┐
             │                                     │
          TURNOVER                              PROFIT
             │                                     │
      ┌──────┼──────┐                    ┌─────────┴─────────┐
    Volume  Price   Mix              Gross Profit          OPEX
      │       │      │                    │                  │
   Brand    Price  Product            COGS              Marketing
   SKU      Promo  Channel         Commodity             Selling
 Customer         Customer         Productivity          Overhead
```

Nhưng case này còn có một layer cực kỳ quan trọng:

```text
GSV
 │
 ├── Discount / Trade Spend
 ↓
TURNOVER
 │
 ├── COGS
 ↓
GROSS PROFIT
 │
 ├── Brand & Marketing Investment
 ├── Selling / Distribution
 ├── Overheads
 ↓
OPERATING PROFIT
```

Đây mới chính là **financial storyline**.

---

# 2. Thứ tự metrics tôi sẽ quan tâm

Nếu chỉ được nhìn **10 metrics trước khi đưa ra quyết định**, tôi sẽ ưu tiên như sau.

| Rank | Metric | Câu hỏi management | Công thức |
|---|---|---|---|
| **1** | **Turnover YoY Growth** | Business có đang lớn lên không? | `(TO24 / TO23) - 1` |
| **2** | **Gross Margin %** | Mỗi € sales giữ lại được bao nhiêu sau product cost? | `Gross Profit / Turnover` |
| **3** | **Operating Profit & Margin** | Growth cuối cùng có tạo profit không? | `OP / Turnover` |
| **4** | **Volume Growth** | Growth đến từ consumer demand hay chỉ tăng giá? | `(Volume24 / Volume23) - 1` |
| **5** | **Discount % Turnover** | Có đang “mua revenue” bằng promotion không? | `(GSV - TO) / TO` |
| **6** | **Price / Mix Growth** | Revenue growth đến từ pricing/premiumisation hay volume? | xem dưới |
| **7** | **Gross Profit Growth** | Profit pool có thực sự lớn lên không? | `(GP24 / GP23)-1` |
| **8** | **Contribution Margin by Brand/SKU/Channel/Customer** | Value được tạo/mất ở đâu? | `(TO - attributable variable costs)/TO` |
| **9** | **Marketing / OPEX % Turnover** | Margin loss là investment hay inefficiency? | `Expense / TO` |
| **10** | **Cash Conversion / ROIC** | Accounting profit có biến thành cash/value không? | xem dưới |

Tôi sẽ coi **1–5 là mandatory**, **6–9 là diagnostic**, còn **10 là strategic/advanced**.

---

# 3. Metric #1 — Turnover: bắt đầu từ top line

Case sử dụng terminology **GSV và TO**, trong đó:

\[
Discount = GSV - TO
\]

Brief nói rõ điều này. fileciteturn0file0L26-L30

### Turnover growth

\[
\boxed{
TO\ Growth = \frac{TO_{2024}}{TO_{2023}}-1
}
\]

Ngoài percentage phải luôn show absolute change:

\[
\boxed{
\Delta TO=TO_{2024}-TO_{2023}
}
\]

Ví dụ:

```text
2023 TO = 100
2024 TO = 107

YoY = +7%
ΔTO = +7
```

Nhưng một FBP **không dừng ở +7%**.

Câu tiếp theo phải là:

> **“Where did the €7 growth come from?”**

Breakdown:

```text
Total
→ Brand
→ Product/SKU
→ Channel
→ Customer
```

Đúng với dimensions mà case yêu cầu. fileciteturn0file0L26-L30

---

# 4. Metric #2 — Gross Margin: metric cực kỳ quan trọng trong FMCG

\[
Gross\ Profit = Turnover - COGS
\]

\[
\boxed{
Gross\ Margin\%=\frac{Gross\ Profit}{Turnover}
}
\]

Và:

\[
COGS\%=\frac{COGS}{Turnover}
\]

Ví dụ:

| | 2023 | 2024 |
|---|---:|---:|
| Turnover | 100 | 110 |
| COGS | 60 | 63 |
| Gross Profit | 40 | 47 |
| GM | 40% | 42.7% |

Turnover:

> +10%

nhưng GP:

> +17.5%

→ đây là **high-quality growth**.

Unilever đặc biệt nhấn mạnh gross-margin expansion vì margin tạo ra khả năng **reinvest vào brand đồng thời tăng profitability**. Năm 2024, họ mô tả gross margin expansion đến từ volume leverage, mix, productivity và input costs; đồng thời margin expansion giúp tăng brand investment và operating profit. citeturn938694view3

### Không chỉ báo GM %, hãy báo basis points

\[
\boxed{
GM\ change\ (bps)
=(GM_{24}-GM_{23})\times10,000
}
\]

Ví dụ:

```text
2023 GM = 40.0%
2024 GM = 42.7%

Change = +270 bps
```

Senior management thường đọc:

> **“GM expanded +270 bps”**

nhanh hơn rất nhiều so với “42.7% vs 40.0%”.

---

# 5. Metric #3 — Operating Profit / Operating Margin

Đây là metric trả lời:

> **Sau sales, product cost, investment và overhead, business cuối cùng có tạo thêm profit không?**

\[
\boxed{
Operating\ Margin=\frac{Operating\ Profit}{Turnover}
}
\]

YoY:

\[
OP\ Growth=
\frac{OP_{24}}{OP_{23}}-1
\]

Margin movement:

\[
\Delta OM_{bps}
=(OM_{24}-OM_{23})\times10,000
\]

Ở Unilever, underlying operating profit/margin được dùng trực tiếp để **assess segment performance và allocate resources**. citeturn860837view2

Đây là lý do metric này cực kỳ quan trọng đối với FBP.

---

# 6. Metric #4 — Volume: phân biệt “growth thật” và “price growth”

Đây là nơi domain knowledge bắt đầu khác accounting.

Giả sử:

```text
Revenue +8%
```

Có hai business hoàn toàn khác nhau:

### Business A

```text
Volume +7%
Price +1%
```

→ demand khỏe.

### Business B

```text
Volume -5%
Price +14%
```

→ revenue vẫn tăng nhưng consumer demand đang suy yếu.

Với FMCG/confectionery, Scenario B đáng lo hơn rất nhiều.

Nếu có Unit / KG / Case:

\[
\boxed{
Volume\ Growth=
\frac{Volume_{24}}{Volume_{23}}-1
}
\]

Unilever cũng tách sales growth thành **volume và price**. Trong định nghĩa chính thức, UVG phản ánh turnover movement do volume và composition/mix, còn UPG phản ánh price changes. citeturn860837view1

---

# 7. Metric #5 — Discount % Turnover

Đây là metric tôi đặc biệt chú ý trong case này vì đề bài **chủ động yêu cầu nó**.

\[
Discount=GSV-TO
\]

Nếu metric được gọi chính xác là **Discount % Turnover**, tôi sẽ tính:

\[
\boxed{
Discount\%TO=
\frac{GSV-TO}{TO}
}
\]

Ví dụ:

```text
GSV = 120
TO = 100

Discount = 20

Discount % TO = 20 / 100 = 20%
```

Tôi cũng sẽ tính thêm:

\[
\boxed{
Discount\%GSV=
\frac{GSV-TO}{GSV}
}
\]

trong ví dụ:

\[
20/120=16.7\%
\]

Hai con số **không giống nhau**.

Do đó slide phải ghi rõ denominator.

---

## Một lỗi Excel/Power BI rất dễ mắc

Không nên:

```text
AVERAGE(Row Discount %)
```

Mà phải:

\[
\boxed{
Discount\%=
\frac{\sum Discount}{\sum TO}
}
\]

Tương tự Gross Margin:

\[
GM=
\frac{\sum GP}{\sum TO}
\]

**không phải average margin của từng row.**

Đây là vấn đề weighted aggregation rất thường gặp khi breakdown customer/SKU.

---

# 8. Metric #6 — Price / Mix

Nếu có volume:

\[
Realized\ Price=
\frac{Turnover}{Volume}
\]

Sau đó:

\[
\boxed{
Realized\ Price/Mix\ Growth=
\frac{TO_{24}/Volume_{24}}
{TO_{23}/Volume_{23}}-1
}
\]

Tuy nhiên cần nhớ:

**Ở aggregate level đây là Price + Mix proxy**, không phải pure price.

Ví dụ:

2023:

```text
50% premium chocolate
50% economy chocolate
```

2024:

```text
70% premium
30% economy
```

Average selling price tăng mặc dù từng SKU **không tăng giá**.

Vì vậy FBP phải hỏi:

> Pricing hay premiumisation/mix?

Muốn tách chuẩn phải xuống SKU.

---

# 9. Metric #7 — Gross Profit Growth

Một metric dễ bị bỏ qua:

\[
\boxed{
GP\ Growth=
\frac{GP_{24}}{GP_{23}}-1
}
\]

Tại sao tôi quan tâm hơn Net Profit trong case này?

Vì GP là **profit pool management có thể reinvest**:

```text
Gross Profit
→ Marketing
→ Promotion
→ Sales
→ Innovation
→ Operating Profit
```

Nên có thể xảy ra:

```text
Turnover       +5%
Gross Profit   +12%
Operating Prof +3%
```

Không nhất thiết xấu.

Có thể management đã deliberate reinvest phần GP thêm vào marketing.

Câu hỏi đúng là:

> **“Operating margin giảm vì inefficiency hay deliberate investment?”**

---

# 10. Metric #8 — Contribution Margin theo Brand / Product / Channel / Customer

Đây thường là analysis **giá trị nhất để ra quyết định**.

Turnover chỉ cho biết:

> Ai bán nhiều?

Contribution cho biết:

> **Ai thực sự kiếm tiền?**

Một công thức generic:

\[
Contribution=
TO
-COGS
-Trade\ Spend
-Variable\ Logistics
-Other\ attributable\ variable\ cost
\]

\[
\boxed{
Contribution\ Margin=
\frac{Contribution}{TO}
}
\]

Sau đó tạo matrix:

| | High growth | Low growth |
|---|---|---|
| **High margin** | INVEST | DEFEND |
| **Low margin** | FIX ECONOMICS | EXIT / RATIONALISE |

Đây là nơi financial analysis chuyển thành strategy.

Ví dụ:

```text
Customer A:
TO = 30m
Margin = 10%

Customer B:
TO = 20m
Margin = 25%
```

Nhìn sales:

> A quan trọng hơn B.

Nhìn economics:

```text
A contribution = 3m
B contribution = 5m
```

→ câu chuyện đảo ngược.

---

# 11. Metric #9 — Marketing Investment và OPEX intensity

Nếu P&L có:

- Advertising & Promotion
- Brand Marketing Investment
- Selling expense
- Distribution
- Overhead

hãy convert tất cả thành % Turnover:

\[
\boxed{
Marketing\ Investment\%=
\frac{Marketing}{TO}
}
\]

\[
OPEX\%=
\frac{OPEX}{TO}
\]

Và quan trọng hơn:

\[
\Delta OPEX\ bps
=
(OPEX\%_{24}-OPEX\%_{23})\times10,000
\]

Ví dụ:

```text
Gross Margin       +250 bps
Marketing          +100 bps
Overhead            -30 bps
Operating Margin   +180 bps
```

Story:

> Productivity and gross-margin expansion created 250 bps headroom; 100 bps was reinvested behind brands while overhead leverage contributed another 30 bps, resulting in approximately 180 bps operating-margin expansion.

Đây là cách nói **FBP**, thay vì đọc từng P&L line.

---

# 12. Metric #10 — Incremental Margin

Một metric khá mạnh trong case interview:

\[
\boxed{
Incremental\ Margin=
\frac{\Delta Operating\ Profit}
{\Delta Turnover}
}
\]

Ví dụ:

```text
Δ Revenue = +10
Δ OP = +4
```

\[
Incremental\ Margin=40\%
\]

Nghĩa là:

> cứ €1 incremental revenue tạo ra €0.40 incremental operating profit.

Nếu doanh thu tăng nhưng:

```text
ΔOP ≈ 0
```

→ cần điều tra discount, mix, COGS hoặc overhead.

---

# 13. Metric #11 — Cash conversion / Free Cash Flow

Nếu P&L Table chỉ có income statement thì **không cần cố nhét metric này**.

Nhưng nếu có cash-flow/balance-sheet data thì đây là next layer.

Theo định nghĩa Unilever:

\[
\boxed{
FCF =
Cash\ Flow\ from\ Operations
- Tax\ Paid
- Net\ Capex
- Net\ Interest
}
\] citeturn860837view0


Cash conversion trả lời:

> **Profit trên P&L có thực sự biến thành cash không?**

Unilever cũng dùng cash conversion để đo khả năng chuyển profit thành cash. citeturn779130view3

---

# 14. Metric #12 — ROIC

Nếu được cung cấp balance sheet:

\[
\boxed{
ROIC=
\frac{Operating\ Profit\ After\ Tax}
{Average\ Invested\ Capital}
}
\]

Unilever dùng underlying ROIC như một guardrail cho **long-term value creation và capital allocation**. citeturn860837view0

Trong case intern với 3–4 slides, tôi **không ưu tiên ROIC trừ khi data cho phép**.

---

# 15. Working Capital — chỉ dùng nếu có balance-sheet data

Ba metrics:

\[
DSO=
\frac{Average\ Receivables}{Sales}\times365
\]

\[
DIO=
\frac{Average\ Inventory}{COGS}\times365
\]

\[
DPO=
\frac{Average\ Payables}{COGS}\times365
\]

\[
\boxed{
Cash\ Conversion\ Cycle=DSO+DIO-DPO
}
\]

Đặc biệt inventory có ý nghĩa trong FMCG vì:

```text
weak demand
↓
inventory build
↓
promotion / clearance
↓
discount ↑
↓
margin ↓
↓
cash ↓
```

---

# 16. Nhưng metric quan trọng nhất không phải một ratio — mà là **bridge**

Một FBP giỏi gần như luôn muốn biến:

```text
2023 result
→ drivers
→ 2024 result
```

Ví dụ Turnover Bridge:

```text
2023 Turnover
+ Volume
+ Price
+ Product Mix
+ Channel Mix
- Discount
+/- FX
= 2024 Turnover
```

Gross Profit Bridge:

```text
2023 GP
+ Volume
+ Price
+ Premium Mix
- Discount
- Raw Material Inflation
+ Productivity
+/- FX
= 2024 GP
```

Operating Profit Bridge:

```text
2023 OP
+ Gross Profit improvement
- Additional Marketing
+ Overhead savings
- Other expenses
= 2024 OP
```

**Bridge trả lời “why”; ratio chỉ trả lời “what”.**

---

# 17. Một số pattern mà bạn nên tự động nhận ra

Đây là phần **domain judgement** mà interview/case thường thực sự kiểm tra.

### Pattern A

```text
Turnover ↑
Discount % ↑↑
Gross Margin ↓
```

Interpretation:

> Business đang có thể **buying growth through promotion**.

Action direction:

- review promotion architecture;
- customer discount;
- SKU promo elasticity;
- trade-spend efficiency.

---

### Pattern B

```text
Turnover ↑
Price ↑↑
Volume ↓
```

Interpretation:

> Growth price-led nhưng consumer demand đang yếu.

Risk:

> future market-share / volume deterioration.

---

### Pattern C

```text
Volume ↑
Turnover ↑
Gross Margin ↓
```

Có thể do:

- low-margin SKU growth;
- channel mix;
- customer mix;
- commodity inflation;
- discount;
- unfavorable pack mix.

Tức phải **drill down mix**, không được kết luận “volume growth = tốt”.

---

### Pattern D

```text
Gross Margin ↑
Operating Margin ↓
```

Câu hỏi:

> Investment hay inefficiency?

Nếu:

```text
Marketing % ↑
```

nhưng brand/volume performance sau đó tốt:

→ có thể là strategic reinvestment.

Nếu:

```text
Overhead % ↑
```

→ structural inefficiency đáng lo hơn.

---

### Pattern E

```text
Sales ↓
Gross Margin ↑
```

Có thể:

> portfolio rationalisation / premiumisation.

Không nhất thiết xấu.

Hãy kiểm tra:

```text
Gross Profit absolute
Operating Profit
Volume
Market share
```

---

# 18. Với riêng confectionery, tôi sẽ thêm 5 domain lenses

Financial data nên được đọc qua:

### ① Pack-price architecture

Không chỉ Brand A vs Brand B.

Phải nhìn:

```text
small pack
sharing pack
premium pack
economy pack
```

Mix thay đổi có thể tác động lớn đến:

- realized price;
- gross margin;
- volume;
- affordability.

---

### ② Promotion dependency

Confectionery/FMCG có thể xuất hiện:

```text
high GSV
+
high discount
=
weak net economics
```

Do đó **Discount %** phải đi cùng TO growth.

---

### ③ Channel mix

Ví dụ economics của:

```text
Traditional Trade
Modern Trade
Convenience
E-commerce
```

có thể hoàn toàn khác nhau.

Không nên chỉ hỏi:

> channel nào sales lớn nhất?

Mà:

> **channel nào tạo incremental profitable growth?**

---

### ④ Customer economics

Top customer có thể:

```text
high volume
+
high discount
+
high servicing cost
=
low profitability
```

---

### ⑤ SKU complexity

Một SKU nhỏ đôi khi:

```text
low volume
low margin
high manufacturing complexity
high inventory
```

→ rationalise SKU có thể cải thiện cả:

- margin;
- working capital;
- supply-chain productivity.

Unilever thực tế cũng gắn productivity, mix và volume leverage với gross-margin improvement. citeturn938694view3

---

# 19. Quan trọng: đừng phân tích YoY theo kiểu này

Sai:

> Sales increased 6%.  
> COGS increased 4%.  
> Gross profit increased 9%.  
> Marketing increased 12%.  
> Operating profit increased 3%.

Đây chỉ là **reporting**.

FBP-level:

> **Turnover grew 6%, but the quality of growth weakened as discount intensity increased and volume lagged revenue growth. Gross-margin expansion from product mix and cost productivity was partly reinvested in marketing, leaving operating profit up only 3%. Performance is concentrated in X brand/channel, while Y customer destroys margin through elevated trade spend.**

Đó mới là **analysis**.

---

# 20. Tôi sẽ dùng một “question funnel” như sau khi mở Excel

Nếu đây là case tôi đang làm, thứ tự kiểm tra sẽ là:

```text
1. Did Turnover grow?
              ↓
2. Was growth volume-led or price/mix-led?
              ↓
3. Did Discount % improve or deteriorate?
              ↓
4. Did Gross Profit grow faster than Turnover?
              ↓
5. Did Gross Margin expand?
              ↓
6. Why did GM move?
              ↓
7. Did OP grow?
              ↓
8. Why did OP Margin move?
              ↓
9. Which Brand/Product caused the change?
              ↓
10. Which Channel?
              ↓
11. Which Customer?
              ↓
12. Which 2–3 drivers explain ~80% of the issue?
              ↓
13. What management action changes those drivers?
```

Đặc biệt câu **12** rất quan trọng.

Không cần tìm 30 insights.

Senior leadership cần:

> **2–3 big drivers → 3 actions.**

---

# 21. Một master scorecard tôi khuyên dùng cho case này

Nếu Excel có đủ data, tôi sẽ build bảng:

| KPI | 2023 | 2024 | Δ abs | YoY / Δbps | Assessment |
|---|---:|---:|---:|---:|---|
| GSV | | | | % | |
| Discount | | | | % | |
| **Discount % TO** | | | | bps | |
| **Turnover** | | | | % | |
| Volume | | | | % | |
| Realized Price/Mix | | | | % | |
| COGS | | | | % | |
| **Gross Profit** | | | | % | |
| **Gross Margin** | | | | bps | |
| Marketing | | | | % | |
| Marketing % TO | | | | bps | |
| Overhead | | | | % | |
| **Operating Profit** | | | | % | |
| **Operating Margin** | | | | bps | |

Sau đó chỉ lấy **4–6 metrics có story** lên slide.

---

# 22. Conversion kEUR ↔ mVND trong chính case này

Brief cho tỷ giá:

> 26,723 VND/EUR. fileciteturn0file0L26-L30

Do đó:

\[
1\ kEUR
=
1,000\times26,723
=
26,723,000\ VND
\]

và:

\[
\boxed{
1\ kEUR=26.723\ mVND
}
\]

Nên:

\[
\boxed{
mVND=kEUR\times26.723
}
\]

và ngược lại:

\[
\boxed{
kEUR=\frac{mVND}{26.723}
}
\]

**YoY % và margin % đương nhiên không đổi khi convert currency**, chỉ absolute amount thay đổi.

---

# 23. Nếu phải nhớ đúng 7 KPI cho case này

Tôi sẽ chọn đúng thứ tự này:

**① Turnover Growth**  
→ Business có tăng trưởng?

**② Gross Margin**  
→ Growth có tạo economic value?

**③ Operating Profit / Margin**  
→ Bottom-line outcome ra sao?

**④ Volume Growth**  
→ Demand có khỏe?

**⑤ Discount % Turnover**  
→ Có đang mua growth bằng promotion?

**⑥ Price / Product / Channel Mix**  
→ Quality of growth là gì?

**⑦ Contribution Margin by Brand/Product/Channel/Customer**  
→ Chính xác nên **invest / fix / defend / exit ở đâu?**

Cash, working capital và ROIC là **layer tiếp theo nếu dataset support**.

Điểm tôi nghĩ đặc biệt quan trọng cho case này là **đừng bắt đầu bằng “P&L có những metric gì?” mà bắt đầu bằng “management phải quyết định gì?”**. Từ đó mới đi ngược về metric. Chính Unilever cũng trình bày performance theo logic tương tự: growth → volume/price → gross margin → reinvestment → operating profitability → return/cash, thay vì đơn thuần đọc lần lượt từng dòng accounting. citeturn938694view3turn860837view0

Một hạn chế hiện tại là file bạn upload **chỉ có brief 2 trang**; nó nhắc tới “P&L Table” nhưng chưa có chính file P&L đó. fileciteturn0file0L31-L33 Vì vậy tôi chưa thể xác định chính xác những row nào như COGS, BMI, overhead, supply-chain cost… có trong dataset.

**Nếu bạn upload tiếp P&L Table + Sales Data của case này, tôi có thể làm bước tiếp theo rất cụ thể:** map từng cột/dòng → metric nào cần tính → công thức Excel → thứ tự drill-down → và quan trọng nhất là dựng cho bạn một **“FBP Analysis Playbook” dạng checklist để bạn dùng lại cho các case tương tự.**

