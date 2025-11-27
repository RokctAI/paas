import frappe

def check_site_role():
    """
    Checks the site role before PaaS installation.
    PaaS can be installed on both tenant and control sites:
    - Tenant sites: Full PaaS functionality with seeders
    - Control sites: For Swagger documentation (no seeders)
    """
    app_role = frappe.conf.get("app_role", "tenant")
    print(f"PaaS installation on site: {frappe.local.site} (app_role: {app_role})")

def run_seeders():
    """
    Runs sensitive seeders from rokct if available.
    Only runs on tenant sites - control sites skip seeding.
    """
    app_role = frappe.conf.get("app_role", "tenant")
    
    if app_role == "control":
        print("Skipping PaaS seeders on control site (Swagger documentation only).")
        return
    
    # Only seed on tenant sites
    try:
        # Check if rokct app has the seeders module
        from rokct.control.seeders import seed_paas_payments, seed_paas_juvo_settings
        
        print("Running PaaS payment gateway seeder from rokct...")
        seed_paas_payments.execute()
        
        print("Running PaaS Juvo settings seeder from rokct...")
        seed_paas_juvo_settings.execute()
        
        print("PaaS seeders completed successfully.")
    except ImportError:
        # Seeders not available (rokct doesn't have them or not installed)
        print("Rokct seeders not found. Skipping sensitive data seeding.")
    except Exception as e:
        print(f"Error running PaaS seeders: {e}")
        frappe.log_error(f"Error running PaaS seeders: {e}", "PaaS Seeder Error")

