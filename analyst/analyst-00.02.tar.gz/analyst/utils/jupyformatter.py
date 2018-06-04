#!/usr/bin/env python3
# coding: utf-8

"""
    Formatting Python Script Downloaded from Jupyter Notebook
    ver. 04 prod

 -----------------------------------------------------------------------------
                                                             hs@uchicago.edu
                                                           November 21, 2017


Format Python script downloaded from Jupyter Notebook to a clearer layout
according to the rules in `append_valid_line`.

Example usage:

    import analyst as a; a.jupyformatter()    #$

  Or use it as a standalone file located under the same directory:
    
    from jupyformatter import jupyformatter; jupyformatter(do_setup=True)   #$

  Set `do_deletion` to False if is used to format this script itself.
  `do_deletion` will not affect `#$ delete below`.


Todo:
    - More logging information, integrated with `-v` verbose option in
      `argparse`.
    - Implement `#$ delete from, #$ delete to` commands using `continue`
      in `edit`.
    - Automatically insert current date
""";


import argparse
import json
import logging
import os
import re
import textwrap
import time
from sys import platform
from urllib.parse import urljoin

import ipykernel
import requests
from notebook.notebookapp import list_running_servers


# `jupyformatter`
# ============================================================================


def jupyformatter(do_setup=False, do_deletion=True):
    """
    Main function
    """
    if do_setup:
        setup()
    convert_nb_to_py()
    script_name = get_notebook_name() + '.py'
    input_ls = read_input(script_name)
    output_ls = edit(input_ls, do_deletion)
    write_output(script_name, output_ls)


# `setup`
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def setup():
    """
    """
    if in_ipynb():
    # In Jupyter Notebook, `logging` module's `basicConfig()` only works
    # after reloading.
        from importlib import reload
        reload(logging)

    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',
                        datefmt='%H:%M:%S', level=logging.INFO)


def in_ipynb():
    """
    Return True if this code is running in a Jupyter Notebook environment.
    """
    try:
        return (str(type(get_ipython()))
                == "<class 'ipykernel.zmqshell.ZMQInteractiveShell'>")
    except NameError:
        return False


# `convert_nb_to_py`
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def convert_nb_to_py():
    """
    """
    notebook_name = get_notebook_name()

    # If eponymous script already exists, rename the original script with
    # a `_orig` suffix.
    if os.path.isfile(notebook_name + '.py'):
        os.rename(notebook_name+'.py', notebook_name+'_orig.py')
        logging.warning('Renamed eponymous script with `_orig` suffix.')

    os.system('jupyter nbconvert --to script {}'.format(notebook_name))


def get_notebook_name():
    """
    Return the name of the current jupyter notebook.

    References:
        https://github.com/jupyter/notebook/issues/1000#issuecomment-359875246
        https://stackoverflow.com/a/13055551
    """
    kernel_id = re.search('kernel-(.*).json',
                          ipykernel.connect.get_connection_file()).group(1)
    servers = list_running_servers()
    for ss in servers:
        response = requests.get(urljoin(ss['url'], 'api/sessions'),
                                params={'token': ss.get('token', '')})
        for nn in json.loads(response.text):
            if nn['kernel']['id'] == kernel_id:
                relative_path = nn['notebook']['path']
                match = re.search(r'/?(\w+).ipynb', relative_path)
                notebook_name = match.group(1)
                return notebook_name


# `parse_args`
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def parse_args():
    """
    Parse command line arguments to get input and output directories.

    Called by:
        main
    """
    parser = argparse.ArgumentParser(
        description="Format Python script downloaded from Jupyter Notebook.")

    parser.add_argument("in_dir", type=str, help="input script directory")
    parser.add_argument(
        "-o",
        "--out_dir",
        type=str,
        help="output directory",
        default="formatted {}.py".format(time.ctime()).replace(":", "-"),
        # `:` is not allowed in Windows filename
    )

    return parser.parse_args()


# `read_input`
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def read_input(filename):
    """
    Given filename (directory), return a list of lines of the input text file.
    """
    with open(filename) as f:
        input_ls = f.readlines()
    return input_ls


