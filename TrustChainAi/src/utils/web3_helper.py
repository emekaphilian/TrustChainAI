"""Web3.py integration utilities with rate limiting, error handling, and multi-RPC fallback."""

import asyncio
import logging
import os
from typing import Optional, List
from web3 import Web3
from eth_keys.exceptions import BadSignature

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiter for RPC calls."""
    
    def __init__(self, calls_per_second: int = 100):
        """Initialize rate limiter.
        
        Args:
            calls_per_second: Max RPC calls per second (typical: 100).
        """
        self.calls_per_second = calls_per_second
        self.min_interval = 1.0 / calls_per_second
        self.last_call = 0.0
    
    async def __aenter__(self):
        """Async context manager for rate limiting."""
        elapsed = asyncio.get_event_loop().time() - self.last_call
        if elapsed < self.min_interval:
            await asyncio.sleep(self.min_interval - elapsed)
        self.last_call = asyncio.get_event_loop().time()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        pass


def validate_contract_address(address: str) -> bool:
    """Validate Ethereum contract address format.
    
    Args:
        address: Hex string with optional 0x prefix.
        
    Returns:
        True if valid checksummed address.
        
    Raises:
        ValueError: If not a valid Ethereum address.
    """
    if not address:
        raise ValueError("Address cannot be empty")
    
    try:
        # Web3.py validates format and checksum
        if Web3.is_address(address):
            return True
    except Exception as e:
        raise ValueError(f"Invalid address format: {e}")
    
    return False


def get_checksummed_address(address: str) -> str:
    """Convert address to checksummed format.
    
    Args:
        address: Raw address.
        
    Returns:
        Checksummed Ethereum address (0x...).
        
    Raises:
        ValueError: If address is invalid.
    """
    if not validate_contract_address(address):
        raise ValueError(f"Invalid address: {address}")
    
    return Web3.to_checksum_address(address)


class RpcManager:
    """Wrapper around Web3.py with multi-provider fallback, retry logic, and rate limiting."""
    
    def __init__(
        self, 
        rpc_endpoints: Optional[List[str]] = None,
        rate_limit: int = 100, 
        max_retries: int = 3,
        backoff_multiplier: float = 2.0
    ):
        """Initialize RPC manager with fallback support.
        
        Args:
            rpc_endpoints: List of RPC endpoint URLs (primary first).
                If None, loads from env: WEB3_RPC_ENDPOINT, WEB3_RPC_FALLBACK
            rate_limit: Max calls per second.
            max_retries: Max retry attempts per provider.
            backoff_multiplier: Exponential backoff multiplier (1s → 2s → 4s).
        """
        if rpc_endpoints is None:
            # Load from environment
            primary = os.getenv("WEB3_RPC_ENDPOINT", "https://mainnet.infura.io/v3/YOUR_KEY")
            fallback = os.getenv("WEB3_RPC_FALLBACK", "https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY")
            rpc_endpoints = [primary, fallback]
        
        self.rpc_endpoints = rpc_endpoints
        self.providers = [Web3(Web3.HTTPProvider(url)) for url in rpc_endpoints]
        self.rate_limiter = RateLimiter(rate_limit)
        self.max_retries = max_retries
        self.backoff_multiplier = backoff_multiplier
    
    async def get_code(self, address: str) -> Optional[str]:
        """Fetch contract bytecode with multi-provider fallback.
        
        Tries primary RPC first, then falls back to secondary providers.
        Each provider gets max_retries attempts with exponential backoff.
        
        Args:
            address: Contract address.
            
        Returns:
            Hex-encoded bytecode, or None if all providers fail.
        """
        checksummed = get_checksummed_address(address)
        
        # Try each provider in order
        for provider_idx, provider in enumerate(self.providers):
            provider_name = f"Provider-{provider_idx + 1}"
            
            for attempt in range(self.max_retries):
                try:
                    async with self.rate_limiter:
                        code = provider.eth.get_code(checksummed)
                        logger.info(
                            f"Fetched code for {checksummed} ({len(code)} bytes) "
                            f"via {provider_name}"
                        )
                        return code
                except Exception as e:
                    backoff = self.backoff_multiplier ** attempt
                    logger.warning(
                        f"RPC error from {provider_name} "
                        f"(attempt {attempt + 1}/{self.max_retries}): {e}. "
                        f"Retry in {backoff:.1f}s"
                    )
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(backoff)
            
            logger.warning(f"Provider-{provider_idx + 1} exhausted, trying next provider...")
        
        logger.error(
            f"Failed to fetch code for {checksummed} "
            f"after {len(self.providers)} providers × {self.max_retries} retries"
        )
        return None
    
    async def get_code_with_fallback(self, address: str) -> Optional[str]:
        """Alias for get_code() that makes fallback behavior explicit.
        
        Args:
            address: Contract address.
            
        Returns:
            Hex-encoded bytecode, or None if all providers fail.
        """
        return await self.get_code(address)
