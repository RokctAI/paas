import frappe
from frappe.tests.utils import FrappeTestCase

# Import the functions to be tested
from paas.api.shop.shop import create_shop, get_shops, get_shop_details

class TestShopAPI(FrappeTestCase):
    def setUp(self):
        # Create users
        if not frappe.db.exists("User", "test-seller@example.com"):
            self.seller_user = frappe.get_doc({
                "doctype": "User",
                "email": "test-seller@example.com",
                "first_name": "Test",
                "last_name": "Seller",
                "roles": [{"role": "Seller"}]
            }).insert(ignore_permissions=True)
        else:
            self.seller_user = frappe.get_doc("User", "test-seller@example.com")

        if not frappe.db.exists("User", "test-seller-2@example.com"):
            self.seller_user_2 = frappe.get_doc({
                "doctype": "User",
                "email": "test-seller-2@example.com",
                "first_name": "Test",
                "last_name": "Seller 2",
                "roles": [{"role": "Seller"}]
            }).insert(ignore_permissions=True)
        else:
            self.seller_user_2 = frappe.get_doc("User", "test-seller-2@example.com")

        if not frappe.db.exists("User", "non-seller@example.com"):
            self.non_seller_user = frappe.get_doc({
                "doctype": "User",
                "email": "non-seller@example.com",
                "first_name": "Non",
                "last_name": "Seller",
            }).insert(ignore_permissions=True)
        else:
            self.non_seller_user = frappe.get_doc("User", "non-seller@example.com")

        # Log in as a seller to create shops
        frappe.set_user(self.seller_user.name)

        # Create some mock shops
        if not frappe.db.exists("Shop", {"shop_name": "Test Shop 1"}):
            self.shop1 = create_shop({
                "shop_name": "Test Shop 1",
                "status": "approved",
                "open": 1,
                "visibility": 1,
                "delivery": 1,
                "user": self.seller_user.name,
                "phone": "+14155552671"
            })
        else:
            self.shop1 = frappe.get_doc("Shop", {"shop_name": "Test Shop 1"}).as_dict()

        if not frappe.db.exists("Shop", {"shop_name": "Test Shop 2"}):
            self.shop2 = create_shop({
                "shop_name": "Test Shop 2",
                "status": "approved",
                "open": 1,
                "visibility": 1,
                "pickup": 1,
                "user": self.seller_user_2.name,
                "phone": "+14155552671"
            })
        else:
            self.shop2 = frappe.get_doc("Shop", {"shop_name": "Test Shop 2"}).as_dict()

        if not frappe.db.exists("Shop", {"shop_name": "Test Shop 3 Not Approved"}):
            self.shop3_not_approved = create_shop({
                "shop_name": "Test Shop 3 Not Approved",
                "status": "new",
                "open": 1,
                "visibility": 1,
                "user": self.seller_user.name,
                "phone": "+14155552671"
            })
        else:
            self.shop3_not_approved = frappe.get_doc("Shop", {"shop_name": "Test Shop 3 Not Approved"}).as_dict()

        if not frappe.db.exists("Shop", {"shop_name": "Test Shop 4 Not Visible"}):
            self.shop4_not_visible = create_shop({
                "shop_name": "Test Shop 4 Not Visible",
                "status": "approved",
                "open": 1,
                "visibility": 0,
                "user": self.seller_user.name,
                "phone": "+14155552671"
            })
        else:
            self.shop4_not_visible = frappe.get_doc("Shop", {"shop_name": "Test Shop 4 Not Visible"}).as_dict()

        # Switch back to administrator
        frappe.set_user("Administrator")

    def tearDown(self):
        # This method will be run after each test
        frappe.set_user("Administrator")
        
        # Delete Key Documents First (Children/Linked)
        shops_to_delete = ["Test Shop 1", "Test Shop 2", "Test Shop 3 Not Approved", "Test Shop 4 Not Visible"]
        for shop_name in shops_to_delete:
            if frappe.db.exists("Shop", shop_name):
                 frappe.delete_doc("Shop", shop_name, force=True, ignore_permissions=True)
                 
        # Delete Users
        users_to_delete = ["test-seller@example.com", "test-seller-2@example.com", "non-seller@example.com"]
        for user_email in users_to_delete:
             if frappe.db.exists("User", user_email):
                  frappe.delete_doc("User", user_email, force=True, ignore_permissions=True)

    def test_create_shop_unauthorized(self):
        """Test that a user without the Seller role cannot create a shop."""
        frappe.set_user(self.non_seller_user.name)
        with self.assertRaises(frappe.PermissionError):
            create_shop({"shop_name": "Unauthorized Shop"})

    def test_create_shop_success(self):
        """Test successful shop creation."""
        self.assertIn('uuid', self.shop1)
        self.assertIn('slug', self.shop1)
        self.assertEqual(self.shop1['slug'], 'test-shop-1')

    def test_get_shops_no_filters(self):
        """Test fetching shops without any filters."""
        shops = get_shops(limit_page_length=20)

        # Should only return approved, open, and visible shops
        self.assertEqual(len(shops), 2)
        shop_names = [s['id'] for s in shops]
        self.assertIn("Test Shop 1", shop_names)
        self.assertIn("Test Shop 2", shop_names)
        self.assertNotIn("Test Shop 3 Not Approved", shop_names)
        self.assertNotIn("Test Shop 4 Not Visible", shop_names)

    def test_get_shops_pagination(self):
        """Test pagination for get_shops."""
        # Get the first page with one item
        shops_page1 = get_shops(limit_start=0, limit_page_length=1, order_by="shop_name", order="asc")
        self.assertEqual(len(shops_page1), 1)
        self.assertEqual(shops_page1[0]['id'], 'Test Shop 1')

        # Get the second page with one item
        shops_page2 = get_shops(limit_start=1, limit_page_length=1, order_by="shop_name", order="asc")
        self.assertEqual(len(shops_page2), 1)
        self.assertEqual(shops_page2[0]['id'], 'Test Shop 2')

    def test_get_shop_details_success(self):
        """Test fetching details for a single, valid shop."""
        shop_details = get_shop_details(uuid=self.shop1['uuid'])
        self.assertIsNotNone(shop_details)
        self.assertEqual(shop_details['id'], self.shop1['shop_name'])
        self.assertEqual(shop_details['uuid'], self.shop1['uuid'])
        self.assertEqual(shop_details['translation']['title'], self.shop1['shop_name'])

    def test_get_shop_details_not_found(self):
        """Test fetching details for a non-existent shop."""
        with self.assertRaises(frappe.DoesNotExistError):
            get_shop_details(uuid="non-existent-uuid")

    def test_get_shops_with_delivery_filter(self):
        """Test fetching shops with delivery=True filter."""
        shops = get_shops(delivery=True)
        self.assertEqual(len(shops), 1)
        self.assertEqual(shops[0]['id'], "Test Shop 1")

    def test_get_shops_with_takeaway_filter(self):
        """Test fetching shops with takeaway=True filter."""
        shops = get_shops(takeaway=True)
        self.assertEqual(len(shops), 1)
        self.assertEqual(shops[0]['id'], "Test Shop 2")

    def test_get_shops_ordering(self):
        """Test ordering of shops."""
        # Test ordering by name descending
        shops_desc = get_shops(order_by="shop_name", order="desc")
        self.assertEqual(shops_desc[0]['id'], "Test Shop 2")
        self.assertEqual(shops_desc[1]['id'], "Test Shop 1")

        # Test ordering by name ascending
        shops_asc = get_shops(order_by="shop_name", order="asc")
        self.assertEqual(shops_asc[0]['id'], "Test Shop 1")
        self.assertEqual(shops_asc[1]['id'], "Test Shop 2")

if __name__ == '__main__':
    # This allows running the tests directly
    # Note: This requires a running Frappe instance and site context.
    # The recommended way to run tests is via `bench --site {site_name} execute ...`
    pass
