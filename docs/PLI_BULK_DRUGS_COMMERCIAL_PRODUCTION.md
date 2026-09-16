# PLI Bulk Drugs — commercial-production sourcing — layer 46

*Generated 2026-09-16 by `scripts/build_layer46_pli_bulk_drugs.py`. Static, hand-verified dataset built from 4 government primary sources (see below) — not a live scrape.*

## The three-source problem this layer solves

No single official document has the full picture: the BDMAI circular has company-level capacity but is from 2022 and image-only; the 2025 PIB release has the applicant/product annexure but no capacity; the 2026 PIB release has the current state-wise numbers and — critically — is the ONLY source that names all 18 APIs now in commercial production (every other source just gives the count). This layer merges all three.

## Sources

- **BDMAI circular (Dept. of Pharmaceuticals letter No.30013/16/2022-Scheme)** (2022-10-18) — company-level committed capacity (MT) per approved project — 51 line items; image-only PDF, transcribed visually. [https://bdmai.org/wp-content/uploads/2025/02/LIST-OF-APPROVED-BULK-DRUG-MANUFACTURERS-ALONG-WITH-MANUFACTUREING-CAPACITY-UNDER-THE-PLI-SCHEME.pdf](https://bdmai.org/wp-content/uploads/2025/02/LIST-OF-APPROVED-BULK-DRUG-MANUFACTURERS-ALONG-WITH-MANUFACTUREING-CAPACITY-UNDER-THE-PLI-SCHEME.pdf)
- **PIB Release ID 2146914 (Rajya Sabha written reply, Anupriya Patel)** (2025-07-22) — applicant/product annexure confirming 48 approved projects. [https://www.pib.gov.in/PressReleasePage.aspx?PRID=2146914](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2146914)
- **PIB Release ID 2295928 (Lok Sabha written reply, Anupriya Patel)** (2026-08-07) — MOST CURRENT — state-wise investment/capacity/production (Annexure-A), full 41-product approved list (Annexure-B), and the exact 18 APIs now in commercial production. [https://www.pib.gov.in/PressReleasePage.aspx?PRID=2295928](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2295928)
- **BusinessToday, "Atma Nirbhar Bharat: Here are 53 drugs on which India will test self reliance"** (2020-06-03) — the original 53 critical China-import-dependent APIs identified pre-scheme. [https://www.businesstoday.in/industry/pharma/story/atma-nirbhar-bharat-here-are-53-drugs-on-which-india-will-test-self-reliance-260146-2020-06-03](https://www.businesstoday.in/industry/pharma/story/atma-nirbhar-bharat-here-are-53-drugs-on-which-india-will-test-self-reliance-260146-2020-06-03)

## Key finding: the Paracetamol/Metformin gap

**22 of the 53 originally-identified critical APIs have NO PLI project approved at all**, including **Paracetamol** and **Metformin** — two of the highest-volume generic APIs in India's own Jan Aushadhi (PMBJP) formulary. These remain exposed to import dependence with zero government-incentivised domestic capacity underway despite being flagged as critical in 2020.

| Gap APIs (no PLI project) |
|---|
| Amoxicillin |
| Azithromycin |
| Erythromycin Stearate |
| Ceftriaxone |
| Cefoperazone |
| Cefixime |
| Cephalexin |
| Piperacillin |
| Tazobactam |
| Sulbactam |
| Metformin |
| Gabapentin |
| Clindamycin Phosphate |
| Clindamycin HCL |
| Doxycycline |
| Potassium Clavulanate |
| Oxytetracycline |
| Clarithromycin |
| Metronidazole |
| Paracetamol |
| Tinidazole |
| Ornidazole |

## The 18 APIs in commercial production (named for the first time here)

| API |
|---|
| Prednisolone |
| Telmisartan |
| Artesunate |
| Norfloxacin |
| Ofloxacin |
| Sulfadiazine |
| Levofloxacin |
| Diclofenac Sodium |
| Carbamazepine |
| Oxcarbazepine |
| Atorvastatin |
| Lopinavir |

## Company-level approved projects (n=51, total committed capacity 92,130 MT)

| S.No. | Company | Product | Committed Capacity (MT) | Commercial? |
|---|---|---|---|---|
| 1 | Aurobindo Pharma Limited (through Lyfius Pharma Pvt. Ltd.) | Penicillin G | 15,000 | ✅ |
| 2 | Karnataka Antibiotics and Pharmaceuticals Limited | 7-ACA | 1,000 |  |
| 3 | Orchid Bio-Pharma Limited | 7-ACA | 1,000 |  |
| 4 | Kinvan Private Limited | Clavulanic Acid | 300 | ✅ |
| 5 | Natural Biogenex Private Limited | Betamethasone | 12 |  |
| 6 | Natural Biogenex Private Limited | Dexamethasone | 10 | ✅ |
| 7 | Natural Biogenex Private Limited | Prednisolone | 15 | ✅ |
| 8 | Symbiotec Pharmalab Private Limited | Prednisolone | 15 | ✅ |
| 9 | Macleods Pharmaceutical Limited | Rifampicin | 200 |  |
| 10 | Karnataka Antibiotics and Pharmaceuticals Limited | Clindamycin Base | 60 |  |
| 11 | Emmennar Pharma Pvt. Ltd. | 1,1 Cyclohexane Diacetic Acid (CDA) | 1,500 | ✅ |
| 12 | Hindys Lab Pvt. Ltd. | 1,1 Cyclohexane Diacetic Acid (CDA) | 3,000 | ✅ |
| 13 | Alkimia Pharma-Chem Pvt Ltd | 1,1 Cyclohexane Diacetic Acid (CDA) | 1,500 | ✅ |
| 14 | Meghmani LLP | Para Amino Phenol | 13,500 | ✅ |
| 15 | Sadhana Nitro Chem Ltd. | Para Amino Phenol | 36,000 | ✅ |
| 16 | Granules India Limited | Dicyandiamide (DCDA) | 8,000 | ✅ |
| 17 | Rajasthan Antibiotics Limited | Meropenem | 48 |  |
| 18 | Centrient Pharmaceuticals India Private Limited | Atorvastatin | 180 | ✅ |
| 19 | Anasia Lab Private Limited | Olmesartan | 75 |  |
| 20 | Andhra Organics Limited | Olmesartan | 75 |  |
| 21 | Aviran Pharmachem Private Limited | Artesunate | 20 | ✅ |
| 22 | K P Manish Global Ingredients Pvt. Ltd. | Artesunate | 80 | ✅ |
| 23 | RMC Performance Chemicals Private Limited | Aspirin | 1,500 |  |
| 24 | Alta Laboratories Limited | Aspirin | 2,250 |  |
| 25 | Lifetech Sciences | Ritonavir | 20 |  |
| 26 | Honour Lab Limited | Lopinavir | 49 | ✅ |
| 27 | Hindys Lab Pvt. Ltd. | Acyclovir | 525 |  |
| 28 | Dasami Lab Pvt. Ltd. | Carbamazepine | 260 | ✅ |
| 29 | Dasami Lab Pvt. Ltd. | Oxcarbazepine | 195 | ✅ |
| 30 | Hetero Drugs Limited | Oxcarbazepine | 195 | ✅ |
| 31 | Hazelo Lab Pvt. Ltd. | Vitamin B6 | 70 |  |
| 32 | Sudarshan Pharma Industries Ltd. | Vitamin B6 | 35 |  |
| 33 | Honour Lab Limited | Vitamin B6 | 140 |  |
| 34 | Honour Lab Limited | Valsartan | 300 |  |
| 35 | Anasia Lab Private Limited | Losartan | 400 |  |
| 36 | Hetero Drugs Limited | Levofloxacin | 230 | ✅ |
| 37 | MSN Life Sciences Pvt. Ltd | Levofloxacin | 230 | ✅ |
| 38 | Vital Laboratories Private Limited | Levofloxacin | 115 | ✅ |
| 39 | Andhra Organics Limited | Sulfadiazine | 360 | ✅ |
| 40 | Sreepathi Pharmaceuticals Limited | Ciprofloxacin | 900 |  |
| 41 | Vital Laboratories Private Limited | Ofloxacin | 100 | ✅ |
| 42 | Global Pharma Healthcare Private Limited | Ofloxacin | 200 | ✅ |
| 43 | Globela Industries Pvt. Ltd | Ofloxacin | 100 | ✅ |
| 44 | Globela Industries Pvt. Ltd | Norfloxacin | 60 | ✅ |
| 45 | Andhra Organics Limited | Telmisartan | 360 | ✅ |
| 46 | Kreative Actives Private Limited | Diclofenac Sodium | 350 | ✅ |
| 47 | Amoli Organics Private Limited | Diclofenac Sodium | 175 | ✅ |
| 48 | Vapi Care Pharma Private Limited | Diclofenac Sodium | 525 | ✅ |
| 49 | Honour Lab Limited | Levetiracetam | 840 |  |
| 50 | Hetero Drugs Limited | Carbidopa | 16 |  |
| 51 | Hetero Drugs Limited | Levodopa | 40 |  |

## State-wise (as of March 2026)

| State | Projects | Committed Inv. (₹cr) | Actual Inv. (₹cr) | Committed Cap. (MT) | Installed Cap. (MT) |
|---|---|---|---|---|---|
| Andhra Pradesh | 10 | 1,745.7 | 2,676 | 24,390 | 16,468 |
| Gujarat | 8 | 330.9 | 407.3 | 14,270 | 13,959 |
| Haryana | 1 | 81 | 37 | 800 | 0 |
| Himachal Pradesh | 2 | 806.8 | 502.6 | 1,100 | 400 |
| Jammu & Kashmir | 1 | 185 | 338.65 | 1,000 | 0 |
| Karnataka | 3 | 96.9 | 201.4 | 37 | 16.7 |
| Madhya Pradesh | 2 | 280 | 101.8 | 1,015 | 15 |
| Maharashtra | 5 | 308.4 | 168.8 | 40,185 | 19,180 |
| Punjab | 1 | 137.7 | 161.1 | 180 | 206 |
| Tamil Nadu | 2 | 31.5 | 45.6 | 280 | 280 |
| Telangana | 13 | 326.02 | 430.2 | 7,820 | 7,820 |

BDMAI's Oct-2022 roster has 51 company-project line items; PIB's 2025/2026 releases say 48 projects approved -- the gap is not reconciled here (could be projects merged, withdrawn, or added between the two dates); treat 51 as the fuller, slightly older company-level list and 48 as the current official count.

