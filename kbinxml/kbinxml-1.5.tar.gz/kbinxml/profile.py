from sixbit import *
from bytebuffer import ByteBuffer

test = 'Lorem_ipsum_dolor_sit_amet_consectetur_adipiscing_elit_Phasellus_ullamcorper_dui_non_commodo_dapibus_Integer_fringilla_ornare_risus_vitae_ultrices_Vestibulum_et_urna_auctor_pellentesque_quam_viverra_viverra_diam_Fusce_accumsan_lacinia_erat_id_amet_'
#test = (charmap*100)[:255]

b = ByteBuffer()

pack_sixbit(test, b)
#print(' '.join('{:08b}'.format(x) for x in b.data))
#print(' '.join('{:08b}'.format(x) for x in b_old.data))
b.offset = 0

new = unpack_sixbit(b)

