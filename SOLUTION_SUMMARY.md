# Tariff Problem Solution Summary

## Problem Statement

A consumer has a maximum demand (M.D.) of **20 kW** at **0.8 p.f. lagging** and an annual load factor of **60%**.

There are two alternative tariffs:
- **Tariff 1**: Rs. 200 per kVA of M.D. plus 3p per kWh consumed
- **Tariff 2**: Rs. 50 per kVA of M.D. plus 7p per kWh consumed

**Question**: Determine which tariff is economical.

---

## Solution

### Step 1: Convert Maximum Demand to kVA

```
Power Factor (p.f.) = cos(φ) = 0.8 lagging

Maximum Demand in kVA = Maximum Demand in kW / Power Factor
                      = 20 kW / 0.8
                      = 25 kVA
```

### Step 2: Calculate Annual Energy Consumption

```
Load Factor = Average Load / Maximum Demand
0.6 = Average Load / 20 kW
Average Load = 20 × 0.6 = 12 kW

Annual Energy Consumption = Average Load × Hours per Year
                          = 12 kW × 8760 hours
                          = 105,120 kWh
```

### Step 3: Calculate Tariff 1 Cost

**Tariff 1 Structure**: Rs. 200 per kVA + 3 paise per kWh

```
Maximum Demand Charge = Rs. 200 × 25 kVA
                      = Rs. 5,000

Energy Charge = Rs. 0.03 × 105,120 kWh
              = Rs. 3,153.60

Total Annual Cost (Tariff 1) = Rs. 5,000 + Rs. 3,153.60
                              = Rs. 8,153.60
```

### Step 4: Calculate Tariff 2 Cost

**Tariff 2 Structure**: Rs. 50 per kVA + 7 paise per kWh

```
Maximum Demand Charge = Rs. 50 × 25 kVA
                      = Rs. 1,250

Energy Charge = Rs. 0.07 × 105,120 kWh
              = Rs. 7,358.40

Total Annual Cost (Tariff 2) = Rs. 1,250 + Rs. 7,358.40
                              = Rs. 8,608.40
```

### Step 5: Compare and Determine Economical Tariff

```
Tariff 1 Total: Rs. 8,153.60
Tariff 2 Total: Rs. 8,608.40

Difference = Rs. 8,608.40 - Rs. 8,153.60
           = Rs. 454.80
```

---

## Answer

### **TARIFF 1 is MORE ECONOMICAL**

**Annual Savings**: Rs. 454.80

---

## Cost Breakdown Comparison

| Component                  | Tariff 1      | Tariff 2      |
|---------------------------|---------------|---------------|
| **MD Charge Rate**        | Rs. 200/kVA   | Rs. 50/kVA    |
| **Energy Charge Rate**    | 3p/kWh        | 7p/kWh        |
| **MD Charge**             | Rs. 5,000.00  | Rs. 1,250.00  |
| **Energy Charge**         | Rs. 3,153.60  | Rs. 7,358.40  |
| **Total Annual Cost**     | **Rs. 8,153.60** | **Rs. 8,608.40** |

---

## Analysis

### Why Tariff 1 is More Economical

Despite Tariff 1 having a **higher MD charge** (Rs. 200/kVA vs Rs. 50/kVA), it is still more economical because:

1. **Lower Energy Charge Rate**: 3p/kWh vs 7p/kWh
2. **High Energy Consumption**: 105,120 kWh annually
3. **Load Factor Effect**: At 60% load factor, energy charges dominate

The energy consumption is high enough that the **4p/kWh difference** (7p - 3p) outweighs the MD charge savings in Tariff 2.

### Breakeven Analysis

The difference in MD charges:
```
Tariff 2 MD savings = Rs. 5,000 - Rs. 1,250 = Rs. 3,750
```

The difference in energy charges:
```
Tariff 1 energy savings = Rs. 7,358.40 - Rs. 3,153.60 = Rs. 4,203.80
```

Since **energy savings (Rs. 4,203.80) > MD savings (Rs. 3,750)**, Tariff 1 wins.

### When Would Tariff 2 Be Better?

Tariff 2 would be economical when:
- Load factor is **very low** (intermittent usage)
- Annual energy consumption is **minimal**
- The consumer prioritizes **low demand charges**

### Load Factor Threshold

We can find the breakeven load factor:

```
Let x = load factor

Tariff 1 Cost: 5000 + 0.03 × (20 × x × 8760)
Tariff 2 Cost: 1250 + 0.07 × (20 × x × 8760)

Setting them equal:
5000 + 5256x = 1250 + 12264x
3750 = 7008x
x = 0.535 (53.5%)

At 60% load factor > 53.5%, Tariff 1 is better
At load factor < 53.5%, Tariff 2 would be better
```

---

## Key Formulas Used

1. **kVA Calculation**:
   ```
   kVA = kW / Power Factor
   ```

2. **Load Factor**:
   ```
   Load Factor = Average Load / Maximum Demand
   ```

3. **Annual Energy**:
   ```
   Annual Energy (kWh) = Average Load (kW) × 8760 hours
   ```

4. **Tariff Cost**:
   ```
   Total Cost = (Rate per kVA × MD in kVA) + (Rate per kWh × Annual Energy)
   ```

---

## Python Implementation

Three versions are provided:

### 1. GUI Application (`electrical_engineering_simulator.py`)
- Full-featured Tkinter interface
- Interactive sliders
- Real-time calculations
- Visualization

### 2. Standalone Calculator (`tariff_calculator_standalone.py`)
- Command-line interface
- No GUI dependencies
- Quick solution display
- Detailed calculation steps

### 3. Test Suite (`test_tariff_solution.py`)
- Automated verification
- Assertion checks
- Validation of results

---

## Verification

Run the standalone calculator to verify:

```bash
python3 tariff_calculator_standalone.py
```

Expected output:
```
TARIFF 1: Rs. 8,153.60
TARIFF 2: Rs. 8,608.40
CONCLUSION: Tariff 1 is MORE ECONOMICAL!
Annual Savings: Rs. 454.80
```

---

## Conclusion

For a consumer with:
- **20 kW** maximum demand
- **0.8** power factor (lagging)
- **60%** load factor

**TARIFF 1** (Rs. 200/kVA + 3p/kWh) is the **economical choice**, providing annual savings of **Rs. 454.80** compared to Tariff 2.

This is because the high load factor (60%) results in substantial energy consumption (105,120 kWh/year), making the lower energy rate (3p vs 7p) more valuable than the lower demand charge.

---

## Additional Features in the Application

Beyond solving the tariff problem, the application includes:

### Synchronous Machine Simulator
- Dynamic modeling using swing equations
- Real-time ODE solving
- Visualization of transient stability

### RLC Circuit Analyzer
- Transient analysis of electrical circuits
- Multiple solver options
- Interactive parameter tuning

### Educational Value
- Comparison of numerical methods (Euler vs RK45)
- Practical electrical engineering applications
- Interactive learning environment

---

*Solution verified and implemented in Python with comprehensive GUI and CLI interfaces.*
