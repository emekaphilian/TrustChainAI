from typing import Dict, List


class DetectionAgent:
    """
    Multi-vulnerability detection engine
    Uses AST-derived features to infer security risks
    """

    def analyze(self, features: Dict) -> List[Dict]:
        findings = []

        # -------------------------
        # REENTRANCY (SWC-107)
        # -------------------------
        if features.get("external_calls") and features.get("reentrancy"):
            findings.append({
                "type": "reentrancy",
                "swc_id": "SWC-107",
                "title": "Reentrancy",
                "description": "External call before state update",
                "confidence": 0.92
            })

        # -------------------------
        # ACCESS CONTROL (SWC-105)
        # -------------------------
        if features.get("access_control_issue"):
            findings.append({
                "type": "access_control",
                "swc_id": "SWC-105",
                "title": "Access Control",
                "description": "Missing or weak authorization checks",
                "confidence": 0.85
            })

        # -------------------------
        # UNCHECKED EXTERNAL CALL (SWC-104)
        # -------------------------
        if features.get("unchecked_calls"):
            findings.append({
                "type": "unchecked_external_call",
                "swc_id": "SWC-104",
                "title": "Unchecked Call",
                "description": "Return value of external call not verified",
                "confidence": 0.80
            })

        # -------------------------
        # WEAK RANDOMNESS (SWC-120)
        # -------------------------
        if features.get("weak_randomness"):
            findings.append({
                "type": "weak_randomness",
                "swc_id": "SWC-120",
                "title": "Weak Randomness",
                "description": "Block variables used as randomness source",
                "confidence": 0.75
            })

        # -------------------------
        # DOS / LOCKING RISK
        # -------------------------
        if features.get("dos_risk"):
            findings.append({
                "type": "denial_of_service",
                "swc_id": "SWC-128",
                "title": "Denial of Service",
                "description": "Contract can be locked or disrupted",
                "confidence": 0.70
            })

        # -------------------------
        # FALLBACK (NO DETECTION)
        # -------------------------
        if not findings:
            findings.append({
                "type": "none_detected",
                "swc_id": "N/A",
                "title": "No Critical Vulnerability",
                "description": "No strong exploit pattern detected",
                "confidence": 0.30
            })

        return findings