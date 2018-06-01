#!/usr/bin/python
#coding: utf-8

import os
from shutil import rmtree

def ll(path='.', ext=None, string=True, recursive=False):
    '''
    recursive or single list of file on directory.
    recursive=True return list recursive, string=True return list of string(path+file),
    string=False return list of tuple(path, file)

    :param path: path on Operation System
    :param string: Bool
    :param recursive: Bool
    :return: absolute path of file
    '''
    if (not string and recursive) and not ext:
        return [(p, file) for p, _, files in os.walk(os.path.abspath(path))for file in files]
    elif (not string and recursive) and ext:
        return [(p, file) for p, _, files in os.walk(os.path.abspath(path))for file in files if file.lower().endswith(ext)]
    elif (string and recursive) and not ext:
        return [os.path.join(p, file) for p, _, files in os.walk(os.path.abspath(path)) for file in files]
    elif (string and recursive) and ext:
        return [os.path.join(p, file) for p, _, files in os.walk(os.path.abspath(path)) for file in files if file.lower().endswith(ext)]
    elif (not string and not recursive) and not ext:
        return [(path, nome) for nome in os.listdir(path) if os.path.isfile(os.path.join(path, nome))]
    elif (not string and not recursive) and ext:
        return [(path, nome) for nome in os.listdir(path) if os.path.isfile(os.path.join(path, nome)) and nome.lower().endswith(ext)]
    elif (string and not recursive) and ext:
        return [os.path.join(path, nome) for nome in os.listdir(path) if os.path.isfile(os.path.join(path, nome)) and nome.lower().endswith(ext)]
    else:
        return [os.path.join(path, nome) for nome in os.listdir(path) if os.path.isfile(os.path.join(path, nome))]

def realfilename(filebase, ext=None, digits=2, separador=True):
    count = 0
    sufix = {'default': 'txt', 0: 'txt', 1: None, 2: None}

    if len(filebase.split('.')) > 1:
        prefix = os.path.abspath(os.path.dirname(filebase))
        basename = os.path.basename(filebase)
        #print('1: ', prefix, basename)

        filebase, sufix[1] = basename.split('.')
        #print('2: ', filebase, sufix[1])

        filebase = '{}/{}'.format(prefix, filebase)
        #print(filebase, sufix[1])

    if ext:
        sufix[2] = ''.join([i for i in ext if i.isalpha()])
        ext = sufix[2]
    elif sufix[1]:
        ext = sufix[1]
    else:
        ext = sufix['default']

    dir = os.path.dirname(filebase)
    #print(dir)
    os.makedirs(os.path.abspath(dir), exist_ok=True, mode=0o777)
    if separador:
        sep = '_'
    else:
        sep = ''
    while True:
        try:
            if count <= 0:
                filename = '{}.{}'.format(filebase, ext)
            else:
                filename = ('{}{}{:0>%s}.{}' % digits).format(filebase, sep, count, ext)
            if os.path.isfile(filename): raise IOError('Arquivo existente: {}'.format(filename))
            print('Criado arquivo: {}'.format(filename))
            return filename
        except IOError as e:
            print(e)
        except:
            raise
        finally:
            count += 1

def run(remove=False):
    with open(realfilename(
            os.path.join('tmp', 'britodfbr','diretorio', 'para', 'teste'),
            ext='.dat', separador=True), 'w') as file:
        file.write('teste ok')

    with open(realfilename(
            os.path.join('tmp', 'diretorio', 'para', 'teste'),
            separador=True, ext='md'),'w') as file:
        file.write('teste ok')

    with open(realfilename(('tmp/teste/test.json'),
            separador=True, ext='bash'),'w') as file:
        file.write('teste ok')

    with open(realfilename(('tmp/teste/lll'),
            separador=True),'w') as file:
        file.write('teste ok')

    with open(realfilename(('tmp/teste/jjj.json'),
            separador=True),'w') as file:
        file.write('teste ok')

    with open(realfilename(os.path.join('tmp', os.path.basename(__file__)),
            digits=4, ext='log', separador=False), 'a') as file:
        file.write(file.name)

    with open(realfilename(os.path.join('tmp', os.path.basename(__file__)),
            digits=5, ext='log', separador=True), 'a') as file:
        file.write(file.name)

    with open(realfilename(os.path.join('tmp', os.path.basename(__file__)),
            digits=5, ext='csv'), 'a') as file:
        file.write('{}'.format(file.name))

    with open(realfilename('../utils/tmp/registro.xml'), 'w') as file:
        file.write(file.name)

    print(ll())

    if remove:
        dirlist=['tmp']
        for i in dirlist:
            rmtree(i)

if __name__ == '__main__':
    run(False)