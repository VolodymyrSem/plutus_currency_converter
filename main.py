import time

from converter.app.app import App
from converter.app.menu import Menu
from converter.core.exceptions import *


def main():
    menu = Menu()
    app = App()
    try:
        app.set_up_directories_and_check_server_state()
        while True:
            menu.print_main_menu()
            input_num = menu.input_choice_main_menu()
            if input_num == '1':
                app.exchange()
            elif input_num == '2':
                app.double_conversion()
            elif input_num == '3':
                app.show_saved_currencies()
            elif input_num == '4':
                start = time.time()
                app.update_rates()
                end = time.time()
                print(f'Downloaded in {end - start} seconds')
            elif input_num == '5':
                app.create_pairs()
            elif input_num == '6':
                app.delete_pairs()
            elif input_num == '7':
                app.delete_all_pairs()
            elif input_num == 'x':
                app.switch_rate_source()
            else:
                raise KeyboardInterrupt
            menu.ask_to_continue()
    except KeyboardInterrupt:
        menu.print_goodbye()
    # except Exception as e:
    #     menu.print_exception(e)
    #     menu.print_exiting()


if __name__ == '__main__':
    main()
    time.sleep(3)
    exit()