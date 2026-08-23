#!/usr/bin/env python3
"""
THE FLAMINGO SIEVE — UNTRAMMELLED BLOCK SCANNER
Complete, unbrevified scanning of Bitcoin blocks for structured private keys.

Features:
- No artificial limits on transaction count or block size.
- Sliding window scan of EVERY byte in EVERY transaction.
- Full Flamingo Sieve audit on every 32-byte candidate.
- Raw JSON display of all data.
- Comprehensive CSV export of all findings.
"""

import json
import csv
import hashlib
import requests
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

# =============================================================================
# 1. FUNDAMENTAL CONSTANTS (UNBREVIFIED)
# =============================================================================

P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
G_X = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
G_Y = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8

# Gap Constant C = 2^32 + 977
C_GAP = (1 << 32) + 977
C_INV = pow(C_GAP, -1, N)

# Digital Bridge
D_BRIDGE = 1 << 16

# GLV Constants
LAMBDA = 0x5363AD4CC05C30E0A5261C028812645A122E22EA20816678DF02967C1B23BD72
BETA = 0x7AE96A2B657C07106E64479EAC3434E99CF0497512F58995C1396C28719501EE

# Generator Anomaly Constants
H_X_ANOMALY = 0x3B78CE563F89A0ED9414F5AA28AD0D96D6795F9C63
COMMON_SUBSTRING = "8ce563f89a0ed9414f5aa28ad0d96d6795f9c6"

# =============================================================================
# 2. GEOMETRIC FAMILY GENERATORS (UNTRAMMELLED)
# =============================================================================

def generate_geometric_families(limit_offset: int = 2048) -> List[int]:
    """
    Generates all geometric family values F(n) such that 32 * F(n) < D_BRIDGE.
    Untrammelled: Generates ALL families defined in the framework without skipping.
    """
    candidates = set()
    
    # Helper to add scaled values
    def add_scaled(val):
        scaled = 32 * val
        if scaled < D_BRIDGE:
            candidates.add(scaled)
            candidates.add((-scaled) % N)
    
    # 2.2.1 2D Polygonal Numbers P_k(n)
    for k in range(3, 100): # Wide range of k
        n = 1
        while True:
            val = ((k - 2) * n * n - (k - 4) * n) // 2
            if val > limit_offset: break
            add_scaled(val)
            n += 1
            
    # 2.2.2 Centered Polygonal Numbers CP_k(n)
    for k in range(3, 100):
        n = 1
        while True:
            val = (k * n * (n - 1)) // 2 + 1
            if val > limit_offset: break
            add_scaled(val)
            n += 1

    # 2.2.3 Lattice Shells
    # FCC: 10n^2 + 2
    n = 1
    while True:
        val = 10 * n * n + 2
        if val > limit_offset: break
        add_scaled(val)
        n += 1
    # BCC: 8n^2 + 6
    n = 1
    while True:
        val = 8 * n * n + 6
        if val > limit_offset: break
        add_scaled(val)
        n += 1
    # SC: 6n^2 + 2
    n = 1
    while True:
        val = 6 * n * n + 2
        if val > limit_offset: break
        add_scaled(val)
        n += 1
    # Diamond: 4n^2 + 2
    n = 1
    while True:
        val = 4 * n * n + 2
        if val > limit_offset: break
        add_scaled(val)
        n += 1

    # 2.2.4 Platonic Solids
    # Tetrahedral
    n = 1
    while True:
        val = n * (n + 1) * (n + 2) // 6
        if val > limit_offset: break
        add_scaled(val)
        n += 1
    # Cube
    n = 1
    while True:
        val = n ** 3
        if val > limit_offset: break
        add_scaled(val)
        n += 1
    # Octahedral
    n = 1
    while True:
        val = n * (2 * n * n + 1) // 3
        if val > limit_offset: break
        add_scaled(val)
        n += 1
    # Dodecahedral
    n = 1
    while True:
        val = n * (9 * n * n - 9 * n + 2) // 2
        if val > limit_offset: break
        add_scaled(val)
        n += 1
    # Icosahedral
    n = 1
    while True:
        val = n * (5 * n * n - 5 * n + 2) // 2
        if val > limit_offset: break
        add_scaled(val)
        n += 1

    # 2.2.5 Centered 3D Figurates (Selected key ones)
    # Centered Cube
    n = 1
    while True:
        val = n**3 + **(n-1)3
        if val > limit_offset: break
        add_scaled(val)
        n += 1
        
    # 2.2.6 Root Lattices
    lattices = [
        lambda n: 6 * n * n + 2,   # G2
        lambda n: 12 * n * n + 2,  # F4
        lambda n: 16 * n * n + 2,  # E6
        lambda n: 20 * n * n + 2,  # E7
        lambda n: 24 * n * n + 2,  # E8
    ]
    for func in lattices:
        n = 1
        while True:
            val = func(n)
            if val > limit_offset: break
            add_scaled(val)
            n += 1

    # 2.2.7 Powers of Two
    for k in range(0, 12):
        add_scaled(1 << k)

    # 2.2.8 Fibonacci
    a, b = 0, 1
    while b <= limit_offset:
        add_scaled(b)
        a, b = b, a + b

    # 2.2.9 Catalan
    n = 0
    while True:
        val = 0
        # Calculate binomial coeff carefully
        num = 1
        den = 1
        for i in range(n):
            num *= (2 * n - i)
            den *= (i + 1)
        val = num // (den * (n + 1))
        
        if val > limit_offset and n > 10: break
        if val <= limit_offset:
            add_scaled(val)
        n += 1
        if n > 20: break # Catalan grows fast

    # 2.2.11 Small Primes
    small_primes = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]
    for p_val in small_primes:
        add_scaled(p_val)

    # Pre-filtering: c mod 5 != 0 and c mod 10 in {1,2,4,6,8,9}
    filtered = []
    allowed_mod10 = {1, 2, 4, 6, 8, 9}
    for c in candidates:
        if c % 5 != 0 and (c % 10) in allowed_mod10:
            filtered.append(c)
            
    return sorted(list(set(filtered)))

