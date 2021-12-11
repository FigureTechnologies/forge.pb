from forgepb import config_handler, global_, utils


# Entry point for wizard
def main():
    print(global_.FORGE)
    process_information, message = utils.view_running_node_info()
    print(message)
    while True:
        try:
            input_mode = int(input(
                "Select Action by Number:\n(1): Bootstrap Node\n(2): Edit Save Location\n(3): Stop Running Node\n(4): Start a bootstrapped node\n(5): Exit\n"))
        except ValueError:
            continue
        if input_mode == 1:
            utils.select_network()
        elif input_mode == 2:
            config_handler.set_build_location()
        elif input_mode == 3:
            utils.stop_active_node(process_information)
            exit()
        elif input_mode == 4:
            if process_information and process_information['node-running-info']:
                utils.handle_running_node(process_information)
            utils.start_node()
            exit()
        elif input_mode == 5:
            exit()


if __name__ == "__main__":
    main()
