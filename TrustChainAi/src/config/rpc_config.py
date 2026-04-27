"""RPC configuration for multi-provider fallback strategy."""

from dataclasses import dataclass
from typing import List


@dataclass
class RpcProvider:
    """RPC provider configuration."""
    name: str
    url_template: str  # Contains {api_key} placeholder
    priority: int  # Lower = higher priority
    rate_limit: int = 100  # Calls per second


# Primary: Infura
INFURA_PROVIDER = RpcProvider(
    name="infura",
    url_template="https://mainnet.infura.io/v3/{api_key}",
    priority=1,
    rate_limit=100
)

# Fallback: Alchemy
ALCHEMY_PROVIDER = RpcProvider(
    name="alchemy",
    url_template="https://eth-mainnet.g.alchemy.com/v2/{api_key}",
    priority=2,
    rate_limit=100
)

# Provider chain (order matters - first is primary)
RPC_PROVIDERS: List[RpcProvider] = [
    INFURA_PROVIDER,
    ALCHEMY_PROVIDER,
]

# Retry configuration
MAX_RETRIES = 3
BACKOFF_MULTIPLIER = 2  # 1s → 2s → 4s
INITIAL_BACKOFF = 1.0  # seconds

# Cache configuration
CACHE_ENABLED = True
CACHE_EXPIRY_HOURS = 24
CACHE_PATH = "data/cache/contracts.db"
