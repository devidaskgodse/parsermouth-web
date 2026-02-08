import marimo

__generated_with = "0.19.9"
app = marimo.App(width="medium")

with app.setup:
    import marimo as mo
    from io import BytesIO, StringIO
    from contextlib import contextmanager
    import pandas as pd


@app.cell
def _():
    mo.md(r"""
    # Parsermouth Web Demo
    `parsermouth` converts LAMMPS simulation outputs to dataframes.

    This demo notebook let you quickly load the LAMMPS files with drag and drop and view them as dataframes. You can also export them to csv files.

    Visit the [repository](https://github.com/devidaskgodse/parsermouth) for the `parsermouth` package.
    """)
    return


@app.function
@contextmanager
def open_input(source, mode='r'):
    """
    Handles file paths, StringIO, and BytesIO.
    Mode 'r' for text, 'rb' for bytes.
    """
    if isinstance(source, (str, bytes)) and not isinstance(source, (StringIO, BytesIO)):
        # If it's a string/bytes path, open the file
        with open(source, mode) as f:
            yield f
    else:
        # If it's already a stream (StringIO or BytesIO), just yield it
        yield source


@app.function
def read_log_general(filename_or_fileobj, is_binary=False):
    mode = 'rb' if is_binary else 'r'

    with open_input(filename_or_fileobj, mode=mode) as f:
        raw_data = f.read()

    # If the data is bytes, decode it to a string first
    if isinstance(raw_data, bytes):
        content = raw_data.decode('utf-8')
    else:
        content = raw_data

    lines = content.splitlines()

    # thermo data starts with a line containing "Step"
    # and ends just before a line containing "Loop"
    try:
        log_start_index = next(i for i, line in enumerate(lines) if line.strip().startswith("Step"))
        log_end_index = next(i for i, line in enumerate(lines) if "Loop" in line)
    except StopIteration:
        raise RuntimeError("Could not find Step/Loop markers in the log file")

    thermo_lines = [
        line
        for line in lines[log_start_index:log_end_index]
        if not line.strip().startswith("WARNING:")
    ]

    full_text = "\n".join(thermo_lines)
    return pd.read_csv(StringIO(full_text), sep=r'\s+')


@app.cell
def _(re):
    def read_chunk_general(filename_or_fileobj, is_binary=False):
        mode = 'rb' if is_binary else 'r'

        with open_input(filename_or_fileobj, mode=mode) as f:
            raw_data = f.read()

        # If the data is bytes, decode it to a string first
        if isinstance(raw_data, bytes):
            content = raw_data.decode('utf-8')
        else:
            content = raw_data

        lines = content.splitlines()

        # extract the timestamp from line 4 (index 3)
        end_timestamp = lines[3].split()[0]

        # extract headers from line 3 after the "# " (index 2)
        raw_headers = lines[2].split()[1:]

        # clean the headers: remove "c_", "v_", "[" and "]"
        cleaned_headers = [re.sub(r"c_|v_|\[|\]", "", h) for h in raw_headers]

        final_headers = ["timestep"] + cleaned_headers

        # parse data rows

        # join the lines (from index 4 onwards) into one large string
        data_body = "\n".join(lines[4:])

        # read the data using a whitespace separator
        # sep=r'\s+' handles any number of spaces or tabs
        df = pd.read_csv(StringIO(data_body), sep=r'\s+', names=final_headers[1:])

        # insert the timestamp as the first column
        df.insert(0, final_headers[0], pd.to_numeric(end_timestamp))

        return df

    return (read_chunk_general,)


@app.function
def read_dump_general(filename_or_fileobj, is_binary=False):
    mode = 'rb' if is_binary else 'r'

    with open_input(filename_or_fileobj, mode=mode) as f:
        raw_data = f.read()

    if isinstance(raw_data, bytes):
        content = raw_data.decode('utf-8')
    else:
        content = raw_data

    # setup iterator for processing
    lines = content.splitlines()
    line_iter = iter(lines)
    all_data = []
    headers = None

    # process blocks
    for line in line_iter:
        line = line.strip()

        if line == "ITEM: TIMESTEP":
            timestep = int(next(line_iter).strip())

            # skip ITEM: NUMBER OF ATOMS + read count
            next(line_iter)
            num_atoms = int(next(line_iter).strip())

            # skip ITEM: BOX BOUNDS (4 lines)
            for _ in range(4): next(line_iter)

            # parse ITEM: ATOMS header
            atom_header_line = next(line_iter)
            if headers is None:
                headers = ["timestep"] + atom_header_line.split()[2:]

            # read N atoms
            for _ in range(num_atoms):
                atom_data = next(line_iter).split()
                # convert to numeric immediately to prevent Object dtypes
                all_data.append([timestep] + [float(x) for x in atom_data])

    df = pd.DataFrame(all_data, columns=headers)

    # recast columns to integer
    potential_ints = ['timestep', 'id', 'type']
    cast_map = {col: int for col in potential_ints if col in df.columns}

    return df.astype(cast_map)


@app.cell
def _(read_chunk_general):
    # File input and dropdown
    file_input = mo.ui.file(label="Upload file", kind='area')

    dropdown_dict = mo.ui.dropdown(
        options = {
            "dump file": read_dump_general,
            "chunk file": read_chunk_general,
            "log file": read_log_general
        },
        value = "dump file", # initial value
        label = "Filetype"
    )
    return dropdown_dict, file_input


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ---
    """)
    return


@app.cell
def _(dropdown_dict, file_input):
    # Combine into a single form
    form = (
        mo.md(
            r"""
            ### Upload LAMMPS output file and select filetype

            {file_input}
            {choice}
            """
        )
        .batch(file_input=file_input, choice=dropdown_dict)
        .form(submit_button_label="Run")
    )

    form
    return (form,)


@app.cell
def _(form):
    output = None

    if form.value is not None:
        uploaded_file = form.value["file_input"]
        selected_option = form.value["choice"]

        file_contents = uploaded_file[0].contents
        data = BytesIO(file_contents)
        df = selected_option(data, is_binary=True)
        output = df
    else:
        uploaded_file = None
        selected_option = None

    output
    return


if __name__ == "__main__":
    app.run()
