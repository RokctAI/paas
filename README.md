# PaaS – Platform‑as‑a‑Service

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)  
[![Frappe Framework](https://img.shields.io/badge/Frappe‑v15-orange)](https://frappeframework.com)  
[![Latest Version](https://img.shields.io/github/v/release/rokctAI/paas?label=Stable%20Version)](https://github.com/rokctAI/paas/releases)  
[![Build Status](https://github.com/rokctAI/paas/actions/workflows/auto_release.yml/badge.svg)](https://github.com/rokctAI/paas/actions)

## 📖 Overview

**PaaS** is a lightweight, open‑source Frappe app that adds a platform‑as‑a‑service layer. It enables self‑service provisioning of tenant sites based on subscription plans while remaining fully functional when used on its own.

- **Standalone mode** – works without any external dependencies, providing dummy data where needed.
- **Enhanced mode** – automatically runs sensitive seeders when the optional components are present.

## 🚀 Key Features

| Feature | Description |
|---------|-------------|
| **Conditional Installation** | Installs automatically only on tenant sites whose `plan_category` is `"paas"`; can also be installed manually on control sites for testing. |
| **Soft Optional Dependency** | The app tries to import optional helpers; if they are missing, it falls back to safe defaults. |
| **Automatic Seeder Integration** | After installation, the app runs seeders that populate payment‑gateway and settings data when available. |
| **Standalone Mode** | When optional helpers are absent, all checks return permissive defaults, keeping the app functional. |
| **Extensible API** | Public endpoints use a shim layer, making it easy to extend without breaking core functionality. |
| **Clear Separation** | No hard imports from other apps; cross‑app calls go through a thin shim. |

## 💻 System Requirements

| Resource | Minimum | Recommended |
|----------|----------|-------------|
| **OS** | Ubuntu 22.04 LTS | Ubuntu 22.04 LTS |
| **Python** | 3.10 | 3.10+ |
| **Frappe** | v15 | v15 |
| **RAM** | 2 GB | 4 GB+ |
| **Disk** | 10 GB SSD | 20 GB SSD |

> **Note** – The app itself is lightweight; any heavy services (databases, email, etc.) are managed separately.

## 📦 Installation

```bash
# From your bench directory
bench get-app https://github.com/rokctAI/paas.git
bench --site <your-site> install-app paas
bench --site <your-site> migrate
```

### Optional: Install optional helpers

If you have the optional helper package installed, the seeders will run automatically after installation.

```bash
bench get-app https://github.com/rokctAI/optional-helpers.git
bench --site <your-site> install-app optional-helpers
bench --site <your-site> migrate
```

## ⚙️ Configuration

Settings are available under **PaaS Settings** in the UI or can be overridden in `site_config.json`:

```json
{
  "paas": {
    "default_plan_category": "paas",
    "allow_control_site_install": true
  }
}
```

- `default_plan_category` – the plan category that triggers automatic provisioning.
- `allow_control_site_install` – when `true`, the app can be installed on a control site for development or documentation.

## 🏗️ Architecture Overview

```
paas/
├── api/               # Public REST endpoints
├── utils.py           # Shim for optional helpers
├── install.py         # Hooks: check_site_role & run_seeders
├── patches.txt        # Cleaned – no sensitive seeders
└── ...                # Doctypes, fixtures, etc.
```

## 🤝 Contributing

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/awesome-feature`).
3. Write tests (the `paas/tests` folder already contains a basic suite).
4. Submit a Pull Request.

Keep the shim layer intact – direct imports of optional helpers will break the standalone mode.

## 📜 License

AGPLv3 © Rokct Holdings. See the [LICENSE](LICENSE) file for details.

---

### 🎉 Quick Recap

- **Standalone** – works out‑of‑the‑box.
- **Enhanced** – runs seeders when optional helpers are present.
- **Clear separation** – all core logic lives inside the PaaS app.

Enjoy building on a lean, flexible platform!

## 📱 Flutter Builder Source Code

The **Flutter Builder** module (moved from Core) requires the source code for the mobile apps to be present to generate builds.

### Directory Structure
The source code for the apps (Customer, Driver, Manager, POS) must be placed in:
`paas/paas/builder/source_code/`

Expected structure:
```
paas/paas/builder/source_code/
├── customer/
├── driver/
├── manager/
└── pos/
```

### Auto-Fetch (Control App)
If the Control app is installed, PaaS will automatically request it to fetch the latest sources during installation via:
`control.control.api.fetch_paas_sources()`

### Manual Setup
If you do not have the Control app, you must manually clone the repositories:
```bash
cd apps/paas/paas/builder/source_code
git clone https://github.com/YourUser/juvo_customer.git customer
git clone https://github.com/YourUser/juvo_driver.git driver
# ... repeat for manager and pos
```
