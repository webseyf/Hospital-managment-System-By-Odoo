# Hospital Management System Module Walkthrough

This document explains the architecture and design decisions for the hardened **HMS v2.0** on Odoo 19.

> [!TIP]
> **Quick Start for HMS v2.0**
> 1. **Schedule**: Create an Appointment (Hospital > Appointments).
> 2. **Confirm**: Confirm the appointment to unlock clinical features.
> 3. **Consult**: Click the **Stethoscope Icon** (Smart Button) to record symptoms/diagnosis.
> 4. **Prescribe**: Add medicines directly on the Consultation (Visit) form.
> 5. **Harden**: Try to book overlapping times for the same doctor to see the scheduling engine in action.

## 1. Directory Structure & File Purposes

## 1. Directory Structure & File Purposes

A well-structured Odoo module separates concerns cleanly. Our module uses the following structure:

*   **`__manifest__.py`**: The heart of the module. It defines metadata (name, version, author), dependencies (like `base`, `mail`), and the strict load order of XML data files.
*   **`__init__.py`**: Tells Python that this directory is a package, and imports the `models` directory.
*   **`models/`**: Contains Python files defining the database structure and business logic.
    *   `patient.py`, `doctor.py`, `appointment.py`, `prescription.py`: Each file defines a specific entity (`models.Model`).
*   **`security/`**: Defines access control.
    *   `security.xml`: Creates the Module Category, the Odoo 19 Privilege layer, and the User/Manager groups.
    *   `ir.model.access.csv`: Grants specific CRUD (Create, Read, Update, Delete) permissions to those groups for each model.
*   **`views/`**: Defines the User Interface (UI).
    *   `menu.xml`: Defines the top-level menus and sub-menus.
    *   `*_views.xml`: Defines the forms, lists (trees), and search views for each model.
*   **`data/`**: Contains predefined data loaded upon installation.
    *   `sequence.xml`: Defines the auto-incrementing rule for Appointment references.

## 2. Manifest Load Order (CRITICAL)

The order of files in the `'data'` list of `__manifest__.py` is essential. Odoo loads them sequentially from top to bottom.

```python
'data': [
    'security/security.xml',        # 1. Create Groups & Privileges FIRST
    'security/ir.model.access.csv', # 2. Grant access to those groups
    'data/sequence.xml',            # 3. Load core data rules
    'views/menu.xml',               # 4. Create UI Menus
    'views/patient_views.xml',      # 5. Create UI Views (can attach to menus)
    # ...
]
```
If `ir.model.access.csv` loaded before `security.xml`, it would fail because the groups it references wouldn't exist yet.

## 3. Strict XML Structure (The "Extra Content" Fix)

Previous versions of this module failed with `AssertionError: Element odoo has extra content: record/data`. This happened because the XML did not strictly adhere to Odoo 19's defined schema (`import_xml.rng`).

**The Fix:**
In Odoo 19, direct children of `<odoo>` are strictly validated. While `<data>` wrappers work in some contexts, they are often unnecessary and can cause conflicts if misused.

The most critical fix was inside specific records like `ir.sequence`. Older tutorials often suggest this deprecated syntax:
```xml
<!-- WRONG SYNTAX (Causes AssertionError) -->
<record id="seq_hospital" model="ir.sequence">
    <name>Hospital Sequence</name>
    <code>hospital.sequence</code>
</record>
```

**Odoo 19 requires explicit `<field>` tags for everything inside a `<record>`:**
```xml
<!-- CORRECT SYNTAX (Valid Odoo 19 Schema) -->
<record id="seq_hospital" model="ir.sequence">
    <field name="name">Hospital Sequence</field> <!-- Explicit field definition -->
    <field name="code">hospital.sequence</field>
</record>
```
All XML files in this rebuild strictly use this `<field name="...">` pattern, ensuring complete compatibility without relying on `<data>` wrappers to bypass validation.

## 4. Odoo 19 Security: The Privilege Layer

Odoo 19 introduced a new access hierarchy: `Category < Privilege < Group`.

Older modules linked `res.groups` directly to `ir.module.category` via `category_id`. This now causes a `ValueError` because `category_id` was removed from `res.groups`.

**The completely new security structure implemented here:**
1.  **Category:** `<record id="module_category_hospital" model="ir.module.category">`
2.  **Privilege (NEW):** `<record id="privilege_hospital" model="res.groups.privilege">`. This maps to the Category.
3.  **Group:** `<record id="group_hospital_user" model="res.groups">`. This maps to the Privilege via `privilege_id`.

## 5. Model Relationships

*   **Many2one (`doctor_id` on Patient, `patient_id` on Appointment):** A standard relational link. Many Patients can have One primary Doctor.
*   **One2many (`patient_ids` on Doctor, `appointment_ids` on Patient):** The inverse of `Many2one`. A Doctor sees a list of all their assigned patients.

## 8. Premium UI Features (Advanced Views)

We have extended the module with advanced Odoo 19 UI features:

### Smart Buttons
On the **Patient** form, you will now see a clickable "Appointments" button in the top-right corner.
*   **Purpose:** Shows the live count of appointments for that patient.
*   **Interactivity:** Clicking it opens a filtered list of only that patient's appointments.
*   **Technical:** Uses a `compute` field in Python and a `div.oe_button_box` in XML.

### Dynamic Status Bar
The **Appointment** form now has a professional workflow at the top:
*   **States:** Draft -> Confirmed -> Done.
*   **Buttons:** Action buttons like "Confirm" and "Mark as Done" only appear when they are relevant (e.g., you can't click "Confirm" if it's already "Done").
*   **Badges:** In the list view, the status is now a colorful badge (Blue for Draft, Green for Done, Red for Cancelled).

### Modern Widgets
*   **Many2one Avatar:** On the Patient form, the "Assigned Doctor" field now shows a small profile avatar next to the name.
*   **StatInfo:** Used in the smart buttons for a clean, numeric display.

## 10. Advanced Search & Archiving

We added powerful filtering capabilities to help manage a growing list of patients:

### Archiving (Soft Delete)
We added the `active` field to the Patient model.
*   **Purpose:** Allows you to "Archive" a patient instead of deleting them. Archived patients are hidden by default but their medical records are preserved.
*   **Search Filter:** A new "Archived" filter allows you to see these hidden records.

### Domain Filtering (The "Minors" Filter)
We added a custom filter using **Domain Logic**.
*   **Definition:** `domain="[('age', '<', 18)]"`
*   **Purpose:** With one click, you can now see all patients who are under 18 years old.

## 11. Relational Fields Deeper Dive (Many2many)

We implemented a **Medical Tags** system to demonstrate the third type of relational field.

### Many2many Relationship
*   **Definition:** `tag_ids = fields.Many2many('hospital.tag', string='Tags')`
*   **Real-world logic:** One patient can have many tags (e.g., "VIP", "Chronic"), and one tag can be applied to many patients.
*   **Database Secret:** Unlike Many2one (which adds a column to the table), a Many2many creates a **hidden auxiliary table** in the background (e.g., `hospital_patient_tag_rel`). This bridge table stores pairs of IDs: `(patient_id, tag_id)`.

### UI Widget: `many2many_tags`
We used the specialty Odoo widget:
```xml
<field name="tag_ids" widget="many2many_tags" options="{'color_field': 'color'}"/>
```
This renders the tags as beautiful, colorful badges rather than a plain technical list. Users can click the "x" to remove a tag or search to add existing ones.
