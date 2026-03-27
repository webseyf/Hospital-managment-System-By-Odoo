# Hospital Management System (Enterprise HMS v6.0)

[![Odoo Version](https://img.shields.io/badge/Odoo-19.0-blue.svg)](https://www.odoo.com/)
[![License](https://img.shields.io/badge/License-LGPL_v3-green.svg)](https://www.gnu.org/licenses/lgpl-3.0)

A comprehensive, production-grade Hospital Management System (HMS) built natively for **Odoo 19**. This module transforms Odoo into a clinical cockpit for small-to-medium hospitals.

## 🚀 Key Features (v6.0 Professional Edition)

### 🏥 Clinical Operations
- **Visit-Centric EMR**: Centralized clinical encounters linking Diagnosis, Prescriptions, Labs, and Radiology.
- **OPD/IPD Management**: Advanced admission workflows with real-time Bed Residency and Occupancy tracking.
- **Nursing Triage**: Dedicated Vitals monitoring, BMI computation, and Urgency case highlighting.
- **Discharge Summaries**: Mandatory clinical exit protocols for Inpatient (IPD) safety.

### 💊 Pharmacy & Diagnostics
- **Smart Prescriptions**: Quantitative tracking with **Real-time Batch/Lot Expiry Alerts**.
- **Integrated Diagnostics**: Bi-directional linkage for Laboratory and Radiology orders.

### 🧾 Enterprise Billing
- **Consolidated Invoicing**: One-click professional billing covering Consultation fees, Medicines, and Diagnostic tests.
- **Billing Idempotency**: Automated guards to prevent duplicate charges or clinical orphans.

### 🛡️ Security & Privacy
- **Granular Roles**: Pre-defined roles for **Doctors, Nurses, Pharmacists, and Receptionists**.
- **Data Isolation**: Strict clinical privacy rules ("Own Patients Only" for Doctors) while maintaining operational visibility for the front desk.

## 📊 Analytics Dashboards
- **Bed Occupancy Rates** (Pivot/Graph)
- **Hospital Revenue Trends** (By Doctor/Specialty)
- **Patient Wait-Time Analytics** (Throughput monitoring)

## 🛠️ Installation

1. Copy the `om_hospital` folder to your Odoo `addons` path.
2. Ensure dependencies are installed: `base`, `mail`, `product`, `stock`, `account`, `product_expiry`.
3. Restart Odoo and update the App List.
4. Install **Hospital Management System**.

## 📄 License
Licensed under [LGPL-3](LICENSE).

---
*Developed by: Seyfadin & Antigravity AI*
