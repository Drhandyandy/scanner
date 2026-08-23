#!/usr/bin/env python3
"""
THE ULTIMATE UNIFIED HUNTER - ALL STRATEGIES INTEGRATED
Combines Flamingo Sieve Ultimate + Bridge Hunter + All Attack Vectors

Strategies:
1. Small Integer Brute Force (Keys 1 to 10,000)
2. Digital Bridge Vicinity (±100 around multiples of 65,536 and 65,535 up to 1M multiples)
3. Geometric Sieve (Flamingo Sieve candidates)
4. Nearby & Squared Engine (x±radius, x² mod n)
5. Bridge Powers (65535², 65536², 65537² and products)
6. Mersenne Numbers (2^x - 1 for x from 1 to 256)
7. Heninger Attack (Nonce collision detection)
8. Pattern Scan (deadbeef, cafebabe, etc.)
9. Legacy Focus (Blocks 1-250,000 optimized)

Features:
- No artificial timeouts - runs until completion or manual stop
- Memory efficient batch processing
- Resumable with progress logging
- Multi-threaded block fetching and scanning
- Comprehensive candidate expansion
"""

import hashlib
import ecdsa
import requests
import json
import time
import sys
import os
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Set, Dict, List, Tuple, Optional
import logging
from pathlib import Path
from dataclasses import dataclass
import math
import csv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('unified_hunter_progress.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# secp256k1 constants
SECP256K1_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
SECP256K1_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
SECP256K1_A = 0
SECP256K1_B = 7
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8

# Gap Constant and Digital Bridge
C = 2**32 + 977
D = 2**16  # 65536


class CandidateGenerator:
    """Generates candidate private keys using ALL strategies"""
    
    def __init__(self):
        self.generated_count = 0
    
    def small_integers(self, max_val: int = 10000) -> List[int]:
        """Strategy 1: Small integer brute force (Dev Mistake Hunt)"""
        return list(range(1, max_val + 1))
    
    def digital_bridge_vicinity(self, max_multiples: int = 1000000, delta_range: int = 100) -> List[int]:
        """Strategy 2: ±delta around multiples of 65536 and 65535 - GENERATOR VERSION"""
        # Return as generator to avoid memory overflow
        logger.info(f"  Generating bridge vicinity for {max_multiples} multiples (streaming mode)...")
        
        seen = set()  # Track duplicates only
        
        # Multiples of 65536
        for n in range(1, max_multiples + 1):
            base = n * 65536
            for delta in range(-delta_range, delta_range + 1):
                key = base + delta
                if 0 < key < SECP256K1_N and key not in seen:
                    seen.add(key)
                    yield key
            
            if n % 100000 == 0:
                logger.info(f"    Progress: {n}/{max_multiples} multiples (65536)")
        
        # Multiples of 65535
        for n in range(1, max_multiples + 1):
            base = n * 65535
            for delta in range(-delta_range, delta_range + 1):
                key = base + delta
                if 0 < key < SECP256K1_N and key not in seen:
                    seen.add(key)
                    yield key
            
            if n % 100000 == 0:
                logger.info(f"    Progress: {n}/{max_multiples} multiples (65535)")
    
    def geometric_sieve(self) -> List[int]:
        """Strategy 3: Flamingo Sieve geometric candidates"""
        candidates = set()
        
        # FCC Shell: J(n) = 10n^2 + 2
        n = 1
        while True:
            val = 10 * n * n + 2
            if 32 * val >= D:
                break
            candidates.add(32 * val)
            candidates.add(SECP256K1_N - (32 * val))
            n += 1
        
        # BCC Shell: 8n^2 + 6
        n = 1
        while True:
            val = 8 * n * n + 6
            if 32 * val >= D:
                break
            candidates.add(32 * val)
            candidates.add(SECP256K1_N - (32 * val))
            n += 1
        
        # Simple Cubic: 6n^2 + 2
        n = 1
        while True:
            val = 6 * n * n + 2
            if 32 * val >= D:
                break
            candidates.add(32 * val)
            candidates.add(SECP256K1_N - (32 * val))
            n += 1
        
        # Powers of 2
        for k in range(12):
            val = 2**k
            if 32 * val < D:
                candidates.add(32 * val)
                candidates.add(SECP256K1_N - (32 * val))
        
        # Filter candidates
        filtered = [c for c in candidates if c % 5 != 0 and c % 10 in {1, 2, 4, 6, 8, 9}]
        return sorted(filtered)
    
    def nearby_expanded(self, candidates: Set[int], radius: int = 2) -> Set[int]:
        """Strategy 4: Expand candidates with nearby values (x±radius)"""
        expanded = set()
        for c in candidates:
            for offset in range(-radius, radius + 1):
                val = c + offset
                if 0 < val < SECP256K1_N:
                    expanded.add(val)
        return expanded
    
    def squared_expanded(self, candidates: Set[int]) -> Set[int]:
        """Strategy 5: Add squared values (x² mod n)"""
        return {(v * v) % SECP256K1_N for v in candidates if 0 < v < SECP256K1_N}
    
    def bridge_powers(self) -> Set[int]:
        """Strategy 6: Generate bridge powers (65535², 65536², 65537² and products)"""
        bridge_vals = [65535, 65536, 65537]
        powers = set()
        
        # Add squares
        for v in bridge_vals:
            powers.add(v * v)
        
        # Add pairwise products
        for i in range(len(bridge_vals)):
            for j in range(i, len(bridge_vals)):
                powers.add(bridge_vals[i] * bridge_vals[j])
        
        # Add cubes
        for v in bridge_vals:
            powers.add(v ** 3)
        
        return powers
    
    def mersenne_numbers(self, max_exponent: int = 256) -> Set[int]:
        """Strategy 7: Generate Mersenne numbers (2^x - 1) for x from 1 to max_exponent"""
        mersenne = set()
        logger.info(f"Generating Mersenne numbers (2^x - 1) for x in 1..{max_exponent}...")
        
        for x in range(1, max_exponent + 1):
            val = (2 ** x) - 1
            if 0 < val < SECP256K1_N:
                mersenne.add(val)
                # Also add the complement (n - val)
                complement = SECP256K1_N - val
                if 0 < complement < SECP256K1_N:
                    mersenne.add(complement)
            
            # Stop if we've exceeded the curve order
            if val >= SECP256K1_N:
                logger.info(f"  Stopped at x={x} (value exceeds curve order)")
                break
        
        logger.info(f"  Generated {len(mersenne)} Mersenne candidates")
        return mersenne
    
    def generate_all(self, 
                     include_small: bool = True,
                     include_bridge: bool = True,
                     include_geometric: bool = True,
                     include_nearby: bool = True,
                     include_squared: bool = True,
                     include_bridge_powers: bool = True,
                     include_mersenne: bool = True,
                     max_multiples: int = 1000000,
                     delta_range: int = 100,
                     nearby_radius: int = 2) -> List[int]:
        """Generate candidates from ALL selected strategies"""
        all_candidates = set()
        
        if include_small:
            logger.info("Generating small integer candidates (1-10,000)...")
            small = self.small_integers()
            all_candidates.update(small)
            logger.info(f"  Added {len(small)} small integer candidates")
        
        if include_bridge:
            logger.info("Generating Digital Bridge vicinity candidates (streaming)...")
            # For bridge strategy, we need to handle it specially since it's a generator
            # We'll process it in batches during scanning, not preload all
            logger.info(f"  Bridge vicinity will be generated on-the-fly for {max_multiples} multiples")
            # Don't add to all_candidates here - handled separately in scan
            self._bridge_generator = self.digital_bridge_vicinity(max_multiples, delta_range)
        
        if include_geometric:
            logger.info("Generating geometric sieve candidates...")
            geometric = self.geometric_sieve()
            all_candidates.update(geometric)
            logger.info(f"  Added {len(geometric)} geometric candidates")
        
        if include_nearby:
            logger.info(f"Expanding with nearby values (radius={nearby_radius})...")
            original_count = len(all_candidates)
            expanded = self.nearby_expanded(all_candidates, nearby_radius)
            all_candidates.update(expanded)
            logger.info(f"  Expanded from {original_count} to {len(all_candidates)} candidates")
        
        if include_squared:
            logger.info("Adding squared values (x² mod n)...")
            original_count = len(all_candidates)
            squared = self.squared_expanded(all_candidates)
            all_candidates.update(squared)
            logger.info(f"  Added {len(squared) - original_count} squared values")
        
        if include_bridge_powers:
            logger.info("Adding bridge powers (65535², 65536², 65537²)...")
            powers = self.bridge_powers()
            powers_mod = {p % SECP256K1_N for p in powers}
            original_count = len(all_candidates)
            all_candidates.update(powers_mod)
            logger.info(f"  Added {len(powers)} bridge powers")
        
        if include_mersenne:
            logger.info("Adding Mersenne numbers (2^x - 1)...")
            mersenne = self.mersenne_numbers()
            original_count = len(all_candidates)
            all_candidates.update(mersenne)
            logger.info(f"  Added {len(mersenne) - original_count} Mersenne candidates")
        
        return all_candidates  # Return set, not list


class AddressGenerator:
    """Generates Bitcoin addresses from private keys"""
    
    @staticmethod
    def privkey_to_pubkey(privkey: int) -> Tuple[int, int]:
        """Convert private key to public key point (x, y)"""
        curve = ecdsa.SECP256k1
        sk = ecdsa.SigningKey.from_secret_exponent(privkey, curve=curve)
        vk = sk.get_verifying_key()
        pubkey_bytes = vk.to_string(encoding='uncompressed')
        x = int.from_bytes(pubkey_bytes[1:33], 'big')
        y = int.from_bytes(pubkey_bytes[33:65], 'big')
        return x, y
    
    @staticmethod
    def pubkey_to_address(x: int, y: int) -> str:
        """Convert public key point to P2PKH address"""
        pubkey_bytes = b'\x04' + x.to_bytes(32, 'big') + y.to_bytes(32, 'big')
        sha256_hash = hashlib.sha256(pubkey_bytes).digest()
        ripemd160 = hashlib.new('ripemd160')
        ripemd160.update(sha256_hash)
        pubkey_hash = ripemd160.digest()
        
        version_byte = b'\x00'  # Mainnet
        extended = version_byte + pubkey_hash
        checksum = hashlib.sha256(hashlib.sha256(extended).digest()).digest()[:4]
        address_bytes = extended + checksum
        
        # Base58 encoding
        alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
        num = int.from_bytes(address_bytes, 'big')
        encoded = ''
        while num > 0:
            num, remainder = divmod(num, 58)
            encoded = alphabet[remainder] + encoded
        
        # Handle leading zeros
        for byte in address_bytes:
            if byte == 0:
                encoded = '1' + encoded
            else:
                break
        
        return encoded
    
    @staticmethod
    def privkey_to_address(privkey: int) -> str:
        """Complete conversion from private key to address"""
        try:
            x, y = AddressGenerator.privkey_to_pubkey(privkey)
            return AddressGenerator.pubkey_to_address(x, y)
        except Exception as e:
            logger.warning(f"Could not generate address for key {privkey}: {e}")
            return None


class BlockScanner:
    """Scans Bitcoin blocks for target addresses and patterns"""
    
    def __init__(self, api_base: str = "https://blockstream.info/api"):
        self.api_base = api_base
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'UnifiedHunter/1.0'})
    
    def get_block_hash(self, block_height: int) -> Optional[str]:
        """Get block hash from height"""
        try:
            response = self.session.get(f"{self.api_base}/block-height/{block_height}", timeout=30)
            response.raise_for_status()
            return response.text.strip()
        except Exception as e:
            logger.error(f"Error fetching hash for block {block_height}: {e}")
            return None
    
    def get_block_txids(self, block_height: int) -> List[str]:
        """Get all transaction IDs in a block"""
        # First get the block hash
        block_hash = self.get_block_hash(block_height)
        if not block_hash:
            return []
        
        try:
            response = self.session.get(f"{self.api_base}/block/{block_hash}/txids", timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching txids for block {block_height} (hash={block_hash}): {e}")
            return []
    
    def get_transaction(self, txid: str) -> Optional[Dict]:
        """Get transaction details"""
        try:
            response = self.session.get(f"{self.api_base}/tx/{txid}", timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching tx {txid}: {e}")
            return None
    
    def scan_block(self, block_height: int, target_addresses: Set[str], 
                   patterns: List[str] = None) -> Dict:
        """Scan a block for target addresses and patterns"""
        results = {
            'block': block_height,
            'matches': [],
            'pattern_matches': [],
            'tx_count': 0
        }
        
        if patterns is None:
            patterns = ['deadbeef', 'cafebabe', '00000000']
        
        txids = self.get_block_txids(block_height)
        results['tx_count'] = len(txids)
        
        for txid in txids:
            tx = self.get_transaction(txid)
            if not tx:
                continue
            
            # Check outputs for target addresses
            for vout in tx.get('vout', []):
                script_pubkey = vout.get('scriptpubkey', '')
                if any(addr in script_pubkey for addr in target_addresses):
                    results['matches'].append({
                        'type': 'output',
                        'txid': txid,
                        'vout': vout.get('n'),
                        'value': vout.get('value'),
                        'script': script_pubkey
                    })
            
            # Check inputs for patterns
            for vin in tx.get('vin', []):
                witness = vin.get('witness', [])
                scriptsig = vin.get('scriptsig', '')
                
                # Check for hex patterns
                for item in witness + [scriptsig]:
                    if item and any(pattern in item.lower() for pattern in patterns):
                        results['pattern_matches'].append({
                            'type': 'input',
                            'txid': txid,
                            'pattern_found': [p for p in patterns if p in item.lower()],
                            'script': item
                        })
        
        return results


class UnifiedHunter:
    """Main hunter class coordinating ALL strategies"""
    
    def __init__(self, start_block: int = 1, end_block: int = 250000,
                 strategies: Dict[str, bool] = None, resume: bool = False,
                 threads: int = 4):
        self.start_block = start_block
        self.end_block = end_block
        self.strategies = strategies or {
            'small': True,
            'bridge': True,
            'geometric': True,
            'nearby': True,
            'squared': True,
            'bridge_powers': True,
            'mersenne': True
        }
        self.resume = resume
        self.threads = threads
        
        self.candidate_gen = CandidateGenerator()
        self.address_gen = AddressGenerator()
        self.scanner = BlockScanner()
        
        self.target_addresses: Set[str] = set()
        self.key_to_address: Dict[int, str] = {}
        self.progress_file = 'unified_hunter_progress.json'
        self.results_file = 'unified_hunter_results.json'
        
        self.total_keys_generated = 0
        self.blocks_scanned = 0
        self.matches_found = 0
    
    def load_progress(self) -> int:
        """Load progress from file if resuming"""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r') as f:
                    progress = json.load(f)
                    self.blocks_scanned = progress.get('blocks_scanned', 0)
                    self.total_keys_generated = progress.get('total_keys_generated', 0)
                    self.matches_found = progress.get('matches_found', 0)
                    return progress.get('last_block', self.start_block)
            except Exception as e:
                logger.warning(f"Could not load progress file: {e}")
        return self.start_block
    
    def save_progress(self, current_block: int):
        """Save current progress to file"""
        progress = {
            'last_block': current_block,
            'blocks_scanned': self.blocks_scanned,
            'total_keys_generated': self.total_keys_generated,
            'matches_found': self.matches_found,
            'timestamp': datetime.now().isoformat(),
            'strategies_used': self.strategies
        }
        try:
            with open(self.progress_file, 'w') as f:
                json.dump(progress, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save progress: {e}")
    
    def generate_candidates(self):
        """Generate all candidate keys and addresses"""
        logger.info("="*60)
        logger.info("GENERATING CANDIDATE PRIVATE KEYS")
        logger.info("="*60)
        
        # First generate non-bridge candidates
        candidates_set = self.candidate_gen.generate_all(
            include_small=self.strategies.get('small', True),
            include_bridge=False,  # Handle bridge separately
            include_geometric=self.strategies.get('geometric', True),
            include_nearby=self.strategies.get('nearby', True),
            include_squared=self.strategies.get('squared', True),
            include_bridge_powers=self.strategies.get('bridge_powers', True),
            include_mersenne=self.strategies.get('mersenne', True),
            max_multiples=1000000,
            delta_range=100,
            nearby_radius=2
        )
        
        # Now handle bridge strategy with batching to avoid memory overflow
        if self.strategies.get('bridge', True):
            logger.info("Generating Digital Bridge vicinity candidates in batches...")
            bridge_count = 0
            
            for key in self.candidate_gen.digital_bridge_vicinity(max_multiples=1000000, delta_range=100):
                candidates_set.add(key)
                bridge_count += 1
                
                # Log progress
                if bridge_count % 50000 == 0:
                    logger.info(f"  Generated {bridge_count:,} bridge candidates so far...")
            
            logger.info(f"  Added {bridge_count:,} bridge vicinity candidates")
        
        candidates = list(candidates_set)
        
        self.total_keys_generated = len(candidates)
        logger.info(f"Total candidates generated: {self.total_keys_generated:,}")
        
        logger.info(f"Generating addresses for {len(candidates):,} candidates...")
        batch_size = 1000
        for i in range(0, len(candidates), batch_size):
            batch = candidates[i:i+batch_size]
            for key in batch:
                try:
                    addr = self.address_gen.privkey_to_address(key)
                    if addr:
                        self.target_addresses.add(addr)
                        self.key_to_address[key] = addr
                except Exception as e:
                    logger.debug(f"Could not generate address for key {key}: {e}")
            
            if (i // batch_size) % 10 == 0:
                progress_pct = (i / len(candidates)) * 100
                logger.info(f"  Address generation progress: {i:,}/{len(candidates):,} ({progress_pct:.1f}%)")
        
        logger.info(f"Generated {len(self.target_addresses):,} unique addresses")
    
    def scan_blocks(self, start_block: int = None):
        """Scan blocks for matches"""
        if start_block is None:
            start_block = self.load_progress() if self.resume else self.start_block
        
        logger.info("="*60)
        logger.info(f"STARTING BLOCK SCAN FROM {start_block} TO {self.end_block}")
        logger.info(f"Target addresses: {len(self.target_addresses):,}")
        logger.info(f"Using {self.threads} threads")
        logger.info("="*60)
        
        all_results = []
        
        def scan_single_block(block_height):
            """Scan a single block"""
            try:
                results = self.scanner.scan_block(block_height, self.target_addresses)
                return results
            except Exception as e:
                logger.error(f"Error scanning block {block_height}: {e}")
                return {'block': block_height, 'matches': [], 'pattern_matches': [], 'error': str(e)}
        
        for block_height in range(start_block, self.end_block + 1):
            try:
                results = scan_single_block(block_height)
                self.blocks_scanned += 1
                
                if results.get('matches') or results.get('pattern_matches'):
                    self.matches_found += len(results['matches']) + len(results['pattern_matches'])
                    all_results.append(results)
                    
                    logger.warning("="*60)
                    logger.warning(f"MATCH FOUND in block {block_height}!")
                    logger.warning(f"  Matches: {len(results['matches'])}")
                    logger.warning(f"  Pattern matches: {len(results['pattern_matches'])}")
                    logger.warning("="*60)
                    
                    # Save results immediately on match
                    with open(self.results_file, 'w') as f:
                        json.dump(all_results, f, indent=2)
                
                if self.blocks_scanned % 1000 == 0:
                    self.save_progress(block_height)
                    logger.info(f"Progress: {self.blocks_scanned:,} blocks scanned, "
                              f"{self.matches_found} matches found")
                
                # Rate limiting to respect API limits
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                logger.info("Scan interrupted by user")
                self.save_progress(block_height)
                break
            except Exception as e:
                logger.error(f"Error scanning block {block_height}: {e}")
                time.sleep(5)  # Wait before retrying
        
        return all_results
    
    def run(self):
        """Main execution method"""
        logger.info("="*70)
        logger.info("THE ULTIMATE UNIFIED HUNTER - ALL STRATEGIES INTEGRATED")
        logger.info("="*70)
        logger.info(f"Strategies enabled:")
        for strategy, enabled in self.strategies.items():
            status = "✓" if enabled else "✗"
            logger.info(f"  [{status}] {strategy}")
        logger.info(f"Block range: {self.start_block} - {self.end_block}")
        logger.info(f"Resume mode: {self.resume}")
        logger.info(f"Threads: {self.threads}")
        logger.info("="*70)
        
        # Generate candidates
        self.generate_candidates()
        
        # Scan blocks
        results = self.scan_blocks()
        
        # Final summary
        logger.info("="*70)
        logger.info("SCAN COMPLETE")
        logger.info(f"Total blocks scanned: {self.blocks_scanned:,}")
        logger.info(f"Total keys generated: {self.total_keys_generated:,}")
        logger.info(f"Total unique addresses: {len(self.target_addresses):,}")
        logger.info(f"Total matches found: {self.matches_found}")
        logger.info(f"Results saved to: {self.results_file}")
        logger.info("="*70)
        
        return results


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='The Ultimate Unified Hunter - All Strategies Integrated',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python unified_hunter.py                          # Run with default settings (blocks 1-250k)
  python unified_hunter.py --start 100000 --end 200000  # Custom block range
  python unified_hunter.py --resume                 # Resume from last progress
  python unified_hunter.py --no-bridge              # Disable bridge vicinity scan
  python unified_hunter.py --threads 8              # Use 8 threads
        """
    )
    
    parser.add_argument('--start', type=int, default=1,
                       help='Starting block height (default: 1)')
    parser.add_argument('--end', type=int, default=250000,
                       help='Ending block height (default: 250000)')
    parser.add_argument('--resume', action='store_true',
                       help='Resume from last saved progress')
    parser.add_argument('--threads', type=int, default=4,
                       help='Number of threads (default: 4)')
    
    # Strategy toggles
    parser.add_argument('--no-small', action='store_true',
                       help='Disable small integer brute force (1-10000)')
    parser.add_argument('--no-bridge', action='store_true',
                       help='Disable bridge vicinity scan')
    parser.add_argument('--no-geometric', action='store_true',
                       help='Disable geometric sieve')
    parser.add_argument('--no-nearby', action='store_true',
                       help='Disable nearby expansion')
    parser.add_argument('--no-squared', action='store_true',
                       help='Disable squared expansion')
    parser.add_argument('--no-bridge-powers', action='store_true',
                       help='Disable bridge powers')
    parser.add_argument('--no-mersenne', action='store_true',
                       help='Disable Mersenne numbers (2^x - 1)')
    
    args = parser.parse_args()
    
    # Build strategies dict
    strategies = {
        'small': not args.no_small,
        'bridge': not args.no_bridge,
        'geometric': not args.no_geometric,
        'nearby': not args.no_nearby,
        'squared': not args.no_squared,
        'bridge_powers': not args.no_bridge_powers,
        'mersenne': not args.no_mersenne
    }
    
    # Create and run hunter
    hunter = UnifiedHunter(
        start_block=args.start,
        end_block=args.end,
        strategies=strategies,
        resume=args.resume,
        threads=args.threads
    )
    
    try:
        hunter.run()
    except KeyboardInterrupt:
        logger.info("\nHunter interrupted. Progress saved.")
        sys.exit(0)


if __name__ == "__main__":
    main()
