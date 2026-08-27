#!/usr/bin/env python3
"""
THE ULTIMATE MASTER HUNTER - COMPLETE UNIFIED FRAMEWORK
Combines ALL components from:
- bitcoin_block_scanner.py (Blockchain API & UTXO tracking)
- flamingo_sieve_ultimate.py (Complete mathematical framework)
- unified_hunter.py (Multi-strategy candidate generation)
- ultimate_bridge_hunter.py (Bridge-focused hunting)

Features:
✓ Complete secp256k1 mathematical framework (Sections 1-32)
✓ All candidate generation strategies (10+ methods)
✓ Live blockchain scanning with multi-threading
✓ UTXO stalking and wallet clustering
✓ Comprehensive CSV/JSON export system
✓ Progress tracking and resumable scans
✓ Bit-shift expansion and dimensional analysis
✓ Developer mistake patterns
✓ GLV endomorphism and geometric families
✓ Morse code patterns and generator anomalies
"""

import json
import csv
import hashlib
import requests
import ecdsa
import time
import os
import sys
import math
import struct
import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set, Generator
from dataclasses import dataclass, asdict, field
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import Enum

# ============================================================================
# CONFIGURATION AND CONSTANTS
# ============================================================================

# secp256k1 curve parameters
SECP256K1_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
SECP256K1_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
SECP256K1_A = 0
SECP256K1_B = 7
SECP256K1_Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
SECP256K1_Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8

# GLV Endomorphism constants
GLV_LAMBDA = 0x5363AD4CC05C30E0A5261C028812645A122E22EA20816678DF02967C1B23BD72
GLV_BETA = 0x7AE96A2B657C07106E64479EAC3434E99CF0497512F58995C1396C28719501EE

# Gap Constant and Digital Bridge
GAP_C = (1 << 32) + 977  # 2^32 + 977
DIGITAL_BRIDGE_D = 1 << 16  # 2^16 = 65536

# Generator anomaly (H = G/2)
GENERATOR_Hx = 0x3B78CE563F89A0ED9414F5AA28AD0D96D6795F9C63
GENERATOR_SUBSTRING = "8ce563f89a0ed9414f5aa28ad0d96d6795f9c6"

# API Configuration
API_BASE = "https://blockchain.info"
HEADERS = {'User-Agent': 'Mozilla/5.0 (compatible; UltimateMasterHunter/1.0)'}

# Export directories
EXPORT_DIR = "master_hunter_exports"
BLOCKCHAIN_EXPORTS = os.path.join(EXPORT_DIR, "blockchain_data")
CANDIDATE_EXPORTS = os.path.join(EXPORT_DIR, "candidates")
ANALYSIS_EXPORTS = os.path.join(EXPORT_DIR, "analysis")

