# Simple Recipe Server

This project's goal is to make it possible to write/store recipes as easily-editable text files, while also making the
recipes available in a variety of other visual formats, depending on the context (shopping, planning, cooking).

The basic strategy is like this:
- A human writes recipes in separate text files (in a particular format)
- Those text files are converted to JSON files
- A handful of HTML files know how to display those JSON files
- A simple web server makes those HTML and JSON files available

To get setup, you need:
- A copy of Python 3 installed on the system
- A local virtual Python environment (`virtualenv -P <path to python3> venv"`)
- A Neocites API token, saved to a local file named `api_key`

To use:
- Activate the virtual environment (`source venv/bin/activate`)
- Add/edit files in the `recipe` directory.
- Run `build.py package` to generate website files into the `dist` directory.
- To test locally, run `python -m http.server` from the `dist` directory. Then, point a webbrowser to wherever that command tells you.
- To upload to Neocities on the internet, run `build.py publish -k api_file` where `api_file` is a text file containing a Neocities API key.

The recipe text files have the following format. 
- The first line is the title
- After the title comes a set of steps. Each step has, in this order:
  - A blank line
  - (Optional) a set of ingredients, one per line, all beginning with a minus sign.
  - (Optional) a set of other things, one per line, all beginning with a plus sign.
  - A set of lines (not beginning with a plus or minus character) with text describing the step.


For example, here is what a simple recipe for crackers might look like:
```
Crackers

Preheat oven to 400F

- 1 cup flour
- 1/2 tsp salt
- 2 Tbsp cold butter
Cut butter roughly into 5 or so pieces.
Place flour, salt, and butter in a food processor fitted with the dough blade.
Pulse until well combined

- 1/4 cup water, or more
+ flour mixture 
Add water to flour mixture and pulse to combine.
Add more water, a little at a time, if necessary, just until the mixture holds together but is not sticky.

- salt (optional)
+ wax paper
Roll dough out onto wax paper until about 1/4 inch thick.
Score cracker shapes with a sharp knife
Sprinkle with salt to taste

Bake about 10 minutes, until lightly browned

```