# `edit`
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def edit(input_ls, do_deletion):
    """
    Loop over each line for editing.

    Arg:
        input_ls (list):
            a list of lines readed from the input text file.

    Return:
        output_ls (list):
            a list of lines going to write to the output.

    Called by:
        main

    Calls:
        convert_heading
        clean_line
        warn_line
        append_valid_line
    """
    # Adding a Python 3 shebang line before the encoding definition
    input_ls[0] = "#!/usr/bin/env python3\n"

    # Convert personal heading to script docstring if horizontal rule shows up
    if '# ---\n' in input_ls[:11]:
        converted_input_ls = convert_heading(input_ls)
    else:
        converted_input_ls = input_ls
    # TODO June 1, 2018: what else for `converted_input_ls`

    output_ls = []
    for index, line in enumerate(converted_input_ls):
        line_num = index + 1
        line_cleaned = clean_line(line)
        warn_line(line_cleaned, line_num, do_deletion)

        if line_cleaned.lower().startswith("#$ delete below"):
            break

        append_valid_line(output_ls, line_cleaned, do_deletion)

    # End the file with (just) one new line character, according to
    # the POSIX standard, 3.206 Line. Given every raw line do end with a
    # new line character, eliminate the last single `\n` if applicable
    # to avoid extra new line at the end of the file.
    if output_ls[-1] == "\n":
        output_ls.pop()

    return output_ls


# `convert_heading`
# --------------------------------------------------------------------


def convert_heading(input_ls):
    '''
    Convert personal standard Notebook heading to script docstring.

    Return:
        converted_input_ls (list)

    Called by:
        edit

    Calls:
        wrap_markdown

    After effect: the header part of the list of lines will have one line
    fewer comparing to the original list.

    For example, convert the head of the script from
        1 |#!/usr/bin/env python3
        2 |# coding: utf-8
        3 |
        4 |# ## Formatting Python script downloaded from Jupyter Notebook
        5 |# Ver. 02 Proto
        6 |#
        7 |# ---
        8 |# <div style="text-align:right">HS<br>November 21, 2017</div>
        9 |
       10 |# In[29]:
       11 |
       12 |"""
       13 |Docstring
       14 |"""
    to
        1 |#!/usr/bin/env python3
        2 |# coding: utf-8
        3 |
        4 |"""
        5 |    Formatting Python script downloaded from Jupyter Notebook
        6 |    Ver. 02 Proto
        7 | -------------------------------------------------------------
        8 |                                                          HS
        9 |                                           November 21, 2017
       10 |
       11 |
       12 |Docstring
       13 |"""

    Mar 23, 2018: note that scripts downloaded from the Linux platform have
    one extra blank line after `# In[\d]:\n`.
    '''
    input_ls.insert(3, input_ls.pop( input_ls.index('"""\n')))
    # Move the first `"""` above the title

    i_horizon = input_ls.index('# ---\n')
    title_ls = input_ls[4:i_horizon]
    # The title and version info section
    wrapped_title_ls = []
    for line in title_ls:
        wrapped_title_ls.extend(wrap_markdown(line, wrap_at=77))
    formatted_title_ls = [" "*4 + line[2:] for line in wrapped_title_ls]

    horizon_ls = input_ls[i_horizon:]
    # The section of the horizontal rule and below

    horizon_ls[0] = " " + "-"*77 + " "    # Horizontal line

    # Author and date aligned to the right
    match_author_date = re.search(r">(.+)<br>(.+)<", horizon_ls[1])
    author, date = match_author_date.group(1), match_author_date.group(2)
    for index, field in [(1, author), (2, date)]:
        horizon_ls[index] = "{:>77}".format(field + "\n")
        # `{:>77}` string format means align the string to the right of a
        # line of length 77.

    converted_input_ls = input_ls[:4] + formatted_title_ls + horizon_ls
    return converted_input_ls


# `wrap_markdown`


