import os


def read(*rnames):
    '''
    return content from file informed in '*rnames'
    :param rnames:
    :return:
    >>> read(os.path.dirname(__file__), 'version.txt')
    '0.7.2'

    >>> read(os.path.dirname(__file__), 'README')
    'incolumepy.utils'

    '''
    with open(os.path.join(os.path.dirname(__file__), *rnames)) as f:
        return f.read().strip()


def namespace(package_name):
    '''
    return the namespace from package_name='incolumepy.package.module' ['incolumepy','incolumepy.package']
    :param package_name: str
    :return: list

    >>> namespace('incolumepy.package.subpackage.module')
    ['incolumepy', 'incolumepy.package', 'incolumepy.package.subpackage']
    >>> namespace('incolumepy.package.module')
    ['incolumepy', 'incolumepy.package']

    >>> namespace('incolumepy.package')
    ['incolumepy']

    >>> namespace('incolumepy')
    ['incolumepy']
    '''
    #print(package_name)
    s = package_name.split('.')
    #print(s)
    l = []
    if len(s) > 2:
        inanis = ''
        for item in s[:-1]:
            if inanis:
                inanis = '{}.{}'.format(inanis, item)
            else:
                inanis = item
            l.append(inanis)
    elif 0 < len(s) <= 2:
        l =s[:1]
    else:
        raise ValueError('package_name not can be void')

    #if len(package_name)<=0:
    #elif 0 < len(s) <= 2:
    #    l = s[1]
    #else:
    #    for item in s[:-1]:
    #        if l:
    #            l.append('{}.{}'.format(l[-1], item))
    #        else:
    #            l.append(item)
    #            pass
    #        #print(l)
    return l

def run():
    print(namespace('incolumepy.package.subpackage.module'))
    print(namespace('incolumepy.package'))
    print(namespace('incolumepy'))
    print(namespace(''))

if __name__ == "__main__":
    pass
    #run()
