import os

from forgepb import utils, config_handler

# Entry point for wizard
def main():
    while True:
        try:
            input_mode = int(input("Select Action by Number:\n(1): Bootstrap Node\n(2): Edit Save Location\n(3): Cancel\n"))
        except ValueError:
            continue
        if input_mode == 1:
            utils.select_network()
        elif input_mode == 2:
            config_handler.set_build_location()
        elif input_mode == 3:
            exit()

if __name__ == "__main__":
    main()