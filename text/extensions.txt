from flask_marshmallow import Marshmallow 
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})
ma = Marshmallow()
limiter = Limiter(get_remote_address, default_limits=["2000/day", "500/hour"]) #creating and instance of Limiter