import utils
from faker import Faker
from const import POPULAR_TYPES


def create_data(rows: int, fields: list, locale: str = 'ru_RU') -> list:
    """
    Генерирует данные на основе указанных полей и количества строк.

    Аргументы:

    rows: Количество записей для генерации
    fields: Список конфигураций полей (каждое с полями 'name' и 'type')
    locale: Локаль для Faker (по умолчанию: 'ru_RU')

    Возвращает:
    Список словарей, содержащих сгенерированные фиктивные данные
    """
    faker = Faker(locale)
    column_generators = []

    for field in fields:
        field_name = field['name']
        field_type = field['type']

        available_methods = POPULAR_TYPES.get(field_type, [])

        print(f"\nField: '{field_name}'")
        print(f"Type: {field_type}")
        print(f"Available methods for {field_type}:")
        print(", ".join(available_methods))

        chosen_method = utils.input_validation(
            prompt="Enter the method name: ",
            expected_type=str,
            validation_func=lambda x: x in available_methods
        )

        generator_func = getattr(faker, chosen_method)
        column_generators.append((field_name, generator_func))

    data = []
    for _ in range(rows):
        record = {}
        for field_name, generator_func in column_generators:
            record[field_name] = generator_func()
        data.append(record)

    print("\nSample of generated data (first 5 records):")
    for i, record in enumerate(data[:5], 1):
        print(f"{i}. {record}")

    return data