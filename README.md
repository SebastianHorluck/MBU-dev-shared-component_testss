# MBU Dev Shared Components

[![PyPI version](https://badge.fury.io/py/mbu-dev-shared-components.svg)](https://badge.fury.io/py/mbu-dev-shared-components)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

MBU Dev Shared Components is a Python library that provides helper modules to streamline Robotic Process Automation (RPA) development.

## Features

- **Office365 Integration**:
  - SharePoint
  - Excel
- **SAP Integration**
- **Solteq Tand Integration**
- **Utility Modules**:
  - JSON handling
  - Fernet encryption

## Installation

Install the package using pip:

```bash
pip install mbu-dev-shared-components


# Dynamic SQL Query Builder

This repository provides a **generic function** to dynamically build SQL `WHERE` clauses using filters. It supports:

- **Equality (`=`)**  
- **LIKE (`%search%`)**  
- **IN (`column IN (value1, value2, ...)`)**  
- **BETWEEN (`column BETWEEN value1 AND value2`)**  
- **AND & OR Conditions**  
- **ORDER BY (`ORDER BY column ASC/DESC`)**  

---

## 📌 How to Use the `check_if_event_exists` Function

| **Usage Type** | **Example Function Call** | **Generated SQL WHERE Clause** |
|--------------|--------------------------------------|--------------------------------------------|
| **1. Basic Equality Filtering** | ```python self.check_if_event_exists(filters={"p.cpr": "123456-7890", "e.event_name": "Some Clinic"}) ``` | `WHERE 1=1 AND p.cpr = ? AND e.event_name = ?` |
| **2. LIKE Filtering** (Partial Match) | ```python self.check_if_event_exists(filters={"e.event_name": "%Clinic%"}) ``` | `WHERE 1=1 AND e.event_name LIKE ?` |
| **3. IN Filtering** (Multiple Values) | ```python self.check_if_event_exists(filters={"e.event_message": ["Scheduled", "Pending"]}) ``` | `WHERE 1=1 AND e.event_message IN (?, ?)` |
| **4. BETWEEN Filtering** (Range) | ```python self.check_if_event_exists(filters={"e.eventTriggerDate": ("2024-01-01", "2024-12-31")}) ``` | `WHERE 1=1 AND e.eventTriggerDate BETWEEN ? AND ?` |
| **5. Multiple AND Conditions** | ```python self.check_if_event_exists(filters={"p.cpr": "123456-7890", "e.event_message": "Scheduled", "e.archived": 0}) ``` | `WHERE 1=1 AND p.cpr = ? AND e.event_message = ? AND e.archived = ?` |
| **6. OR Conditions (Single Group)** | ```python self.check_if_event_exists(or_filters=[{"e.event_name": "Clinic A"}, {"e.event_name": "Clinic B"}]) ``` | `WHERE 1=1 AND (e.event_name = ? OR e.event_name = ?)` |
| **7. OR with Multiple Conditions** | ```python self.check_if_event_exists(or_filters=[{"e.event_name": "Clinic A", "e.event_message": "Scheduled"}, {"e.event_name": "Clinic B"}]) ``` | `WHERE 1=1 AND ((e.event_name = ? AND e.event_message = ?) OR (e.event_name = ?))` |
| **8. AND & OR Combined** | ```python self.check_if_event_exists(filters={"e.archived": 0}, or_filters=[{"e.event_name": "Clinic A"}, {"e.event_name": "Clinic B"}]) ``` | `WHERE 1=1 AND e.archived = ? AND (e.event_name = ? OR e.event_name = ?)` |
| **9. LIKE with OR** | ```python self.check_if_event_exists(or_filters=[{"e.event_message": "%Scheduled%"}, {"e.event_message": "%Pending%"}]) ``` | `WHERE 1=1 AND (e.event_message LIKE ? OR e.event_message LIKE ?)` |
| **10. Complex AND, OR, LIKE, IN Combined** | ```python self.check_if_event_exists(filters={"p.cpr": "123456-7890", "e.event_message": ["Scheduled", "Pending"]}, or_filters=[{"e.event_name": "%Hospital%"}, {"e.event_name": "%Clinic%"}]) ``` | `WHERE 1=1 AND p.cpr = ? AND e.event_message IN (?, ?) AND (e.event_name LIKE ? OR e.event_name LIKE ?)` |
| **11. ORDER BY (Ascending)** | ```python self.check_if_event_exists(filters={"p.cpr": "123456-7890"}, order_by="e.timestamp", order_direction="ASC") ``` | `WHERE 1=1 AND p.cpr = ? ORDER BY e.timestamp ASC` |
| **12. ORDER BY (Descending)** | ```python self.check_if_event_exists(filters={"p.cpr": "123456-7890"}, order_by="e.timestamp", order_direction="DESC") ``` | `WHERE 1=1 AND p.cpr = ? ORDER BY e.timestamp DESC` |
| **13. ORDER BY with Multiple Filters** | ```python self.check_if_event_exists(filters={"e.event_message": "Scheduled"}, order_by="e.eventTriggerDate", order_direction="DESC") ``` | `WHERE 1=1 AND e.event_message = ? ORDER BY e.eventTriggerDate DESC` |
=======
```