def wrap_markdown(line, wrap_at=79):
    """
    Wrap Markdown heading/comment (starts with `# `) at `wrap_at`.

    Args:
        line (string)
        wrap_at (int, default to 79)

    Return:
        line_wrapped_ls (list): a list of line string(s) if the original
            line needs to be wrapped. Every line string in the list is a
            line ends with a new line character `\n`.

    Called by:
        append_valid_line
    """
    line_wrapped_ls = []

    delimiter_padding = None
    # Padding style of the delimiter for the corresponding level of heading
    if line.startswith("# ## "):
        # Level 2 Markdown heading
        delimiter_padding = "="
        num_padding = 76    # The number of delimiter characters in one line
 #      line_wrapped_ls.extend(["\n"])
        # 2 blank lines before level 2 heading, `append_valid_line` should
        # already leave 1 before.
    elif line.startswith("# ### "):
        # Level 3 Markdown heading
        delimiter_padding = "~"
        num_padding = 72
    elif line.startswith("# #### "):
        # Level 4 Markdown heading
        delimiter_padding = "-"
        num_padding = 68

    line_lstripped = line.lstrip("# ")

    if len(line_lstripped) > wrap_at-2:    # -2 compensate for `# `
        # Wrap the text, then add back comment marks and new line chars.

        textwrap_ls = textwrap.fill(
            line_lstripped, width=wrap_at-3).split("\n")
        # `textwrap.fill()` returns a list of wrapped strings that do not
        # end with new line character `\n`.
        #
        # `width=wrap_at-3` compensate 1 for the trailing `\n` and 2 for
        # the leading `# ` that will be added to each wrapped line of
        # comment/heading.

        for index, line in enumerate(textwrap_ls):
            textwrap_ls[index] = "# " + line + "\n"
        line_wrapped_ls.extend(textwrap_ls)
    else:
        line_wrapped_ls.append("# " + line_lstripped)

    if delimiter_padding:
        line_wrapped_ls.append("# " + delimiter_padding*num_padding + "\n")

    return line_wrapped_ls


# `clean_line`
# --------------------------------------------------------------------


def clean_line(line):
    """
    Clean line string with customed rules.

    Arg:
        line (string)

    Return:
        line (string)

    Called by:
        edit
    """
    # Strip "text\n  " or "text  \n" or "text  \n  " to "text\n"
    # Strip "  \n" or "\n  " or "  \n  " to "\n" to make sure excluding
    # extra line breaks in `append_valid_line()`
    line = line.rstrip() + "\n"

    # Delete Jupyter cell numbers `# In[\d]:\n` using `append_valid_line()`'s
    # consecutive blank line elimination mechanism
    if line.startswith("# In["):
        line = "\n"

    return line


# `warn_line`
# --------------------------------------------------------------------


def warn_line(line, line_num, do_deletion):
    """
    Log with customed rules.

    Called by:
        edit
    """
    if do_deletion:
        if "#@" in line:
            # A "#@" mark is my personal reminder to "check it later"
            logging.warning("\"#@\" mark founded in line {}".format(line_num))

        if "#$" in line:
            # A "#$" mark is my personal reminder to "delete this later"
            logging.info("\"#$\" mark founded in line {}".format(line_num))

    if not line.startswith("# ") and len(line) > 79:
        # Overlong comments and Markdowns will be wrapped by `wrap_markdown()`
        logging.warning("Line {} exceeds 79 characters".format(line_num))


# `append_valid_line`
# --------------------------------------------------------------------


def append_valid_line(output_ls, line, do_deletion):
    """
    Append line to the list of lines for output according to customed rules.

    Called by:
        edit

    Calls:
        wrap_markdown
    """
    is_valid = False
    # Judge if the line should be appended according to the rules below

    if line.startswith("# "):
        # Wrapping Markdown heading and comment to 79 characters a line
        output_ls.extend(wrap_markdown(line))
    else:
        # `#$` is my personal mark at the end of the line to exclude this
        # line from output
        is_keep = ("#$" not in line) if do_deletion else True

        # Should not have more than 2 consecutive blank lines in general
        if line == "\n" and output_ls[-2:] != ['\n', '\n']:
            is_valid = True

# But top-level function definition should have 2 blank lines above
# elif line.startswith("def ") or line.startswith("if __"):
# is_valid = True
# if output_ls[-1] == "\n":
# output_ls.append("\n")
# else:
# output_ls.extend(["\n", "\n"])

        elif is_keep and (line != "\n"):
            if line.startswith("get_ipython().magic("):
                # Comment out line and cell magics and display an
                # explanation
                output_ls.append("# " + line)
                output_ls.extend([
"# This code was originally developed in Jupyter Notebook. The above line\n",
"# magic may not work as part of a plain Python script. Therefore, it was\n",
"# commented out automatically by `jupyformatter.py`.\n", "\n"
                ])
            else:
                is_valid = True

    if is_valid:
        output_ls.append(line)


# `write_output`
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def write_output(out_fname, output_ls):
    """
    Write the formatted lines to output file.

    Called by:
        main
    """
    with open(out_fname, "w") as f:
        f.writelines(output_ls)

    logging.info('Successfully formatted to `{}`'.format(out_fname))

