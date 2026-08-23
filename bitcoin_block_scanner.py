#!/usr/bin/env python3
"""
Bitcoin Block Scanner with UTXO Stalking and Wallet Grouping
Fetches real-time data from Blockchain.com API.
Features:
- Scan blocks by height, hash, or range
- Track UTXOs for specific addresses
- Group wallet data by clustering heuristics
- Analyze transaction flows
"""

import requests
import time
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Set, Optional

API_BASE = "https://blockchain.info"
HEADERS = {'User-Agent': 'Mozilla/5.0'}

class BitcoinScanner:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.watched_addresses: Set[str] = set()
        self.address_clusters: Dict[int, Set[str]] = defaultdict(set)
        self.utxo_data: Dict[str, Dict] = {}  # address -> utxos
        
    def make_request(self, url: str, params: Optional[Dict] = None) -> Dict:
        """Make API request with error handling."""
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            return {}
    
    def get_latest_block_height(self) -> int:
        """Get the current highest block height."""
        data = self.make_request(f"{API_BASE}/q/getblockcount")
        if isinstance(data, int):
            return data
        return 0
    
    def get_block_by_height(self, height: int) -> Dict:
        """Fetch block data by height."""
        return self.make_request(f"{API_BASE}/block/{height}?format=json")
    
    def get_block_by_hash(self, block_hash: str) -> Dict:
        """Fetch block data by hash."""
        return self.make_request(f"{API_BASE}/rawblock/{block_hash}")
    
    def get_address_details(self, address: str) -> Dict:
        """Get detailed information about an address."""
        return self.make_request(f"{API_BASE}/rawaddr/{address}")
    
    def get_utxos_for_address(self, address: str) -> List[Dict]:
        """Get unspent outputs for a specific address."""
        data = self.make_request(f"{API_BASE}/unspent?active={address}")
        return data.get('unspent_outputs', [])
    
    def stalk_utxos(self, addresses: List[str], verbose: bool = True) -> Dict[str, Dict]:
        """Track UTXOs for a list of addresses and update internal state."""
        results = {}
        for addr in addresses:
            if verbose:
                print(f"Stalking UTXOs for: {addr}...")
            utxos = self.get_utxos_for_address(addr)
            total_balance = sum(u['value'] for u in utxos)
            
            self.utxo_data[addr] = {
                'utxos': utxos,
                'balance': total_balance,
                'count': len(utxos),
                'last_updated': datetime.now().isoformat()
            }
            
            # Add to watched list
            self.watched_addresses.add(addr)
            
            if verbose:
                print(f"  - Balance: {total_balance / 1e8:.8f} BTC")
                print(f"  - UTXO Count: {len(utxos)}")
                
            results[addr] = self.utxo_data[addr]
        return results
    
    def cluster_addresses_by_inputs(self, tx_hash: str) -> Set[str]:
        """
        Heuristic: If multiple addresses are inputs in the same transaction,
        they likely belong to the same wallet/entity.
        """
        time.sleep(0.2)  # Rate limiting
        tx_data = self.make_request(f"{API_BASE}/rawtx/{tx_hash}")
        if not tx_data or 'inputs' not in tx_data:
            return set()
        
        input_addresses = set()
        for inp in tx_data.get('inputs', []):
            prev_out = inp.get('prev_out', {})
            addr = prev_out.get('addr')
            if addr:
                input_addresses.add(addr)
        
        # If more than one input, cluster them
        if len(input_addresses) > 1:
            cluster_id = hash(frozenset(input_addresses)) % 10000
            self.address_clusters[cluster_id].update(input_addresses)
            
        return input_addresses
    
    def analyze_block_for_clustering(self, height: int) -> Dict[int, Set[str]]:
        """Scan a block and identify potential wallet clusters based on common inputs."""
        block = self.get_block_by_height(height)
        if not block or 'tx' not in block:
            return {}
        
        print(f"Analyzing block {height} for wallet clustering...")
        local_clusters = defaultdict(set)
        
        for i, tx in enumerate(block.get('tx', [])):
            tx_hash = tx.get('hash')
            if not tx_hash:
                continue
            
            # Limit to first 10 transactions to avoid rate limits
            if i >= 10:
                break
                
            inputs = self.cluster_addresses_by_inputs(tx_hash)
            if len(inputs) > 1:
                cluster_id = hash(frozenset(inputs)) % 10000
                local_clusters[cluster_id].update(inputs)
                self.address_clusters[cluster_id].update(inputs)
        
        return local_clusters
    
    def get_wallet_summary(self, cluster_id: int) -> Dict:
        """Get aggregated data for a specific wallet cluster."""
        addresses = self.address_clusters.get(cluster_id, set())
        if not addresses:
            return {}
        
        total_balance = 0
        total_utxos = 0
        
        # Ensure we have fresh data for these addresses
        if addresses - set(self.utxo_data.keys()):
            self.stalk_utxos(list(addresses - set(self.utxo_data.keys())), verbose=False)
        
        for addr in addresses:
            if addr in self.utxo_data:
                total_balance += self.utxo_data[addr]['balance']
                total_utxos += self.utxo_data[addr]['count']
        
        return {
            'cluster_id': cluster_id,
            'addresses': list(addresses),
            'address_count': len(addresses),
            'total_balance_btc': total_balance / 1e8,
            'total_utxos': total_utxos
        }
    
    def display_block_info(self, block: Dict):
        """Display formatted block information."""
        if not block:
            print("No block data found.")
            return

        print("\n" + "="*40)
        print(f"Block Height: {block.get('height')}")
        print(f"Hash: {block.get('hash')}")
        print(f"Time: {datetime.fromtimestamp(block.get('time', 0)).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Transactions: {len(block.get('tx', []))}")
        print(f"Size: {block.get('size')} bytes")
        print(f"Weight: {block.get('weight')}")
        print(f"Difficulty: {block.get('difficulty')}")
        
        # Calculate fees and reward
        total_output = sum(out['value'] for tx in block.get('tx', []) for out in tx.get('out', []))
        coinbase_tx = block.get('tx', [{}])[0]
        coinbase_output = sum(out['value'] for out in coinbase_tx.get('out', []))
        subsidy = 50 * 1e8
        # Approximate fee calculation
        fees = coinbase_output - subsidy 
        
        print(f"Total Output: {total_output / 1e8:.8f} BTC")
        print(f"Estimated Fees: {fees / 1e8:.8f} BTC")
        print("="*40 + "\n")

    def display_transactions(self, block: Dict, limit: int = 5):
        """Display first N transactions in the block."""
        txs = block.get('tx', [])
        if not txs:
            return

        print(f"\nTop {min(limit, len(txs))} Transactions:")
        print("-" * 60)
        for i, tx in enumerate(txs[:limit]):
            print(f"\nTx #{i+1}: {tx.get('hash')}")
            total_in = sum(inp.get('prev_out', {}).get('value', 0) for inp in tx.get('inputs', []))
            total_out = sum(out.get('value', 0) for out in tx.get('out', []))
            fee = total_in - total_out
            
            print(f"  Inputs: {len(tx.get('inputs', []))} | Outputs: {len(tx.get('out', []))}")
            print(f"  Value: {total_out / 1e8:.8f} BTC | Fee: {fee / 1e8:.8f} BTC")

    def display_watched_wallets(self):
        """Display summary of all watched addresses and clusters."""
        if not self.watched_addresses and not self.address_clusters:
            print("\nNo wallets currently being watched.")
            return

        print("\n=== WATCHED WALLETS & CLUSTERS ===")
        
        # Show individual addresses
        if self.watched_addresses:
            print("\n-- Individual Addresses --")
            for addr in self.watched_addresses:
                if addr in self.utxo_data:
                    data = self.utxo_data[addr]
                    print(f"[{addr[:12]}...{addr[-12:]}]: {data['balance']/1e8:.8f} BTC ({data['count']} UTXOs)")

        # Show clusters
        if self.address_clusters:
            print("\n-- Detected Wallet Clusters --")
            for cid, addrs in self.address_clusters.items():
                summary = self.get_wallet_summary(cid)
                if summary:
                    print(f"\nCluster #{cid}:")
                    print(f"  Total Balance: {summary['total_balance_btc']:.8f} BTC")
                    print(f"  Addresses: {summary['address_count']}")
                    print(f"  Total UTXOs: {summary['total_utxos']}")
                    if len(addrs) <= 5:
                        for a in addrs:
                            print(f"    - {a[:12]}...{a[-12:]}")
                    else:
                        print(f"    - (and {len(addrs)-5} more...)")

