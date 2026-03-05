def input_validation(prompt, expected_type, validation_func=None, error_message=None):
    """
    Проверка пользовательского ввода с преобразованием типа и валидацией.

    Аргументы:
        prompt: Сообщение для отображения пользователю
        expected_type: Ожидаемый тип для преобразования (str, int и т. д.)
        validation_func: Необязательная функция для проверки преобразованного значения
        error_message: Cообщение об ошибке (по умолчанию: ошибка общего типа)

    Возвращает:
        Преобразованное и проверенное значение.
    """
    if error_message is None:
        error_message = f"Invalid input. Expected {expected_type.__name__}"

    while True:
        user_input = input(prompt).strip()

        if not user_input:
            print("Input cannot be empty. Please try again.")
            continue

        try:
            converted_value = expected_type(user_input)

            if validation_func and not validation_func(converted_value):
                print(error_message)
                continue

            return converted_value

        except ValueError:
            print(f"Invalid input. Expected {expected_type.__name__}")
