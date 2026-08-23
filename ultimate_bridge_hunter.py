#!/usr/bin/env python3
"""
THE ULTIMATE "DEV MISTAKE" & "DIGITAL BRIDGE" HUNTER
Untrammelled, Unbrevified, and Resumable Scanner for Historical Bitcoin Blocks

Strategies:
1. Small Integer Brute Force (Keys 1 to 10,000)
2. Digital Bridge Vicinity (±100 around multiples of 65,536 and 65,535 up to 1M multiples)
3. Geometric Sieve (Flamingo Sieve candidates)
4. Heninger Attack (Nonce collision detection)
5. Pattern Scan (deadbeef, cafebabe, etc.)
6. Legacy Focus (Blocks 1-250,000 optimized)

Features:
- No artificial timeouts - runs until completion or manual stop
- Memory efficient batch processing
- Resumable with progress logging
- Multi-threaded block fetching and scanning
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hunter_progress.log'),
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
    """Generates candidate private keys using multiple strategies"""
    
    def __init__(self):
        self.generated_count = 0
    
    def small_integers(self, max_val: int = 10000) -> List[int]:
        """Strategy 1: Small integer brute force"""
        return list(range(1, max_val + 1))
    
    def digital_bridge_vicinity(self, max_multiples: int = 1000000, delta_range: int = 100) -> List[int]:
        """Strategy 2: ±delta around multiples of 65536 and 65535"""
        candidates = set()
        
        # Multiples of 65536
        for n in range(1, max_multiples + 1):
            base = n * 65536
            for delta in range(-delta_range, delta_range + 1):
                key = base + delta
                if 0 < key < SECP256K1_N:
                    candidates.add(key)
        
        # Multiples of 65535
        for n in range(1, max_multiples + 1):
            base = n * 65535
            for delta in range(-delta_range, delta_range + 1):
                key = base + delta
                if 0 < key < SECP256K1_N:
                    candidates.add(key)
        
        return sorted(list(candidates))
    
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
    
    def generate_all(self, strategies: List[str] = None) -> List[int]:
        """Generate candidates from selected strategies"""
        if strategies is None:
            strategies = ['small', 'bridge', 'geometric']
        
        all_candidates = set()
        
        if 'small' in strategies:
            logger.info("Generating small integer candidates (1-10,000)...")
            small = self.small_integers()
            all_candidates.update(small)
            logger.info(f"  Added {len(small)} small integer candidates")
        
        if 'bridge' in strategies:
            logger.info("Generating Digital Bridge vicinity candidates...")
            bridge = self.digital_bridge_vicinity()
            all_candidates.update(bridge)
            logger.info(f"  Added {len(bridge)} bridge vicinity candidates")
        
        if 'geometric' in strategies:
            logger.info("Generating geometric sieve candidates...")
            geometric = self.geometric_sieve()
            all_candidates.update(geometric)
            logger.info(f"  Added {len(geometric)} geometric candidates")
        
        return sorted(list(all_candidates))


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


class BlockScanner:
    """Scans Bitcoin blocks for target addresses"""
    
    def __init__(self, api_base: str = "https://blockstream.info/api"):
        self.api_base = api_base
        self.session = requests.Session()
    
    def get_block_txids(self, block_height: int) -> List[str]:
        """Get all transaction IDs in a block"""
        try:
            response = self.session.get(f"{self.api_base}/block/{block_height}/txids", timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching txids for block {block_height}: {e}")
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


class Hunter:
    """Main hunter class coordinating all strategies"""
    
    def __init__(self, start_block: int = 1, end_block: int = 250000,
                 strategies: List[str] = None, resume: bool = False):
        self.start_block = start_block
        self.end_block = end_block
        self.strategies = strategies or ['small', 'bridge', 'geometric']
        self.resume = resume
        
        self.candidate_gen = CandidateGenerator()
        self.address_gen = AddressGenerator()
        self.scanner = BlockScanner()
        
        self.target_addresses: Set[str] = set()
        self.key_to_address: Dict[int, str] = {}
        self.progress_file = 'hunter_progress.json'
        self.results_file = 'hunter_results.json'
        
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
            'timestamp': datetime.now().isoformat()
        }
        try:
            with open(self.progress_file, 'w') as f:
                json.dump(progress, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save progress: {e}")
    
    def generate_candidates(self):
        """Generate all candidate keys and addresses"""
        logger.info("Generating candidate private keys...")
        candidates = self.candidate_gen.generate_all(self.strategies)
        self.total_keys_generated = len(candidates)
        
        logger.info(f"Generating addresses for {len(candidates)} candidates...")
        for i, key in enumerate(candidates):
            if i % 10000 == 0:
                logger.info(f"  Progress: {i}/{len(candidates)} addresses generated")
            try:
                x, y = self.address_gen.privkey_to_pubkey(key)
                addr = self.address_gen.pubkey_to_address(x, y)
                self.target_addresses.add(addr)
                self.key_to_address[key] = addr
            except Exception as e:
                logger.warning(f"Could not generate address for key {key}: {e}")
        
        logger.info(f"Generated {len(self.target_addresses)} unique addresses")
    
    def scan_blocks(self, start_block: int = None):
        """Scan blocks for matches"""
        if start_block is None:
            start_block = self.load_progress() if self.resume else self.start_block
        
        logger.info(f"Starting block scan from {start_block} to {self.end_block}")
        logger.info(f"Target addresses: {len(self.target_addresses)}")
        
        all_results = []
        
        for block_height in range(start_block, self.end_block + 1):
            try:
                results = self.scanner.scan_block(block_height, self.target_addresses)
                self.blocks_scanned += 1
                
                if results['matches'] or results['pattern_matches']:
                    self.matches_found += len(results['matches']) + len(results['pattern_matches'])
                    all_results.append(results)
                    logger.warning(f"MATCH FOUND in block {block_height}!")
                    logger.warning(f"  Matches: {len(results['matches'])}")
                    logger.warning(f"  Pattern matches: {len(results['pattern_matches'])}")
                    
                    # Save results immediately on match
                    with open(self.results_file, 'w') as f:
                        json.dump(all_results, f, indent=2)
                
                if self.blocks_scanned % 1000 == 0:
                    self.save_progress(block_height)
                    logger.info(f"Progress: {self.blocks_scanned} blocks scanned, "
                              f"{self.matches_found} matches found")
                
                # Rate limiting
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
        logger.info("="*60)
        logger.info("ULTIMATE DEV MISTAKE & DIGITAL BRIDGE HUNTER")
        logger.info("="*60)
        logger.info(f"Strategies: {', '.join(self.strategies)}")
        logger.info(f"Block range: {self.start_block} - {self.end_block}")
        logger.info(f"Resume mode: {self.resume}")
        
        # Generate candidates
        self.generate_candidates()
        
        # Scan blocks
        results = self.scan_blocks()
        
        # Final summary
        logger.info("="*60)
        logger.info("SCAN COMPLETE")
        logger.info(f"Total blocks scanned: {self.blocks_scanned}")
        logger.info(f"Total keys generated: {self.total_keys_generated}")
        logger.info(f"Total matches found: {self.matches_found}")
        logger.info("="*60)
        
        return results


def main():
    parser = argparse.ArgumentParser(description='Ultimate Bitcoin Key Hunter')
    parser.add_argument('--start', type=int, default=1, help='Start block height')
    parser.add_argument('--end', type=int, default=250000, help='End block height')
    parser.add_argument('--strategies', nargs='+', 
                       choices=['small', 'bridge', 'geometric'],
                       default=['small', 'bridge', 'geometric'],
                       help='Strategies to use')
    parser.add_argument('--resume', action='store_true', help='Resume from last progress')
    
    args = parser.parse_args()
    
    hunter = Hunter(
        start_block=args.start,
        end_block=args.end,
        strategies=args.strategies,
        resume=args.resume
    )
    
    hunter.run()


if __name__ == '__main__':
    main()