def main():
    scanner = BitcoinScanner()
    print("=== BITCOIN BLOCK SCANNER & UTXO STALKER ===")
    
    while True:
        print("\n--- MENU ---")
        print("1. Get Latest Block Height")
        print("2. Get Block by Height")
        print("3. Get Block by Hash")
        print("4. Scan Block Range for Clusters")
        print("5. Stalk Address UTXOs")
        print("6. View Watched Wallets/Clusters")
        print("7. Analyze Specific Transaction for Clustering")
        print("8. Exit")
        
        choice = input("\nEnter choice (1-8): ").strip()
        
        if choice == '1':
            height = scanner.get_latest_block_height()
            print(f"\nLatest Block Height: {height}")
            
        elif choice == '2':
            try:
                h = int(input("Enter block height: ").strip())
                block = scanner.get_block_by_height(h)
                scanner.display_block_info(block)
                scanner.display_transactions(block)
            except ValueError:
                print("Invalid height.")
                
        elif choice == '3':
            hsh = input("Enter block hash: ").strip()
            block = scanner.get_block_by_hash(hsh)
            scanner.display_block_info(block)
            scanner.display_transactions(block)
            
        elif choice == '4':
            try:
                start = int(input("Start height: ").strip())
                end = int(input("End height: ").strip())
                if end < start:
                    end = start + 5
                print(f"Scanning blocks {start} to {end}...")
                for h in range(start, end + 1):
                    scanner.analyze_block_for_clustering(h)
                    time.sleep(0.5) # Rate limiting
                scanner.display_watched_wallets()
            except ValueError:
                print("Invalid range.")
                
        elif choice == '5':
            addr_input = input("Enter Bitcoin address(es) (comma-separated): ").strip()
            addresses = [a.strip() for a in addr_input.split(',') if a.strip()]
            if addresses:
                scanner.stalk_utxos(addresses)
            else:
                print("No valid addresses provided.")
                
        elif choice == '6':
            scanner.display_watched_wallets()
            
        elif choice == '7':
            tx_hash = input("Enter Transaction Hash: ").strip()
            inputs = scanner.cluster_addresses_by_inputs(tx_hash)
            if len(inputs) > 1:
                print(f"Cluster detected! Addresses likely belonging to same wallet:")
                for inp in inputs:
                    print(f"  - {inp}")
            else:
                print("No multi-input cluster detected in this transaction.")
                
        elif choice == '8':
            print("Exiting scanner.")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()
