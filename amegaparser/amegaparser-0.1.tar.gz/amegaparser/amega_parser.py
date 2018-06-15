import click
from . import events
from . import readings
from . import analysis

__version__ = "0.1"


@click.group()
@click.version_option(version=__version__, prog_name="AmegaView Data Parser")
def cli():
    pass


@cli.group(name="readings", invoke_without_command=True)
@click.pass_context
def cli_readings(ctx):
    """
    Utilities for working with Amega Point readings.
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli_readings.command(name="bin2csv")
@click.option("--output", type=click.Path(), default="output.csv")
@click.argument("input_file", type=click.File(mode="rb"))
def cli_readings_bin2csv(output, input_file):
    """ Binary to CSV. """
    readings.bin_to_csv(input_file, output)


@cli_readings.command(name="csv2bin")
@click.option("--output", type=click.Path(), default="output.xtt")
@click.argument("input_file", type=click.File(mode="r"))
def cli_readings_csv2bin(output, input_file):
    """
    CSV to Binary. Be sure to keep the header information in
    the CSV file!
    """
    readings.csv_to_bin(input_file, output)


@cli_readings.command(name="analysis")
@click.option("--file-type", type=click.Choice(["bin", "csv"]), default="bin")
@click.option("--output", type=click.Path(), default="output_analysis.csv")
@click.argument("input_file", type=click.Path(exists=True))
def cli_readings_analysis(file_type, output, input_file):
    mode = "rb" if file_type == "bin" else "r"

    with open(input_file, mode=mode) as f:
        data = getattr(readings, f"process_{file_type}")(f)

    analysis.bad_value_readings(data, output)


@cli.group(name="events", invoke_without_command=True)
@click.pass_context
def cli_events(ctx):
    """
    Utilities for working with AmegaView event logs.
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli_events.command(name="bin2csv")
@click.option("--output", type=click.Path(), default="output_events.csv")
@click.argument("input_file", type=click.File(mode="rb"))
def cli_events_bin2csv(output, input_file):
    """ Binary to CSV. """
    events.bin_to_csv(input_file, output)


@cli_events.command(name="csv2bin")
@click.option("--output", type=click.Path(), default="output_events.xtt")
@click.argument("input_file", type=click.File(mode="r"))
def cli_events_csv2bin(output, input_file):
    """
    CSV to Binary. Be sure to keep the header information in
    the CSV file!
    """
    events.csv_to_bin(input_file, output)


@cli.group(name="combined", invoke_without_command=True)
@click.pass_context
def cli_combined(ctx):
    """
    Analysis utilities for use with both reading and event information.
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli_combined.command(name="alarmstatus")
@click.option("--output", type=click.Path(), default="alarmstatus.csv")
@click.argument("readings_file", type=click.File("rb"))
@click.argument("events_file", type=click.File("rb"))
def cli_combined_alarmstatus(output, readings_file, events_file):
    """
    All provided files need to be the binary version.
    """
    reading_data = readings.process_bin(readings_file)
    event_data = events.process_bin(events_file)

    analysis.alarmstatus(reading_data, event_data, output)


if __name__ == "__main__":
    cli()
