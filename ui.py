import marimo

__generated_with = "0.19.7"
app = marimo.App(width="medium")

with app.setup:
    import marimo as mo
    from parsermouth import parse_log, parse_chunk, parse_dump, read_log_general, open_input, read_chunk_general, read_dump_general
    # from parsermouth import
    import pandas as pd
    from io import StringIO, BytesIO
    import re


@app.cell
def _():
    return


@app.cell
def _(dump_file):
    read_dump_general(BytesIO(dump_file.contents(0)), is_binary=True)
    return


@app.cell
def _():
    return


@app.cell
def _(chunk_file):
    read_chunk_general(BytesIO(chunk_file.contents(0)), is_binary=True)
    return


@app.cell
def _():
    read_chunk_general("chunk.dat")
    return


@app.cell
def _(read_chunk_general2):
    read_chunk_general2("chunk.dat").equals(read_chunk_general("chunk.dat"))
    return


@app.cell
def _(chunk_file):
    read_chunk_general("chunk.dat").equals(read_chunk_general(BytesIO(chunk_file.contents(0)), is_binary=True))
    return


@app.cell
def _():
    parse_chunk("chunk.dat").equals(read_chunk_general("chunk.dat"))
    return


@app.cell
def _(file_area):
    read_log_general("log.lammps").equals(read_log_general(BytesIO(file_area.contents(0)), is_binary=True))
    return


@app.cell
def _():
    read_log_general("log.lammps").equals(parse_log("log.lammps"))
    return


@app.cell
def _(file_area):
    read_log_general(BytesIO(file_area.contents(0)), is_binary=True)
    return


@app.cell
def _():
    read_log_general("log.lammps")
    return


@app.cell
def _():
    parse_log("log.lammps")
    return


@app.cell
def _():
    parse_chunk("chunk.dat")
    return


@app.cell
def _():
    parse_dump("out.dump")
    return


@app.cell
def _():
    parse_dump('contacts.dump')
    return


@app.cell
def _():
    parse_dump('intruder.dump')
    return


if __name__ == "__main__":
    app.run()
