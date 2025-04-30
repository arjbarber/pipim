import pip._internal.commands.list as pip_list

def run_pip_list():
    cmd = pip_list.ListCommand()
    options, args = cmd.parse_args([])  # No extra args needed for basic pip list
    cmd.run(options, args)

if __name__ == "__main__":
    run_pip_list()
