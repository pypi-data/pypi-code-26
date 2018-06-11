import csv
import click

@click.command()
@click.option('--infile', '-i', help='Full path and filename of the input CSV file.', prompt="Enter a valid CSV file")
def dataStats(infile):
    nRows = 0
    nCols = 0
    delim = ','
    with open(infile) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=delim)
        nCols = len(reader.fieldnames)
        for row in reader:
            nRows += 1
            
        
    print("\nFile contains " + str(nRows) + " rows and " + str(nCols) + " columns.\n\n")

if __name__ == '__main__':
    print('\n DataStats started ...\n\n')
    dataStats()
