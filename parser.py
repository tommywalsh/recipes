import json


def lines_until_next_blanks(doc):
    lines = []
    while True:
        rawline = doc.readline()
        if not rawline:
            return lines
        line = rawline.strip()

        if len(line) == 0:
            # Skip any leading blank lines
            if len(lines) != 0:
                return lines
        else:
            lines.append(line)


def parse_title(line):
    assert len(line) != 0
    return line


def parse_header(header_lines):
    assert len(header_lines) == 1
    return {"title": parse_title(header_lines[0])}


def parse_step(step_lines):
    ingredients = []
    other_inputs = []
    instructions = None

    for line in step_lines:
        if line.startswith("-"):
            ingredients.append(line.lstrip("- "))
        elif line.startswith("+"):
            other_inputs.append(line.lstrip("+ "))
        elif instructions:
            instructions = "{} {}".format(instructions, line)
        else:
            instructions = line

    return {
        "ingredients": ingredients,
        "other_inputs": other_inputs,
        "instructions": instructions
    }


def parse_recipe(recipe):
    header = parse_header(lines_until_next_blanks(recipe))
    steps = []
    while True:
        step_lines = lines_until_next_blanks(recipe)
        if len(step_lines) == 0:
            break
        steps.append(parse_step(step_lines))

    return {
        "title": header["title"],
        "steps": steps
    }


def write_recipe_file(recipe_obj):
    title = recipe_obj["title"]
    filename = "{}.json".format(title.replace(' ', '_').lower())
    with open(filename, "w") as output_file:
        json.dump(recipe_obj, output_file, indent=2)


def parse_file(filename):
    with open(filename) as recipe:
        return parse_recipe(recipe)

