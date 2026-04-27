from ethics.engine import ethics_check
from typing import Dict, List, Any


class EthicsAgent:
    """
    Ethics evaluation agent.
    Evaluates contracts for ethical considerations and bias.
    """
    
    def __init__(self):
        self.history: List[Dict[str, Any]] = []
    
    def evaluate(self, contract: str) -> Dict[str, Any]:
        """
        Evaluate a contract for ethical considerations.
        
        Args:
            contract: Contract source code
            
        Returns:
            Ethics evaluation results
        """
        # Run ethics check (uses heuristic from ethics.engine)
        vulns = []  # Would be populated from detection
        result = ethics_check(vulns, contract)
        
        # Record in history
        self.history.append({
            "contract": contract[:50] + "..." if len(contract) > 50 else contract,
            "result": result
        })
        
        return result
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get evaluation history."""
        return self.history.copy()