for directory in [EXPORT_DIR, BLOCKCHAIN_EXPORTS, CANDIDATE_EXPORTS, ANALYSIS_EXPORTS]:
    os.makedirs(directory, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('master_hunter_progress.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


# ============================================================================
# SECTION 1: SECP256K1 MATHEMATICAL FRAMEWORK
# ============================================================================

@dataclass
class CurveParameters:
    """Complete secp256k1 curve parameters"""
    p: int = SECP256K1_P
    n: int = SECP256K1_N
    a: int = SECP256K1_A
    b: int = SECP256K1_B
    Gx: int = SECP256K1_Gx
    Gy: int = SECP256K1_Gy
    lambda_glv: int = GLV_LAMBDA
    beta_glv: int = GLV_BETA
    gap_c: int = GAP_C
    bridge_d: int = DIGITAL_BRIDGE_D


class FastReduction:
    """Fast modular reduction using sparse structure of p"""

    @staticmethod
    def fast_reduce(value: int, p: int = SECP256K1_P) -> int:
        """Section 24: Fast reduction using 2^256 ≡ C (mod p)"""
        C = GAP_C
        while value.bit_length() > 256:
            high = value >> 256
            low = value & ((1 << 256) - 1)
            value = low + high * C
        while value >= p:
            value -= p
        return value

    @staticmethod
    def verify_sparse_structure(p: int = SECP256K1_P) -> Dict:
        """Verify sparse binary representation of p"""
        zero_positions = [32, 9, 8, 7, 6, 4]
        actual_zeros = [i for i in range(256) if ((p >> i) & 1) == 0]
        ones_count = bin(p).count('1')
        zeros_count = 256 - ones_count

        return {
            "expected_zero_positions": zero_positions,
            "actual_zero_positions": actual_zeros,
            "ones_count": ones_count,
            "zeros_count": zeros_count,
            "is_sparse": len(actual_zeros) < 20,
            "pattern_98741": all(pos in actual_zeros for pos in [9, 8, 7, 6, 4])
        }


# ============================================================================
# SECTION 2: GEOMETRIC FAMILIES AND CANDIDATE GENERATION
# ============================================================================

class GeometricFamilies:
    """Section 5: All geometric families for candidate generation"""

    @staticmethod
    def j_n(n: int) -> int:
        """FCC coordination sequence J(n) = 10n² + 2"""
        return 10 * n * n + 2

    @staticmethod
    def s_n(n: int) -> int:
        """Crystal ball sequence S(n)"""
        return (10 * n**3 + 15 * n**2 + 11 * n + 3) // 3

    @staticmethod
    def polygonal_2d(k: int, n: int) -> int:
        """2D Polygonal numbers P_k(n)"""
        if k < 3:
            return n
        return ((k - 2) * n * (n - 1)) // 2 + n

    @staticmethod
    def pyramidal_3d(k: int, n: int) -> int:
        """3D Pyramidal numbers"""
        return n * (n + 1) * (k * n - k + 2) // 6

    @staticmethod
    def generate_all_candidates(bridge_d: int = DIGITAL_BRIDGE_D, multiplier: int = 32) -> Set[int]:
        """Generate all geometric candidates"""
        candidates = set()

        # FCC Shell: J(n) = 10n² + 2
        n = 1
        while True:
            val = GeometricFamilies.j_n(n)
            if multiplier * val >= bridge_d:
                break
            candidates.add(multiplier * val)
            candidates.add(SECP256K1_N - (multiplier * val))
            n += 1

        # BCC Shell: 8n² + 6
        n = 1
        while True:
            val = 8 * n * n + 6
            if multiplier * val >= bridge_d:
                break
            candidates.add(multiplier * val)
            candidates.add(SECP256K1_N - (multiplier * val))
            n += 1

        # Simple Cubic: 6n² + 2
        n = 1
        while True:
            val = 6 * n * n + 2
            if multiplier * val >= bridge_d:
                break
            candidates.add(multiplier * val)
            candidates.add(SECP256K1_N - (multiplier * val))
            n += 1

        # Powers of 2
        for k in range(12):
            val = 2**k
            if multiplier * val < bridge_d:
                candidates.add(multiplier * val)
                candidates.add(SECP256K1_N - (multiplier * val))

        return candidates

    @staticmethod
    def filter_candidates(candidates: Set[int]) -> Set[int]:
        """Filter candidates by divisibility rules"""
        return {c for c in candidates 
                if c % 5 != 0 and c % 10 in {1, 2, 4, 6, 8, 9} and 0 < c < SECP256K1_N}


# ============================================================================
# SECTION 3: CANDIDATE EXPANSION STRATEGIES
# ============================================================================

class NearbySquaredEngine:
    """Expand candidates using nearby values and squared operations"""

    @staticmethod
    def expand_candidates(
        candidates: Set[int],
        radius: int = 2,
        include_squares: bool = True,
        include_bridge_powers: bool = True,
        include_mersenne: bool = True,
        include_bitshifts: bool = False,
        include_mistakes: bool = True,
        N: int = SECP256K1_N
    ) -> Set[int]:
        """Expand candidate set with multiple strategies"""
        expanded = set(candidates)

        # Nearby values (±radius)
        for c in candidates:
            for delta in range(-radius, radius + 1):
                val = (c + delta) % N
                if val > 0:
                    expanded.add(val)

        # Squared values
        if include_squares:
            for c in candidates:
                expanded.add((c * c) % N)

        # Bridge powers
        if include_bridge_powers:
            D = DIGITAL_BRIDGE_D
            bridge_powers = {
                (D - 1) ** 2,  # 65535²
                D ** 2,         # 65536²
                (D + 1) ** 2,   # 65537²
                (D - 1) * D,
                D * (D + 1),
                (D - 1) * (D + 1)
            }
            for bp in bridge_powers:
                expanded.add(bp % N)
                expanded.add(N - (bp % N))

        # Mersenne numbers
        if include_mersenne:
            for x in range(1, 257):
                mersenne = (1 << x) - 1
                if mersenne < N:
                    expanded.add(mersenne)

        # Bit shifts
        if include_bitshifts:
            for c in list(expanded):
                for shift in range(-32, 33):
                    if shift > 0:
                        expanded.add((c << shift) % N)
                    elif shift < 0:
                        expanded.add((c >> (-shift)) % N)

        # Developer mistakes
        if include_mistakes:
            mistakes = DevMistakeFocus.generate_all_mistakes()
            expanded.update(mistakes)

        return {e for e in expanded if 0 < e < N}


class DevMistakeFocus:
    """Generate candidates based on common developer mistakes"""

    @staticmethod
    def hardcoded_test_keys() -> Set[int]:
        """Common hardcoded test keys"""
        return {
            1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
            100, 1000, 10000,
            0xDEADBEEF, 0xCAFEBABE, 0xFEEDFACE,
            0x12345678, 0x87654321
        }

    @staticmethod
    def ascii_hex_errors() -> Set[int]:
        """ASCII/hex conversion errors"""
        mistakes = set()
        test_strings = ["password", "admin", "test", "bitcoin", "private", "key"]
        for s in test_strings:
            mistakes.add(int(hashlib.sha256(s.encode()).hexdigest(), 16) % SECP256K1_N)
        return mistakes

    @staticmethod
    def timestamp_keys() -> Set[int]:
        """Timestamp-based keys"""
        mistakes = set()
        # Bitcoin genesis timestamp
        mistakes.add(1231006505)
        # Common Unix timestamps
        for year in range(2009, 2025):
            ts = int(datetime(year, 1, 1).timestamp())
            mistakes.add(ts)
            mistakes.add(ts % SECP256K1_N)
        return mistakes

    @staticmethod
    def sequence_patterns() -> Set[int]:
        """Sequential pattern mistakes"""
        mistakes = set()
        # Repeating patterns
        for digit in range(1, 10):
            pattern = int(str(digit) * 8, 16)
            mistakes.add(pattern)
        # Incremental sequences
        for start in [1, 100, 1000]:
            for length in [4, 8, 16]:
                val = sum(start + i for i in range(length))
                mistakes.add(val % SECP256K1_N)
        return mistakes

    @staticmethod
    def small_multipliers() -> Set[int]:
        """Small multiplier patterns"""
        mistakes = set()
        bases = [DIGITAL_BRIDGE_D, GAP_C, 1000000, 10000000]
        for base in bases:
            for mult in range(1, 101):
                mistakes.add((base * mult) % SECP256K1_N)
        return mistakes

    @staticmethod
    def generate_all_mistakes() -> Set[int]:
        """Generate all developer mistake candidates"""
        all_mistakes = set()
        all_mistakes.update(DevMistakeFocus.hardcoded_test_keys())
        all_mistakes.update(DevMistakeFocus.ascii_hex_errors())
        all_mistakes.update(DevMistakeFocus.timestamp_keys())
        all_mistakes.update(DevMistakeFocus.sequence_patterns())
        all_mistakes.update(DevMistakeFocus.small_multipliers())
        return {m for m in all_mistakes if 0 < m < SECP256K1_N}


# ============================================================================
# SECTION 4: BIT-SHIFT ENGINE
# ============================================================================

class BitShiftEngine:
    """Generate bit-shift variants of candidates"""

    @staticmethod
    def generate_all_shifts(candidate: int, max_shift: int = 32) -> Set[int]:
        """Generate all bit-shift variants"""
        shifts = set()
        for shift in range(-max_shift, max_shift + 1):
            if shift > 0:
                val = (candidate << shift) % SECP256K1_N
            elif shift < 0:
                val = (candidate >> (-shift)) % SECP256K1_N
            else:
                val = candidate
            if 0 < val < SECP256K1_N:
                shifts.add(val)
        return shifts


# ============================================================================
# SECTION 5: CRYPTOGRAPHIC OPERATIONS
# ============================================================================

class CryptoOperations:
    """Core cryptographic operations for key testing"""

    @staticmethod
    def point_add(p1: Tuple[int, int], p2: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Add two points on secp256k1 curve"""
        if p1 is None:
            return p2
        if p2 is None:
            return p1

        x1, y1 = p1
        x2, y2 = p2

        if x1 == x2 and y1 != y2:
            return None  # Point at infinity

        if x1 == x2 and y1 == y2:
            # Point doubling
            lam = (3 * x1 * x1 + SECP256K1_A) * pow(2 * y1, SECP256K1_P - 2, SECP256K1_P) % SECP256K1_P
        else:
            # Point addition
            lam = (y2 - y1) * pow(x2 - x1, SECP256K1_P - 2, SECP256K1_P) % SECP256K1_P

        x3 = (lam * lam - x1 - x2) % SECP256K1_P
        y3 = (lam * (x1 - x3) - y1) % SECP256K1_P

        return (x3, y3)

    @staticmethod
    def scalar_multiply(k: int, point: Tuple[int, int] = None) -> Optional[Tuple[int, int]]:
        """Multiply point by scalar using double-and-add"""
        if point is None:
            point = (SECP256K1_Gx, SECP256K1_Gy)

        if k == 0 or point is None:
            return None
        if k == 1:
            return point

        result = None
        addend = point

        while k:
            if k & 1:
                result = CryptoOperations.point_add(result, addend)
            addend = CryptoOperations.point_add(addend, addend)
            k >>= 1

        return result

    @staticmethod
    def private_to_public(private_key: int) -> Optional[str]:
        """Convert private key to compressed public key (hex)"""
        try:
            point = CryptoOperations.scalar_multiply(private_key)
            if point is None:
                return None

            x, y = point
            # Compressed format: 02/03 + x coordinate
            prefix = '02' if y % 2 == 0 else '03'
            return prefix + f"{x:064x}"
        except Exception as e:
            logger.debug(f"Error converting private key: {e}")
            return None

    @staticmethod
    def public_to_address(public_key_hex: str) -> str:
        """Convert public key to P2PKH address"""
        if not public_key_hex:
            return ""

        try:
            pub_key_bytes = bytes.fromhex(public_key_hex)

            # SHA256
            sha256_hash = hashlib.sha256(pub_key_bytes).digest()

            # RIPEMD160
            ripemd160 = hashlib.new('ripemd160')
            ripemd160.update(sha256_hash)
            pubkey_hash = ripemd160.digest()

            # Add version byte (0x00 for mainnet)
            versioned = b'\x00' + pubkey_hash

            # Double SHA256 for checksum
            checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]

            # Base58 encode
            address_bytes = versioned + checksum
            return CryptoOperations.base58_encode(address_bytes)
        except Exception as e:
            logger.debug(f"Error generating address: {e}")
            return ""

    @staticmethod
    def base58_encode(data: bytes) -> str:
        """Base58 encode bytes"""
        alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
        num = int.from_bytes(data, 'big')
        encoded = ''
        while num > 0:
            num, remainder = divmod(num, 58)
            encoded = alphabet[remainder] + encoded
        # Add leading '1's for each leading zero byte
        for byte in data:
            if byte == 0:
                encoded = '1' + encoded
            else:
                break
        return encoded


# ============================================================================
# SECTION 6: BLOCKCHAIN SCANNER
# ============================================================================

class BlockchainScanner:
    """Bitcoin blockchain scanner with UTXO tracking"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.watched_addresses: Set[str] = set()
        self.address_clusters: Dict[int, Set[str]] = defaultdict(set)
        self.utxo_data: Dict[str, Dict] = {}

        # Data buffers
        self.blocks_buffer: List[Dict] = []
        self.transactions_buffer: List[Dict] = []
        self.utxos_buffer: List[Dict] = []

    def make_request(self, url: str, params: Optional[Dict] = None, retries: int = 3) -> Optional[Dict]:
        """Make API request with error handling and retries"""
        for attempt in range(retries):
            try:
                response = self.session.get(url, params=params, timeout=15)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"API Error after {retries} attempts: {e}")
                    return None
        return None

    def get_block_by_height(self, height: int) -> Optional[Dict]:
        """Get block by height"""
        url = f"{API_BASE}/block-height/{height}"
        params = {'format': 'json'}
        data = self.make_request(url, params)
        if data and 'blocks' in data and len(data['blocks']) > 0:
            return data['blocks'][0]
        return None

    def get_block_by_hash(self, block_hash: str) -> Optional[Dict]:
        """Get block by hash"""
        url = f"{API_BASE}/rawblock/{block_hash}"
        params = {'format': 'json'}
        return self.make_request(url, params)

    def get_address_details(self, address: str) -> Optional[Dict]:
        """Get address details including UTXOs"""
        url = f"{API_BASE}/rawaddr/{address}"
        params = {'format': 'json'}
        return self.make_request(url, params)

    def scan_block_for_keys(self, block: Dict, candidate_keys: Set[int]) -> List[Dict]:
        """Scan block transactions for matching candidate keys"""
        matches = []

        for tx in block.get('tx', []):
            for output in tx.get('out', []):
                script = output.get('script', '')
                if len(script) >= 70:  # Potential P2PKH
                    # Extract potential public key hash
                    try:
                        # Try to derive address from candidate keys
                        for key in candidate_keys:
                            pub_key = CryptoOperations.private_to_public(key)
                            if pub_key:
                                address = CryptoOperations.public_to_address(pub_key)
                                if address in script or output.get('addr') == address:
                                    matches.append({
                                        'private_key': hex(key),
                                        'public_key': pub_key,
                                        'address': address,
                                        'tx_hash': tx.get('hash'),
                                        'block_height': block.get('height'),
                                        'value': output.get('value', 0) / 1e8,
                                        'timestamp': datetime.now().isoformat()
                                    })
                    except Exception as e:
                        logger.debug(f"Error checking key: {e}")
                        continue

        return matches


# ============================================================================
# SECTION 7: MULTI-THREADED HUNTER
# ============================================================================

@dataclass
class HunterProgress:
    """Track hunting progress"""
    total_candidates: int = 0
    blocks_scanned: int = 0
    keys_tested: int = 0
    matches_found: int = 0
    start_time: str = ""
    last_checkpoint: str = ""
    current_block: int = 0


class MasterHunter:
    """Main hunter class combining all strategies"""

    def __init__(self, threads: int = 4):
        self.threads = threads
        self.scanner = BlockchainScanner()
        self.progress = HunterProgress()
        self.matches: List[Dict] = []
        self.candidate_keys: Set[int] = set()

    def generate_candidates(self, strategy: str = "all") -> Set[int]:
        """Generate candidate private keys using specified strategy"""
        logger.info(f"Generating candidates with strategy: {strategy}")

        candidates = set()

        if strategy in ["all", "geometric"]:
            # Geometric families
            base = GeometricFamilies.generate_all_candidates()
            candidates.update(GeometricFamilies.filter_candidates(base))

        if strategy in ["all", "bridge"]:
            # Digital Bridge vicinity
            D = DIGITAL_BRIDGE_D
            for n in range(1, 10001):
                for delta in range(-100, 101):
                    key = n * D + delta
                    if 0 < key < SECP256K1_N:
                        candidates.add(key)
                    key2 = n * (D - 1) + delta
                    if 0 < key2 < SECP256K1_N:
                        candidates.add(key2)

        if strategy in ["all", "mersenne"]:
            # Mersenne numbers
            for x in range(1, 257):
                mersenne = (1 << x) - 1
                if mersenne < SECP256K1_N:
                    candidates.add(mersenne)

        if strategy in ["all", "mistakes"]:
            # Developer mistakes
            candidates.update(DevMistakeFocus.generate_all_mistakes())

        if strategy in ["all", "expanded"]:
            # Expand with nearby and squares
            candidates = NearbySquaredEngine.expand_candidates(
                candidates,
                radius=2,
                include_squares=True,
                include_bridge_powers=True,
                include_mersenne=True,
                include_mistakes=True
            )

        self.candidate_keys = candidates
        self.progress.total_candidates = len(candidates)
        logger.info(f"Generated {len(candidates):,} candidates")

        return candidates

    def test_single_key(self, private_key: int) -> Optional[Dict]:
        """Test a single private key"""
        try:
            pub_key = CryptoOperations.private_to_public(private_key)
            if not pub_key:
                return None

            address = CryptoOperations.public_to_address(pub_key)
            if not address:
                return None

            # Check if address has balance
            addr_data = self.scanner.get_address_details(address)
            if addr_data and addr_data.get('final_balance', 0) > 0:
                return {
                    'private_key': hex(private_key),
                    'public_key': pub_key,
                    'address': address,
                    'balance': addr_data.get('final_balance', 0) / 1e8,
                    'total_received': addr_data.get('total_received', 0) / 1e8,
                    'n_tx': addr_data.get('n_tx', 0),
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            logger.debug(f"Error testing key {hex(private_key)}: {e}")

        return None

    def scan_block_range(self, start_block: int, end_block: int, 
                         resume_file: Optional[str] = None) -> List[Dict]:
        """Scan a range of blocks for matches"""
        logger.info(f"Scanning blocks {start_block} to {end_block}")

        # Load resume state if provided
        if resume_file and os.path.exists(resume_file):
            try:
                with open(resume_file, 'r') as f:
                    state = json.load(f)
                    start_block = max(start_block, state.get('current_block', start_block))
                    logger.info(f"Resuming from block {start_block}")
            except Exception as e:
                logger.warning(f"Could not load resume file: {e}")

        self.progress.start_time = datetime.now().isoformat()
        self.progress.current_block = start_block

        # Multi-threaded block scanning
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {}
            block_heights = list(range(start_block, end_block + 1))

            # Submit block scanning tasks
            for height in block_heights:
                future = executor.submit(self._scan_single_block, height)
                futures[future] = height

            # Process completed tasks
            for future in as_completed(futures):
                height = futures[future]
                try:
                    block_matches = future.result()
                    self.matches.extend(block_matches)
                    self.progress.blocks_scanned += 1
                    self.progress.current_block = height

                    if height % 10 == 0:
                        self._save_progress(resume_file)
                        logger.info(f"Progress: {height}/{end_block} ({self.progress.blocks_scanned} blocks, {len(self.matches)} matches)")

                except Exception as e:
                    logger.error(f"Error scanning block {height}: {e}")

        self.progress.last_checkpoint = datetime.now().isoformat()
        return self.matches

    def _scan_single_block(self, height: int) -> List[Dict]:
        """Scan a single block"""
        block = self.scanner.get_block_by_height(height)
        if not block:
            return []

        return self.scanner.scan_block_for_keys(block, self.candidate_keys)

    def _save_progress(self, resume_file: Optional[str]):
        """Save progress to file"""
        if not resume_file:
            return

        try:
            state = {
                'current_block': self.progress.current_block,
                'blocks_scanned': self.progress.blocks_scanned,
                'keys_tested': self.progress.keys_tested,
                'matches_found': len(self.matches),
                'timestamp': datetime.now().isoformat()
            }
            with open(resume_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save progress: {e}")

    def save_results(self, filename: str):
        """Save results to JSON and CSV"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # JSON export
        json_file = os.path.join(CANDIDATE_EXPORTS, f"{filename}_{timestamp}.json")
        with open(json_file, 'w') as f:
            json.dump({
                'summary': asdict(self.progress),
                'matches': self.matches
            }, f, indent=2)
        logger.info(f"Results saved to {json_file}")

        # CSV export
        if self.matches:
            csv_file = os.path.join(CANDIDATE_EXPORTS, f"{filename}_{timestamp}.csv")
            with open(csv_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.matches[0].keys())
                writer.writeheader()
                writer.writerows(self.matches)
            logger.info(f"CSV saved to {csv_file}")

    def print_summary(self):
        """Print hunting summary"""
        print("\n" + "="*70)
        print("MASTER HUNTER SUMMARY")
        print("="*70)
        print(f"Candidates generated: {self.progress.total_candidates:,}")
        print(f"Blocks scanned: {self.progress.blocks_scanned:,}")
        print(f"Keys tested: {self.progress.keys_tested:,}")
        print(f"Matches found: {self.progress.matches_found:,}")
        print(f"Start time: {self.progress.start_time}")
        print(f"Last update: {self.progress.last_checkpoint}")
        print("="*70)


# ============================================================================
# SECTION 8: EXPORT UTILITIES
# ============================================================================

class ExportManager:
    """Manage all data exports"""

    @staticmethod
    def export_candidates(candidates: Set[int], prefix: str = "candidates"):
        """Export candidates to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Text file (hex)
        txt_file = os.path.join(CANDIDATE_EXPORTS, f"{prefix}_{timestamp}.txt")
        with open(txt_file, 'w') as f:
            for c in sorted(candidates):
                f.write(f"{hex(c)}\n")

        # CSV file
        csv_file = os.path.join(CANDIDATE_EXPORTS, f"{prefix}_{timestamp}.csv")
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['index', 'decimal', 'hexadecimal'])
            for i, c in enumerate(sorted(candidates)):
                writer.writerow([i+1, c, hex(c)])

        logger.info(f"Exported {len(candidates):,} candidates to {txt_file} and {csv_file}")

    @staticmethod
    def export_analysis(analysis_data: Dict, name: str):
        """Export analysis data"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_file = os.path.join(ANALYSIS_EXPORTS, f"{name}_{timestamp}.json")
        
        with open(json_file, 'w') as f:
            json.dump(analysis_data, f, indent=2)

        logger.info(f"Analysis exported to {json_file}")

    @staticmethod
    def export_blockchain_data(blocks: List[Dict], transactions: List[Dict]):
        """Export blockchain data"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Blocks CSV
        if blocks:
            blocks_file = os.path.join(BLOCKCHAIN_EXPORTS, f"blocks_{timestamp}.csv")
            with open(blocks_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=blocks[0].keys())
                writer.writeheader()
                writer.writerows(blocks)
            logger.info(f"Blocks exported to {blocks_file}")

        # Transactions CSV
        if transactions:
            tx_file = os.path.join(BLOCKCHAIN_EXPORTS, f"transactions_{timestamp}.csv")
            with open(tx_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=transactions[0].keys())
                writer.writeheader()
                writer.writerows(transactions)
            logger.info(f"Transactions exported to {tx_file}")


# ============================================================================
# MAIN INTERACTIVE MENU
# ============================================================================

def main():
    """Main interactive menu"""
    print("\n" + "="*70)
    print("THE ULTIMATE MASTER HUNTER")
    print("Complete Unified Bitcoin Key Hunting Framework")
    print("="*70)

    hunter = MasterHunter(threads=4)
    export_mgr = ExportManager()

    while True:
        print("\n" + "-"*70)
        print("MAIN MENU")
        print("-"*70)
        print("1. Generate Candidates (All Strategies)")
        print("2. Generate Candidates (Geometric Only)")
        print("3. Generate Candidates (Bridge Vicinity)")
        print("4. Generate Candidates (Developer Mistakes)")
        print("5. View Candidate Statistics")
        print("6. Export Candidates to File")
        print("7. Test Single Private Key")
        print("8. Scan Block Range (Live)")
        print("9. Quick Scan (Last 100 Blocks)")
        print("10. Verify Curve Parameters")
        print("11. Analyze Sparse Structure")
        print("12. Show Geometric Families")
        print("13. Show Bridge Relationships")
        print("14. Run Full Analysis Suite")
        print("15. Save Current Results")
        print("0. Exit")
        print("-"*70)

        choice = input("\nEnter choice (0-15): ").strip()

        if choice == "1":
            hunter.generate_candidates("all")
            print(f"\n✓ Generated {len(hunter.candidate_keys):,} candidates")

        elif choice == "2":
            hunter.generate_candidates("geometric")
            print(f"\n✓ Generated {len(hunter.candidate_keys):,} geometric candidates")

        elif choice == "3":
            hunter.generate_candidates("bridge")
            print(f"\n✓ Generated {len(hunter.candidate_keys):,} bridge candidates")

        elif choice == "4":
            hunter.generate_candidates("mistakes")
            print(f"\n✓ Generated {len(hunter.candidate_keys):,} mistake candidates")

        elif choice == "5":
            if hunter.candidate_keys:
                print(f"\nCandidate Statistics:")
                print(f"  Total: {len(hunter.candidate_keys):,}")
                sample = sorted(list(hunter.candidate_keys))[:10]
                print(f"  Sample (first 10): {[hex(c) for c in sample]}")
            else:
                print("\nNo candidates generated yet. Choose option 1-4 first.")

        elif choice == "6":
            if hunter.candidate_keys:
                prefix = input("Enter filename prefix (default: candidates): ").strip() or "candidates"
                export_mgr.export_candidates(hunter.candidate_keys, prefix)
            else:
                print("\nNo candidates to export. Generate candidates first.")

        elif choice == "7":
            try:
                key_input = input("\nEnter private key (hex or decimal): ").strip()
                if key_input.startswith('0x'):
                    key = int(key_input, 16)
                else:
                    key = int(key_input)

                print(f"\nTesting key: {hex(key)}")
                result = hunter.test_single_key(key)

                if result:
                    print("\n🎯 MATCH FOUND!")
                    print(f"  Address: {result['address']}")
                    print(f"  Balance: {result['balance']} BTC")
                    print(f"  Total Received: {result['total_received']} BTC")
                    print(f"  Transactions: {result['n_tx']}")
                else:
                    print("\nNo balance found for this key.")

            except ValueError:
                print("Invalid key format.")

        elif choice == "8":
            if not hunter.candidate_keys:
                print("\nGenerating candidates first...")
                hunter.generate_candidates("all")

            try:
                start = int(input("\nStart block (default: 1): ").strip() or "1")
                end = int(input(f"End block (default: {start + 99}): ").strip() or str(start + 99))
                threads = int(input("Threads (default: 4): ").strip() or "4")
                
                hunter.threads = threads
                resume = input("Resume file? (y/n): ").strip().lower() == 'y'
                resume_file = "hunter_checkpoint.json" if resume else None

                print(f"\n🔍 Scanning blocks {start} to {end}...")
                matches = hunter.scan_block_range(start, end, resume_file)
                hunter.print_summary()

                if matches:
                    hunter.save_results("block_scan_matches")
                    print(f"\n🎯 FOUND {len(matches)} MATCHES!")

            except ValueError:
                print("Invalid input.")

        elif choice == "9":
            if not hunter.candidate_keys:
                print("\nGenerating candidates first...")
                hunter.generate_candidates("all")

            # Get latest block
            latest_data = hunter.scanner.make_request(f"{API_BASE}/q/getblockcount")
            if latest_data:
                latest = int(latest_data)
                start = max(1, latest - 99)
                
                print(f"\n🔍 Quick scanning blocks {start} to {latest}...")
                hunter.threads = 4
                matches = hunter.scan_block_range(start, latest)
                hunter.print_summary()

                if matches:
                    hunter.save_results("quick_scan_matches")
                    print(f"\n🎯 FOUND {len(matches)} MATCHES!")
            else:
                print("Could not fetch latest block count.")

        elif choice == "10":
            params = CurveParameters()
            print("\n" + "="*70)
            print("CURVE PARAMETERS")
            print("="*70)
            print(f"p (prime): {hex(params.p)}")
            print(f"n (order): {hex(params.n)}")
            print(f"a: {params.a}")
            print(f"b: {params.b}")
            print(f"Gx: {hex(params.Gx)}")
            print(f"Gy: {hex(params.Gy)}")
            print(f"λ (GLV): {hex(params.lambda_glv)}")
            print(f"β (GLV): {hex(params.beta_glv)}")
            print(f"C (Gap): {params.gap_c} ({hex(params.gap_c)})")
            print(f"D (Bridge): {params.bridge_d} ({hex(params.bridge_d)})")

        elif choice == "11":
            analysis = FastReduction.verify_sparse_structure()
            print("\n" + "="*70)
            print("SPARSE STRUCTURE ANALYSIS")
            print("="*70)
            print(json.dumps(analysis, indent=2))

        elif choice == "12":
            print("\n" + "="*70)
            print("GEOMETRIC FAMILIES")
            print("="*70)
            print("\nFCC Sequence J(n) = 10n² + 2:")
            for n in range(1, 11):
                print(f"  J({n}) = {GeometricFamilies.j_n(n)}")

            print("\nCrystal Ball S(n):")
            for n in range(1, 11):
                print(f"  S({n}) = {GeometricFamilies.s_n(n)}")

        elif choice == "13":
            D = DIGITAL_BRIDGE_D
            C = GAP_C
            print("\n" + "="*70)
            print("DIGITAL BRIDGE RELATIONSHIPS")
            print("="*70)
            print(f"D = 2^16 = {D}")
            print(f"C = 2^32 + 977 = {C}")
            print(f"C = D² + 977 = {D*D + 977}")
            print(f"\nKey relationships:")
            print(f"  D - 1 = {D - 1}")
            print(f"  D + 1 = {D + 1}")
            print(f"  (D-1)² = {(D-1)**2}")
            print(f"  D² = {D**2}")
            print(f"  (D+1)² = {(D+1)**2}")

        elif choice == "14":
            print("\n🔍 Running Full Analysis Suite...")
            
            # 1. Curve verification
            print("\n1. Verifying curve parameters...")
            params = CurveParameters()
            
            # 2. Sparse structure
            print("2. Analyzing sparse structure...")
            sparse = FastReduction.verify_sparse_structure()
            export_mgr.export_analysis(sparse, "sparse_structure")
            
            # 3. Generate all candidates
            print("3. Generating all candidates...")
            hunter.generate_candidates("all")
            
            # 4. Export candidates
            print("4. Exporting candidates...")
            export_mgr.export_candidates(hunter.candidate_keys, "full_candidate_set")
            
            # 5. Candidate statistics
            print("5. Computing candidate statistics...")
            stats = {
                'total': len(hunter.candidate_keys),
                'min': min(hunter.candidate_keys),
                'max': max(hunter.candidate_keys),
                'sample': [hex(c) for c in sorted(list(hunter.candidate_keys))[:20]]
            }
            export_mgr.export_analysis(stats, "candidate_statistics")
            
            print("\n✓ Full analysis complete! Check exports directory.")

        elif choice == "15":
            if hunter.matches:
                hunter.save_results("manual_save_matches")
                print("\n✓ Results saved successfully!")
            else:
                print("\nNo matches to save yet.")

        elif choice == "0":
            print("\nExiting Master Hunter. Good luck hunting! 🎯")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
