"""Contract scanner - orchestrates blockchain retrieval and vulnerability detection."""

import asyncio
import logging
from typing import List, Optional
from dataclasses import dataclass

from src.utils.web3_helper import RpcManager, validate_contract_address
from src.utils.logging import audit_logger
from src.models.vulnerability_detector import VulnerabilityDetector
from src.models.bias_detector import BiasDetector
from src.models.types import Prediction

logger = logging.getLogger(__name__)


@dataclass
class ScanResult:
    """Result of scanning one or more contracts."""
    predictions: List[Prediction]
    scan_duration: float
    contracts_scanned: int
    errors: List[str]


class ContractScanner:
    """Orchestrates contract scanning with multi-RPC fallback and bias monitoring."""

    def __init__(
        self,
        rpc_manager: Optional[RpcManager] = None,
        vulnerability_detector: Optional[VulnerabilityDetector] = None,
        bias_detector: Optional[BiasDetector] = None,
        batch_size: int = 32
    ):
        """Initialize scanner with components.

        Args:
            rpc_manager: Web3 RPC manager (created if None)
            vulnerability_detector: ML model for vuln detection (created if None)
            bias_detector: Fairness monitor (created if None)
            batch_size: Contracts to process in parallel
        """
        self.rpc_manager = rpc_manager or RpcManager()
        self.vuln_detector = vulnerability_detector or VulnerabilityDetector()
        self.bias_detector = bias_detector or BiasDetector()
        self.batch_size = batch_size

    async def scan_contract(self, contract_address: str) -> Optional[Prediction]:
        """Scan a single contract for vulnerabilities.

        Args:
            contract_address: Ethereum contract address

        Returns:
            Prediction object or None if scan failed
        """
        try:
            # Validate address format
            if not validate_contract_address(contract_address):
                logger.error(f"Invalid contract address: {contract_address}")
                audit_logger.log_error("invalid_address", {"address": contract_address})
                return None

            # Fetch bytecode
            bytecode = await self.rpc_manager.get_code(contract_address)
            if bytecode is None:
                logger.error(f"Failed to fetch bytecode for {contract_address}")
                audit_logger.log_error("rpc_failure", {"address": contract_address})
                return None

            # Run vulnerability detection
            prediction = self.vuln_detector.predict(bytecode, contract_address)

            # Run bias detection (per-scan)
            self.bias_detector.analyze_prediction(prediction)

            # Log successful scan
            audit_logger.log_scan(
                contract_address=contract_address,
                vulns_found=len(prediction.vulnerabilities),
                risk_score=prediction.risk_score,
                contract_type=prediction.contract_type,
                model_version=prediction.model_version
            )

            logger.info(f"Scanned {contract_address}: {len(prediction.vulnerabilities)} vulns, risk={prediction.risk_score:.2f}")
            return prediction

        except Exception as e:
            logger.error(f"Scan failed for {contract_address}: {e}")
            audit_logger.log_error("scan_failure", {"address": contract_address, "error": str(e)})
            return None

    async def scan_contracts_batch(self, contract_addresses: List[str]) -> ScanResult:
        """Scan multiple contracts in parallel batches.

        Args:
            contract_addresses: List of contract addresses to scan

        Returns:
            ScanResult with all predictions and metadata
        """
        import time
        start_time = time.time()

        predictions = []
        errors = []

        # Process in batches to avoid overwhelming RPC providers
        for i in range(0, len(contract_addresses), self.batch_size):
            batch = contract_addresses[i:i + self.batch_size]
            logger.info(f"Processing batch {i//self.batch_size + 1}: {len(batch)} contracts")

            # Scan contracts in parallel
            tasks = [self.scan_contract(addr) for addr in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            # Collect results
            for addr, result in zip(batch, batch_results):
                if isinstance(result, Exception):
                    errors.append(f"{addr}: {str(result)}")
                    logger.error(f"Batch scan error for {addr}: {result}")
                elif result is not None:
                    predictions.append(result)
                else:
                    errors.append(f"{addr}: scan returned None")

        duration = time.time() - start_time
        contracts_scanned = len(predictions) + len(errors)

        logger.info(f"Batch scan complete: {len(predictions)} successful, {len(errors)} errors, {duration:.1f}s")

        return ScanResult(
            predictions=predictions,
            scan_duration=duration,
            contracts_scanned=contracts_scanned,
            errors=errors
        )

    def scan_contract_sync(self, contract_address: str) -> Optional[Prediction]:
        """Synchronous wrapper for single contract scan.

        Args:
            contract_address: Contract address to scan

        Returns:
            Prediction or None
        """
        # Run async function in new event loop
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(self.scan_contract(contract_address))
        finally:
            loop.close()

    def scan_contracts_sync(self, contract_addresses: List[str]) -> ScanResult:
        """Synchronous wrapper for batch scanning.

        Args:
            contract_addresses: List of addresses to scan

        Returns:
            ScanResult
        """
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(self.scan_contracts_batch(contract_addresses))
        finally:
            loop.close()


# CLI entry point for standalone scanning
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Scan Ethereum contracts for vulnerabilities")
    parser.add_argument("--contract", help="Single contract address to scan")
    parser.add_argument("--batch-file", help="File with contract addresses (one per line)")
    parser.add_argument("--output", default="results/scan_results.json", help="Output file for results")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size for parallel scanning")

    args = parser.parse_args()

    scanner = ContractScanner(batch_size=args.batch_size)

    if args.contract:
        # Single contract scan
        result = scanner.scan_contract_sync(args.contract)
        if result:
            print(f"Scan result: {len(result.vulnerabilities)} vulnerabilities, risk={result.risk_score:.2f}")
        else:
            print("Scan failed")

    elif args.batch_file:
        # Batch scan from file
        with open(args.batch_file, 'r') as f:
            addresses = [line.strip() for line in f if line.strip()]

        print(f"Scanning {len(addresses)} contracts...")
        result = scanner.scan_contracts_sync(addresses)

        print(f"Completed: {len(result.predictions)} successful, {len(result.errors)} errors")
        print(".1f")

        # Save results
        import json
        output_data = {
            "predictions": [p.__dict__ for p in result.predictions],
            "errors": result.errors,
            "metadata": {
                "contracts_scanned": result.contracts_scanned,
                "scan_duration": result.scan_duration
            }
        }

        with open(args.output, 'w') as f:
            json.dump(output_data, f, indent=2, default=str)
        print(f"Results saved to {args.output}")

    else:
        parser.print_help()