"""
Market Structure Analysis (Stub)

Placeholder for support/resistance, BOS/CHOCH, FVG detection.
"""

from pydantic import BaseModel
from typing import Optional


class StructureState(BaseModel):
    """Market structure state"""
    
    liquidity_sweep_detected: bool = False
    sr_rejection_detected: bool = False
    bos_detected: bool = False
    choch_detected: bool = False
    fvg_present: bool = False
    volume_expansion: bool = False
    
    def entry_model_ready(self) -> bool:
        """Check if all conditions met for entry
        
        Requires:
        - (sweep OR sr rejection)
        - (bos OR choch)
        - volume expansion
        - fvg present
        """
        sweep_or_rejection = self.liquidity_sweep_detected or self.sr_rejection_detected
        bos_or_choch = self.bos_detected or self.choch_detected
        
        return (
            sweep_or_rejection and
            bos_or_choch and
            self.volume_expansion and
            self.fvg_present
        )
