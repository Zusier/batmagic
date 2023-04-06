import argparse
import tomllib
import re
import time

def load_config():
    CONFIG = "config.toml"
    with open(CONFIG, "rb") as f:
        return tomllib.load(f)

# replace that is not case sensitive
def no_case_replace(line, find, replace):
    compiled = re.compile(re.escape(find), re.IGNORECASE)
    res = compiled.sub(replace, line)
    return res


def format_reg(line, config):
    keys = [
        ("HKLM", "HKEY_LOCAL_MACHINE"),
        ("HKU", "HKEY_USERS"),
        ("HKCR", "HKEY_CLASSES_ROOT"),
        ("HKCU", "HKEY_CURRENT_USER"),
    ]
    for a, b in keys:
        if config["reg"]["SHORT_PATHS"]:
            line = no_case_replace(line, b, a)
        else:
            line = no_case_replace(line, a, b)
    return line


def format_batch_script(script_lines, config):
    formatted_lines = []
    # keeps track of the depth of indents
    indent_level = 0
    indent_prefix = " " * config["basic"]["INDENT_SIZE"]

    for line in script_lines:
        line = line.strip()
        match line:
            # check if there should be an indent on unclosed blocks
            case _ if ("{" in line and "}" not in line) or (
                "(" in line and ")" not in line
            ):
                formatted_lines.append((indent_prefix * indent_level) + line)
                indent_level += 1
            # check for closed blocks and decrease indents
            case _ if ("{" not in line and "}" in line) or (
                "(" not in line and ")" in line
            ):
                indent_level -= 1
                formatted_lines.append((indent_prefix * indent_level) + line)
            # check for comments
            case _ if line.startswith("::"):
                formatted_lines.append(config["basic"]["COMMENT_STYLE"] + line[2:])
            case _ if line.startswith("REM"):
                formatted_lines.append(config["basic"]["COMMENT_STYLE"] + line[3:])
            # format registry commands
            case _ if line.startswith("reg"):
                reg = format_reg(line, config)
                formatted_lines.append((indent_prefix * indent_level) + reg)
            # check for goto's and labels
            case _ if line.startswith("goto") or line.startswith(":"):
                formatted_lines.append(" " * indent_level + line)
            case _:
                formatted_lines.append((indent_prefix * indent_level) + line)
    return formatted_lines


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    # load config
    config = load_config()

    # load script to format
    with open(args.filename, "r") as f:
        script_lines = f.readlines()

    start_time = time.perf_counter()  # start the timer

    formatted_lines = format_batch_script(script_lines, config)

    # record runtime
    end_time = time.perf_counter()  # stop the timer
    elapsed_time_ms = (end_time - start_time) * 1000

    print(f"Execution time: {elapsed_time_ms:.2f} ms")

    output_filename = args.filename.split(".")[0] + "_formatted.bat"
    with open(output_filename, "w") as f:
        f.write("\n".join(formatted_lines))