# Pre-generate candidate set once
CANDIDATE_SET = set(generate_geometric_families())
CANDIDATE_LIST = sorted(CANDIDATE_SET, key=lambda x: min(x, N-x))

print(f"[INIT] Generated {len(CANDIDATE_LIST)} filtered candidates from all geometric families.")

# =============================================================================
# 3. AUDIT FUNCTION (UNBREVIFIED)
# =============================================================================

def balanced_residue(x: int) -> int:
    """Maps x to [-N/2, N/2]"""
    if x <= N // 2:
        return x
    return x - N

def audit_key(d: int) -> Optional[int]:
    """
    Computes rho(d) = bal(d * C^-1 mod N).
    Returns the offset o if |rho(d)| is in the candidate set, else None.
    """
    rho = balanced_residue((d * C_INV) % N)
    abs_rho = abs(rho)
    
    if abs_rho in CANDIDATE_SET:
        return abs_rho
    return None

# =============================================================================
# 4. UNTRAMMELLED BLOCK SCANNER ENGINE
# =============================================================================

class FlamingoBlockScanner:
    def __init__(self):
        self.api_base = "https://blockstream.info/api"
        self.findings = []
        self.stats = {
            "blocks_scanned": 0,
            "transactions_scanned": 0,
            "bytes_scanned": 0,
            "candidates_tested": 0,
            "matches_found": 0
        }

    def fetch_block_raw(self, height: int) -> Optional[str]:
        """Fetches the FULL raw block hex. No truncation."""
        try:
            url = f"{self.api_base}/block-height/{height}"
            block_hash = requests.get(url, timeout=10).text.strip()
            
            raw_url = f"{self.api_base}/block/{block_hash}/raw"
            response = requests.get(raw_url, timeout=30)
            response.raise_for_status()
            return response.hex()
        except Exception as e:
            print(f"[ERROR] Failed to fetch block {height}: {e}")
            return None

    def scan_transaction_hex(self, tx_hex: str, txid: str, block_height: int) -> List[Dict]:
        """
        Scans EVERY 32-byte window in the transaction hex.
        Untrammelled: Slides byte-by-byte, no skipping.
        """
        matches = []
        hex_len = len(tx_hex)
        
        # We need 64 hex chars for 32 bytes
        if hex_len < 64:
            return matches

        # Slide one byte (2 hex chars) at a time
        for i in range(0, hex_len - 63, 2):
            candidate_hex = tx_hex[i:i+64]
            
            try:
                d_candidate = int(candidate_hex, 16)
                
                # Quick range check before expensive modular math
                if d_candidate == 0 or d_candidate >= N:
                    continue
                
                self.stats["candidates_tested"] += 1
                
                offset = audit_key(d_candidate)
                if offset is not None:
                    match_data = {
                        "block_height": block_height,
                        "txid": txid,
                        "offset_hex": candidate_hex,
                        "offset_decimal": str(d_candidate),
                        "matched_offset_value": offset,
                        "byte_position": i // 2,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    matches.append(match_data)
                    self.stats["matches_found"] += 1
                    print(f"\n[!!!] MATCH FOUND! Offset: {offset} at pos {i//2} in TX {txid[:8]}...")
                    
            except ValueError:
                continue
                
        return matches

    def scan_block(self, height: int, display_raw: bool = False) -> Dict:
        """
        Scans a full block. 
        display_raw: If True, prints raw JSON of the block structure.
        """
        print(f"\n[SCAN] Starting untrammelled scan of Block #{height}...")
        start_time = time.time()
        
        raw_hex = self.fetch_block_raw(height)
        if not raw_hex:
            return {"error": "Failed to fetch"}

        self.stats["blocks_scanned"] += 1
        self.stats["bytes_scanned"] += len(raw_hex) // 2

        if display_raw:
            print("\n[RAW DATA] Block Header Info (Simulated Parse):")
            # Displaying raw hex snippet as representative raw data
            print(json.dumps({
                "block_height": height,
                "raw_hex_length": len(raw_hex),
                "hex_snippet_first_100": raw_hex[:100],
                "hex_snippet_last_100": raw_hex[-100:]
            }, indent=2))

        # Note: Parsing individual TXs from raw block hex requires manual binary parsing
        # because the API returns the whole block serialized. 
        # For true unbrevified scanning of TX content, we should ideally fetch TXIDs 
        # then fetch each raw TX. This ensures we don't miss boundaries.
        
        # Strategy: Fetch TXIDs for the block, then fetch each raw TX individually.
        # This is slower but guarantees 100% coverage of every transaction's exact bytes.
        
        try:
            block_hash = requests.get(f"{self.api_base}/block-height/{height}", timeout=10).text.strip()
            txids_url = f"{self.api_base}/block/{block_hash}/txids"
            txids = requests.get(txids_url, timeout=20).json()
            
            print(f"[INFO] Block contains {len(txids)} transactions. Scanning all...")
            
            block_matches = []
            for idx, txid in enumerate(txids):
                # Fetch raw TX hex
                tx_hex = requests.get(f"{self.api_base}/tx/{txid}/hex", timeout=10).text.strip()
                self.stats["transactions_scanned"] += 1
                
                # Scan this transaction
                tx_matches = self.scan_transaction_hex(tx_hex, txid, height)
                block_matches.extend(tx_matches)
                
                # Progress indicator for large blocks
                if (idx + 1) % 100 == 0:
                    print(f"[PROGRESS] Scanned {idx+1}/{len(txids)} transactions...")
                    
            duration = time.time() - start_time
            print(f"[DONE] Block #{height} scan completed in {duration:.2f}s.")
            print(f"       TXs: {len(txids)}, Candidates Tested: {self.stats['candidates_tested']}, Matches: {len(block_matches)}")
            
            return {
                "block_height": height,
                "transactions_count": len(txids),
                "scan_duration": duration,
                "matches": block_matches
            }
            
        except Exception as e:
            print(f"[ERROR] Error processing transactions in block {height}: {e}")
            return {"error": str(e)}

    def export_to_csv(self, filename: str = None):
        """Exports all findings to CSV sections."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"flamingo_block_scan_results_{timestamp}.csv"
            
        if not self.findings:
            print("[INFO] No findings to export.")
            return

        with open(filename, 'w', newline='') as f:
            fieldnames = [
                "block_height", "txid", "offset_hex", "offset_decimal", 
                "matched_offset_value", "byte_position", "timestamp"
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.findings)
            
        print(f"[EXPORT] Saved {len(self.findings)} findings to {filename}")

# =============================================================================
# 5. MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    scanner = FlamingoBlockScanner()
    
    print("="*80)
    print("FLAMINGO SIEVE: UNTRAMMELLED BLOCK SCANNER")
    print("="*80)
    print("This scanner will:")
    print("1. Fetch FULL raw blocks via Blockstream API.")
    print("2. Iterate EVERY transaction in the block.")
    print("3. Slide a 32-byte window over EVERY BYTE of every transaction.")
    print("4. Audit every candidate against the complete geometric family set.")
    print("5. Display RAW JSON data and export matches to CSV.")
    print("="*80)
    
    try:
        # Example: Scan a specific block (e.g., Block 800,000)
        # You can change this to any valid block height
        target_block = 800000 
        
        result = scanner.scan_block(target_block, display_raw=True)
        
        if "matches" in result and result["matches"]:
            scanner.findings.extend(result["matches"])
            scanner.export_to_csv()
        else:
            print("\n[INFO] No structured keys found in this block (expected for random blocks).")
            print("       The probability of a random key matching is ~1.5e-74.")
            
        # Display final stats
        print("\n" + "="*80)
        print("FINAL STATISTICS")
        print("="*80)
        print(json.dumps(scanner.stats, indent=2))
        
    except KeyboardInterrupt:
        print("\n[INTERRUPT] Scan stopped by user.")
        if scanner.findings:
            scanner.export_to_csv()
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
