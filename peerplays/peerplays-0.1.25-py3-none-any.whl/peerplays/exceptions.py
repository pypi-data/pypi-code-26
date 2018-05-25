class WalletExists(Exception):
    """ A wallet has already been created and requires a password to be
        unlocked by means of :func:`peerplays.wallet.unlock`.
    """
    pass


class WalletLocked(Exception):
    """ Wallet is locked
    """
    pass


class AccountExistsException(Exception):
    """ The requested account already exists
    """
    pass


class AccountDoesNotExistsException(Exception):
    """ The account does not exist
    """
    pass


class AssetDoesNotExistsException(Exception):
    """ The asset does not exist
    """
    pass


class InsufficientAuthorityError(Exception):
    """ The transaction requires signature of a higher authority
    """
    pass


class MissingKeyError(Exception):
    """ A required key couldn't be found in the wallet
    """
    pass


class InvalidWifError(Exception):
    """ The provided private Key has an invalid format
    """
    pass


class ProposalDoesNotExistException(Exception):
    """ The proposal does not exist
    """
    pass


class BlockDoesNotExistsException(Exception):
    """ The block does not exist
    """
    pass


class NoWalletException(Exception):
    """ No Wallet could be found, please use :func:`peerplays.wallet.create` to
        create a new wallet
    """
    pass


class WitnessDoesNotExistsException(Exception):
    """ The witness does not exist
    """
    pass


class WrongMasterPasswordException(Exception):
    """ The password provided could not properly unlock the wallet
    """
    pass


class CommitteeMemberDoesNotExistsException(Exception):
    """ Committee Member does not exist
    """
    pass


class VestingBalanceDoesNotExistsException(Exception):
    """ Vesting Balance does not exist
    """
    pass


class BetDoesNotExistException(Exception):
    """ This bet does not exist
    """
    pass


class BettingMarketDoesNotExistException(Exception):
    """ Betting market does not exist
    """
    pass


class BettingMarketGroupDoesNotExistException(Exception):
    """ Betting Market Group does not exist
    """
    pass


class EventDoesNotExistException(Exception):
    """ This event does not exist
    """
    pass


class EventGroupDoesNotExistException(Exception):
    """ This event group does not exist
    """
    pass


class SportDoesNotExistException(Exception):
    """ Sport does not exist
    """
    pass


class RuleDoesNotExistException(Exception):
    """ Rule does not exist
    """
    pass


class ObjectNotInProposalBuffer(Exception):
    """ Couldn't find object to relative 0.0.x
    """
    pass


class InvalidMessageSignature(Exception):
    """ The message signature does not fit the message
    """
    pass


class KeyNotFound(Exception):
    """ Key not found
    """
    pass


class InvalidMemoKeyException(Exception):
    """ Memo key in message is invalid
    """
    pass


class OfflineHasNoRPCException(Exception):
    """ When in offline mode, we don't have RPC
    """
    pass


class WrongMemoKey(Exception):
    """ The memo provided is not equal the one on the blockchain
    """
    pass
