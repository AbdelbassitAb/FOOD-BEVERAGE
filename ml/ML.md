# 🤖 Machine Learning - Customer Segmentation

## 📚 Section 3.3 & 3.4 - Customer Segmentation with K-Means

This notebook implements a **customer segmentation** model based on RFM analysis (Recency, Frequency, Monetary) and K-Means clustering to identify homogeneous customer groups and personalize marketing strategies.

---

## 📓 Notebook: `customer_segmentation.ipynb`

### 🎯 Business Objective

Identify distinct customer segments to:

- Optimize marketing budget allocation
- Personalize offers by segment
- Improve retention and lifetime value (LTV)
- Reduce churn among at-risk customers

---

## 🔬 Methodology (Section 3.3)

### 1. **RFM Analysis**

Compute 3 key metrics for each customer:

- **Recency**: Number of days since the last purchase
- **Frequency**: Total number of transactions
- **Monetary**: Total amount spent (€)

**Additional metrics:**

- Average amount per transaction
- Customer lifetime (days since first purchase)
- Number of product categories purchased

### 2. **K-Means Clustering**

**Technique:** Unsupervised clustering with optimized number of clusters

**Process:**

1. Feature standardization (StandardScaler)
2. Elbow Method for optimal K
3. Silhouette Score for separation validation
4. Apply the final clustering with optimal K
5. PCA for 2D visualization

**Optimal K selected:** 6 clusters (based on Elbow + Silhouette)

---

## 📊 Results (Section 3.4 - Evaluation)

### Performance Metrics

| Metric                   | Value | Interpretation                      |
| ------------------------ | ----- | ----------------------------------- |
| **Silhouette Score**     | 0.50+ | Good cluster separation             |
| **Davies-Bouldin Index** | <1.0  | Compact and distinct clusters       |
| **Number of clusters**   | 6     | Optimal segmentation                |
| **Customers analyzed**   | 766   | Entities with transactional history |

### Identified Segments

The 6 customer segments discovered:

#### 🌟 **Segment 0 - VIP Champions**

- **Characteristics:** low Recency, high Frequency, very high Monetary
- **Profile:** Best customers, frequent purchases and high values
- **Marketing budget:** Premium (15€/customer)

#### 💎 **Segment 1 - Loyal Customers**

- **Characteristics:** low Recency, mid-high Frequency, average Monetary
- **Profile:** Loyal customers with regular engagement
- **Marketing budget:** Mid-high (10€/customer)

#### ⚠️ **Segment 2 - At Risk / Dormant**

- **Characteristics:** high Recency, low-mid Frequency, variable Monetary
- **Profile:** Inactive customers needing reactivation
- **Marketing budget:** Medium (8€/customer)

#### 🆕 **Segment 3 - New Customers**

- **Characteristics:** low Recency, low Frequency, low Monetary
- **Profile:** New customers to nurture
- **Marketing budget:** Medium (7€/customer)

#### 🚀 **Segment 4 - Potential Loyalists**

- **Characteristics:** average Recency, average Frequency, average Monetary
- **Profile:** Promising customers with growth potential
- **Marketing budget:** Medium (8€/customer)

#### 💤 **Segment 5 - Lost Customers**

- **Characteristics:** very high Recency, very low Frequency, low Monetary
- **Profile:** Lost customers or one-time buyers
- **Marketing budget:** Minimal (3€/customer)

---

## 💼 Concrete Marketing Recommendations (Section 3.4)

### 🌟 VIP Champions

**Actions:**

- Premium loyalty program with bonus points
- Early access to new products
- Exclusive premium offers
- Personalized VIP customer service
- Private events and exclusive perks

**Expected ROI:** Retention +25%, LTV +40%

---

### 💎 Loyal Customers

**Actions:**

- Referral program with rewards
- Personalized cross-sell offers
- Volume purchase discounts
- Newsletter with exclusive content
- Gamification to increase engagement

**Expected ROI:** Conversion +20%, Retention +15%

---

### ⚠️ At Risk / Dormant

**Actions:**

- Reactivation campaign with strong offer (20-30% off)
- 'We miss you' email with strong incentive
- Satisfaction survey to understand inactivity
- Intensive digital retargeting
- Personalized offer based on history

**Expected ROI:** Reactivation 10-15%, Churn -10%

---

### 🆕 New Customers

**Actions:**

- Automated onboarding sequence
- Product guides and tutorials
- First order free (shipping)
- Discovery program with samples
- Proactive support during the first 30 days

**Expected ROI:** Second purchase conversion +30%

---

### 🚀 Potential Loyalists

**Actions:**

- Targeted upselling toward premium products
- Personalized bundle offers
- Points program for loyalty
- Educational content on product benefits
- Incentives to increase purchase frequency

**Expected ROI:** LTV +25%, Frequency +20%

---

### 💤 Lost Customers

**Actions:**

