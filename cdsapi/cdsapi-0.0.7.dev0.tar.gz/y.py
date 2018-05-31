import cdsapi
c = cdsapi.Client()

r = c.retrieve(
    'seasonal-monthly-pressure-levels',
    {
        'format':'grib'
    }
)
r.download('download.grib')
