from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
STORAGE_DIR = BASE_DIR / "storage" / "uploads"

TYPES = ['str', 'int', 'float', 'bool']

POPULAR_TYPES = {
    'str': ['name', 'address', 'phone_number', 'email', 'job', 'company',
            'text', 'country', 'city', 'street_address', 'postcode', 'pystr'],
    'int': ['pyint', 'random_int', 'year', 'month', 'day_of_month'],
    'float': ['pyfloat', 'latitude', 'longitude'],
    'bool': ['boolean', 'pybool']
}

DEFAULT_LOCALE = 'ru_RU'
DEFAULT_SAMPLE_SIZE = 5

YES_RESPONSES = {'yes', 'y'}
NO_RESPONSES = {'no', 'n'}