- Win-back campaign with exceptional offer (40% off)
- Detailed exit survey
- Minimal communication (avoid spam)
- Focus on long-term rather than immediate ROI
- Analysis to prevent future churn

**Expected ROI:** Win-back 3-5% only

---

## 📈 Estimated Business Impact

### Global KPIs

| Metric                              | Estimated improvement |
| ----------------------------------- | --------------------- |
| **Retention rate**                  | +15-25%               |
| **Lifetime Value (LTV)**            | +30%                  |
| **Conversion rate**                 | +20%                  |
| **Churn reduction**                 | -10-15%               |
| **Marketing ROI**                   | +40%                  |
| **Customer acquisition cost (CAC)** | -25%                  |

### Recommended Budget Allocation

```
🌟 VIP Champions:       40% of the budget (highest ROI)
💎 Loyal Customers:     25% of the budget (retention)
⚠️ At Risk:            15% of the budget (churn prevention)
🆕 New Customers:       12% of the budget (acquisition)
🚀 Potential Loyalists: 6% of the budget (growth)
💤 Lost Customers:      2% of the budget (win-back)
```

---

## 🛠️ Technologies Used

- **Python 3.13**
- **scikit-learn** - K-Means, PCA, StandardScaler
- **pandas** - Data manipulation
- **matplotlib/seaborn** - Visualizations
- **Snowflake** - Cloud data warehouse (ANALYTICS.FINANCIAL_TRANSACTIONS_CLEAN)

---

## 🚀 Quick Start

### Prerequisites

```bash
pip install pandas numpy scikit-learn matplotlib seaborn snowflake-connector-python
```

### Configuration Snowflake

Create `../streamlit/.streamlit/secrets.toml`:

```toml
[snowflake]
account = "YOUR_ACCOUNT"
user = "YOUR_USER"
password = "YOUR_PASSWORD"
warehouse = "YOUR_WAREHOUSE"
database = "ANYCOMPANY_LAB"
schema = "ANALYTICS"
```

### Execution

1. Open `customer_segmentation.ipynb` in VS Code
2. Select Python 3.x kernel
3. Run all cells (Ctrl+Shift+P → "Run All")

---

## 📊 Included Visualizations

### 1. Elbow Method

- Inertia vs K chart to identify optimal K
- Silhouette Score by K for validation

### 2. Segmentation PCA 2D

- Visualization of clusters in reduced 2D space
- Clear separation of the 6 segments

### 3. RFM Space 3D Projection

- Frequency vs Monetary avec taille de bulle = Recency
- Vue d'ensemble de la distribution des clients

### 4. Profils de Segments

- Average statistics per segment (Recency, Frequency, Monetary)
- Customer distribution by segment

---

## ✅ Alignment with the School Project

### Section 3.3 - Develop ML Models ✅

- ✅ Technique used: K-Means Clustering (unsupervised)
- ✅ Feature engineering: RFM + behavioral metrics
- ✅ Hyperparameter optimization: Elbow Method for optimal K
- ✅ Complete pipeline: Data loading → preprocessing → training → evaluation

### Section 3.4 - Evaluation & Recommendations ✅

- ✅ **Performance metrics:** Silhouette Score, Davies-Bouldin Index, Inertia
- ✅ **Feature interpretation:** RFM profiles per segment with automatic labeling
- ✅ **Concrete marketing recommendations:** Segment-level actions with budget and ROI
- ✅ **Estimated business impact:** Quantified KPIs (+15-40% by metric)

---

## 📝 Notebook Structure

```
customer_segmentation.ipynb
│
├── 1. Introduction & Objectifs
├── 2. Import Libraries
├── 3. Load Data from Snowflake (766 customers)
├── 4. RFM Feature Engineering
├── 5. K-Means Clustering & Optimization
│   ├── Elbow Method
│   ├── Silhouette Analysis
│   └── PCA Transformation
├── 6. Visualizations
│   ├── PCA 2D Scatter
│   └── RFM Space Plot
├── 7. Section 3.4 - Evaluation
│   ├── Performance Metrics
│   ├── Segment Profiling
│   └── Automatic Labeling
└── 8. Section 3.4 - Marketing Recommendations
    ├── Actions by segment
    ├── Budget allocation
    └── Estimated business impact
```

---

## 🎓 Key Presentation Points

1. **Robust methodology:** RFM + K-Means is a proven technique in the industry
2. **Rigorous validation:** Silhouette Score and Davies-Bouldin confirm cluster quality
3. **Business value:** Concrete recommendations with quantified impact
4. **Scalability:** The model can be retrained periodically with new data
5. **Possible integration:** Automatic scoring via Snowflake Stored Procedure

---

## 📧 Questions?

For any implementation questions:

- Review the explanatory markdown cells in the notebook
- Check Section 7 metrics (Section 3.4 - Evaluation)
- Read Section 8 recommendations for real use cases

**Happy Machine Learning! 🚀🤖**
