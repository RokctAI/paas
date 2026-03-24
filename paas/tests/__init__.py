import sys
from unittest.mock import MagicMock
import unittest

# 1. Mock 'frappe' and its submodules if missing
if 'frappe' not in sys.modules:
    mock_frappe = MagicMock()
    # Handle 'frappe' as a package
    mock_frappe.__path__ = []
    # Mock __spec__ to avoid importlib issues during patching
    mock_frappe.__spec__ = MagicMock()
    sys.modules['frappe'] = mock_frappe

    # Nested mocking for common frappe submodules
    # Must do this in order of depth to ensure parents exist
    sub_packages = ['frappe.tests', 'frappe.model',
                    'frappe.custom', 'frappe.database', 'frappe.query_builder']
    for pkg in sub_packages:
        m = MagicMock()
        m.__path__ = []
        m.__spec__ = MagicMock()
        sys.modules[pkg] = m

    sub_modules = [
        'frappe.tests.utils', 'frappe.utils', 'frappe.model.document',
        'frappe.custom.doctype', 'frappe.custom.doctype.custom_field',
        'frappe.custom.doctype.custom_field.custom_field', 'frappe.exceptions',
        'frappe.database.mariadb', 'frappe.database.mariadb.database',
        'frappe.query_builder.functions', 'frappe.auth', 'frappe.qb'
    ]
    for mod in sub_modules:
        m = MagicMock()
        m.__spec__ = MagicMock()
        sys.modules[mod] = m

    # Mock core attributes/functions frequently used at top level or during
    # class definition
    mock_frappe._ = lambda x: x
    mock_frappe.whitelist = lambda *args, **kwargs: (lambda f: f)

    # Define a base class that skips tests when mocked
    class SkipOnMockTestCase(unittest.TestCase):
        @classmethod
        def setUpClass(cls):
            # Check if frappe is mocked
            if 'frappe' in sys.modules and (
                isinstance(
                    sys.modules['frappe'],
                    MagicMock) or getattr(
                    sys.modules['frappe'],
                    '_is_mock',
                    False)):
                raise unittest.SkipTest(
                    "Skipping Frappe test in mocked environment")
            if hasattr(super(), 'setUpClass'):
                super().setUpClass()

    mock_frappe._is_mock = True
    sys.modules['frappe.tests.utils'].FrappeTestCase = SkipOnMockTestCase

    # Mock exceptions as classes
    for err in ['AuthenticationError', 'ValidationError', 'PermissionError',
                'DoesNotExistError', 'DuplicateEntryError', 'LinkExistsError']:
        err_cls = type(err, (Exception,), {})
        setattr(mock_frappe, err, err_cls)
        setattr(sys.modules['frappe.exceptions'], err, err_cls)

# 2. Mock other dependencies
missing_deps = [
    'rcore', 'rcore.utils', 'rcore.tenant', 'rcore.tenant.api',
    'rcore.rlending', 'rcore.rlending.wallet_integration',
    'erpnext', 'staticmap', 'sentence_transformers'
]

for dep in missing_deps:
    if dep not in sys.modules:
        m = MagicMock()
        # Handle some nested imports by giving it a __path__
        m.__path__ = []
        m.__spec__ = MagicMock()
        sys.modules[dep] = m

# Special handling for cryptography as it's often imported deeply
if 'cryptography' not in sys.modules:
    for crypto_sub in [
        'cryptography',
        'cryptography.hazmat',
        'cryptography.hazmat.primitives',
        'cryptography.hazmat.primitives.asymmetric',
        'cryptography.hazmat.primitives.ciphers',
        'cryptography.hazmat.primitives.ciphers.algorithms',
        'cryptography.hazmat.primitives.ciphers.modes',
        'cryptography.hazmat.primitives.kdf',
        'cryptography.hazmat.primitives.kdf.pbkdf2',
            'cryptography.hazmat.backends']:
        if crypto_sub not in sys.modules:
            m = MagicMock()
            m.__path__ = []
            m.__spec__ = MagicMock()
            sys.modules[crypto_sub] = m

# Ensure requests is available
if 'requests' not in sys.modules:
    try:
        import requests  # noqa: F401
    except ImportError:
        m = MagicMock()
        m.__spec__ = MagicMock()
        sys.modules['requests'] = m
