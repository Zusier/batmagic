import argparse

INDENT_SIZE = 4
COMMENT_STYLE = "::"

def format_batch_script(script_lines):
    formatted_lines = []
    indent_level = 0
    for line in script_lines:
        line = line.strip()
        if ("{" in line and "}" not in line) or ("(" in line and ")" not in line):
            formatted_lines.append(((" " * INDENT_SIZE) * indent_level) + line)
            indent_level+=1
        elif ("{" not in line and "}" in line) or ("(" not in line and ")" in line):
            indent_level-=1
            formatted_lines.append(((" " * INDENT_SIZE) * indent_level) + line)
        elif line.startswith("::"):
            formatted_lines.append(COMMENT_STYLE + line[2:])
        elif line.startswith("REM"):
            formatted_lines.append(COMMENT_STYLE + line[3:])
        elif line.startswith("goto") or line.startswith(":"):
            formatted_lines.append(" " * indent_level + line)
        else:
            formatted_lines.append(((" " * INDENT_SIZE) * indent_level) + line)
    return formatted_lines

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    with open(args.filename, "r") as f:
        script_lines = f.readlines()

    formatted_lines = format_batch_script(script_lines)

    output_filename = args.filename.split(".")[0] + "_formatted.bat"
    with open(output_filename, "w") as f:
        f.write("\n".join(formatted_lines))
