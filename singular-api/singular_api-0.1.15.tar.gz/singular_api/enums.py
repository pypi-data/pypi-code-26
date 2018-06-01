class RemoveMethod(object):
    DontRemove = 0
    FromSC = 1
    FromConn = 2
    FromBoth = 3


RemoveMethods = (
    (RemoveMethod.DontRemove, 'Dont remove'),
    (RemoveMethod.FromSC, 'Remove from Singular Center'),
    (RemoveMethod.FromConn, 'Remove from Connector'),
    (RemoveMethod.FromBoth, 'Remove from Singular Center and Connector'),
)
