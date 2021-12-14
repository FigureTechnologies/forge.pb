from forgepb.command_line import root_cmd

if __name__ == '__main__':
    try:
        root_cmd()
        exit(0)
    except Exception as e:
        print(e)
        exit(1)
