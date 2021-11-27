import os

from forgepb import utils, config_handler

# Entry point
def main():
    while True:
        # Set mode for pbpm, else display choices again
        try:
            input_mode = int(input("Select Action by Number:\n(1): Bootstrap Node\n(2): Edit Save Location\n(3): Cancel\n"))
        except ValueError:
            continue

        if input_mode == 1:
            utils.select_env()
        elif input_mode == 2:
            config_handler.set_build_location()
        elif input_mode == 3:
            exit()

if __name__ == "__main__":
    main()