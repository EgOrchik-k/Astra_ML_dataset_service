import utils

from const import TYPES


def get_parametrs():
    num_rows = utils.input_validation(
        prompt="Enter the number of rows:",
        expected_type=int,
        validation_func=lambda x: x > 0
    )
    num_fields = utils.input_validation(
        prompt="Enter the number of fields:",
        expected_type=int,
        validation_func=lambda x: x > 0
    )

    fields = []
    print("\nCorrect data types:\n", ", ".join(TYPES))

    for i in range(1, num_fields + 1):
        print(f"\nFields {i}:")
        name = input("Field name: ").strip()

        fields_type = utils.input_validation(
            prompt="Data type: ",
            expected_type=str,
            validation_func=lambda x: x in TYPES,
        )

        fields.append({'name': name, 'type': fields_type})

    print(f"\nCurrent parameters:\n{num_rows}, {fields}")
    return num_rows, fields