# Monoid:
from categories.monoid import mappend, mempty

# Functor:
from categories.functor import fmap

# Applicative:
from categories.applicative import apply, pure

# Monad:
from categories.monad import bind, mreturn

# Set up default instances for some built-in types:
from categories import builtins
