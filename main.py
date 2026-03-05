import os
import sys
import subprocess
from const import YES_RESPONSES
import config
import generators
import saver
import utils


def launch_in_terminal():
    """
    Запускает скрипт в новом терминальном окне, если он не был запущен из терминала.
    """
    if os.environ.get('TERMINAL_STARTED') != '1':
        env = os.environ.copy()
        env['TERMINAL_STARTED'] = '1'
        subprocess.run(
            ['gnome-terminal', '--', 'bash', '-c', 'python3 main.py; exec bash'],
            env=env
        )
        sys.exit()


def get_user_confirmation(question: str) -> bool:
    response = utils.input_validation(
        prompt=f"{question}\nYour answer (yes/no): ",
        expected_type=str,
        validation_func=lambda x: x.lower() in YES_RESPONSES | {'no', 'n'},
        error_message="Please answer 'yes' or 'no'"
    )
    return response.lower() in YES_RESPONSES


def main():
    try:
        #launch_in_terminal()

        rows, fields = config.get_parametrs()

        data = generators.create_data(rows, fields)

        if get_user_confirmation("Do you want to save data to a file?"):
            saver.save_data_to_file(data)

        if get_user_confirmation("Do you want to save data to database?"):
            saver.save_data_to_db(data)

        print("\nProcess completed successfully!")

    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)
    finally:
        input("\nPress Enter to close the window...")


if __name__ == "__main__":
    main()