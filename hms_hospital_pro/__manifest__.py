{
    'name': 'Hospital Management System',
    'version': '1.0.0',
    'category': 'Healthcare/Hospital',
    'summary': 'Professional Clinical & Hospital Management System (HMS) for Odoo 19',
    'description': """
Hospital Management System (HMS) - Professional Edition
======================================================
Transform Odoo into a complete clinical cockpit. This module is designed for 
small-to-medium hospitals and clinics, offering deep clinical workflows:

Key Highlights:
- Visit-Centric Architecture: Link Diagnosis, Prescription, Labs, and Radiology to a single Visit.
- OPD & IPD Management: Inpatient admission with Bed Management and Real-time Occupancy.
- Nursing & Triage: Dedicated Vitals entry, BMI computation, and Urgent case tracking.
- Pharmacy & Stocks: Batch (Lot) tracking with Real-time Expiry alerts.
- Diagnostic Orders: Integrated Laboratory and Radiology workflow.
- Consolidated Billing: Professional invoicing for consultations, medicines, and diagnostics.
- Advanced Analytics: Bed occupancy pivots and Patient wait-time trends.
    """,
    'author': 'Seyfadin: Odoo Developer',
    'website': 'https://linktr.ee/seyfadinA',
    'depends': ['base', 'mail', 'product', 'stock', 'account', 'product_expiry'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/hospital_rules.xml',
        'data/patient_sequence.xml',
        'data/uhid_sequence.xml',
        'data/week_day_data.xml',
        'data/lab_sequence.xml',
        'data/radiology_sequence.xml',
        'demo/hospital_demo.xml',
        'views/patient_views.xml',
        'views/doctor_views.xml',
        'views/department_views.xml',
        'views/ward_views.xml',
        'views/vitals_views.xml',
        'views/staff_views.xml',
        'views/product_views.xml',
        'views/lab_views.xml',
        'views/radiology_views.xml',
        'views/discharge_summary_views.xml',
        'views/dashboard_views.xml',
        'views/appointment_views.xml',
        'views/tag_views.xml',
        'views/visit_views.xml',
        'views/prescription_views.xml',
        'views/menu.xml', # Menu must ALWAYS be last
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'price': 0.0,
    'currency': 'USD',
    'images': ['static/description/banner.png'],
    'maintainer': 'Seyfadin',
}
