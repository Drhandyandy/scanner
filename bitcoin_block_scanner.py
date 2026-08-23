#!/usr/bin/env python3
"""
Bitcoin Block Scanner with UTXO Stalking and Wallet Grouping
Fetches real-time data from Blockchain.com API.
Features:
- Scan blocks by height, hash, or range
- Track UTXOs for specific addresses
- Group wallet data by clustering heuristics
- Analyze transaction flows
- Display RAW JSON data
- Export all data to CSV files organized by sections
"""

import requests
import time
import json
import csv
import os
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Set, Optional

API_BASE = "https://blockchain.info"
HEADERS = {'User-Agent': 'Mozilla/5.0'}

# Create export directory
EXPORT_DIR = "bitcoin_data_exports"
os.makedirs(EXPORT_DIR, exist_ok=True)

class BitcoinScanner:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.watched_addresses: Set[str] = set()
        self.address_clusters: Dict[int, Set[str]] = defaultdict(set)
        self.utxo_data: Dict[str, Dict] = {}  # address -> utxos
        
        # Data buffers for CSV export
        self.blocks_buffer: List[Dict] = []
        self.transactions_buffer: List[Dict] = []
        self.utxos_buffer: List[Dict] = []
        self.clusters_buffer: List[Dict] = []
        
    def make_request(self, url: str, params: Optional[Dict] = None) -> Dict:
        """Make API request with error handling."""
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            return {}
    
    def _display_raw_json(self, data: Dict, title: str = "RAW DATA"):
        """Display raw JSON data in formatted way."""
        print("\n" + "="*80)
        print(f"=== {title} ===")
        print("="*80)
        print(json.dumps(data, indent=2))
        print("="*80 + "\n")
    
    def _buffer_block_data(self, block: Dict):
        """Buffer block data for CSV export."""
        if not block:
            return
        
        coinbase_tx = block.get('tx', [{}])[0]
        coinbase_output = sum(out.get('value', 0) for out in coinbase_tx.get('out', []))
        subsidy = 50 * 1e8
        fees = coinbase_output - subsidy
        
        total_output = sum(
            out.get('value', 0) 
            for tx in block.get('tx', []) 
            for out in tx.get('out', [])
        )
        
        self.blocks_buffer.append({
            'timestamp': datetime.now().isoformat(),
            'height': block.get('height'),
            'hash': block.get('hash'),
            'time': block.get('time'),
            'time_formatted': datetime.fromtimestamp(block.get('time', 0)).strftime('%Y-%m-%d %H:%M:%S') if block.get('time') else '',
            'size': block.get('size'),
            'weight': block.get('weight'),
            'difficulty': block.get('difficulty'),
            'transaction_count': len(block.get('tx', [])),
            'total_output_btc': total_output / 1e8,
            'estimated_fees_btc': fees / 1e8,
            'nonce': block.get('nonce'),
            'bits': block.get('bits'),
            'merkle_root': block.get('mrkl_root'),
            'prev_block': block.get('prev_block')
        })
    
    def _buffer_transaction_data(self, tx: Dict, block_height: int = None):
        """Buffer transaction data for CSV export."""
        if not tx:
            return
        
        total_in = sum(inp.get('prev_out', {}).get('value', 0) for inp in tx.get('inputs', []))
        total_out = sum(out.get('value', 0) for out in tx.get('out', []))
        fee = total_in - total_out
        
        inputs_list = []
        outputs_list = []
        
        for inp in tx.get('inputs', []):
            prev_out = inp.get('prev_out', {})
            inputs_list.append(prev_out.get('addr', ''))
        
        for out in tx.get('out', []):
            outputs_list.append(f"{out.get('addr', '')}:{out.get('value', 0)}")
        
        self.transactions_buffer.append({
            'timestamp': datetime.now().isoformat(),
            'tx_hash': tx.get('hash'),
            'block_height': block_height or tx.get('block_height'),
            'time': tx.get('time'),
            'time_formatted': datetime.fromtimestamp(tx.get('time', 0)).strftime('%Y-%m-%d %H:%M:%S') if tx.get('time') else '',
            'size': tx.get('size'),
            'weight': tx.get('weight'),
            'fee_btc': fee / 1e8,
            'total_input_btc': total_in / 1e8,
            'total_output_btc': total_out / 1e8,
            'input_count': len(tx.get('inputs', [])),
            'output_count': len(tx.get('out', [])),
            'inputs': ';'.join(inputs_list[:10]),  # First 10 inputs
            'outputs': ';'.join(outputs_list[:10])  # First 10 outputs
        })
    
    def _buffer_utxo_data(self, address: str, utxos: List[Dict], balance: int):
        """Buffer UTXO data for CSV export."""
        for i, utxo in enumerate(utxos):
            self.utxos_buffer.append({
                'timestamp': datetime.now().isoformat(),
                'address': address,
                'utxo_index': i,
                'tx_hash': utxo.get('tx_hash_big_endian') or utxo.get('tx_hash'),
                'tx_output_n': utxo.get('tx_output_n'),
                'value_btc': utxo.get('value', 0) / 1e8,
                'value_satoshi': utxo.get('value', 0),
                'confirmations': utxo.get('confirmations'),
                'script': utxo.get('script')
            })
    
    def _buffer_cluster_data(self, cluster_id: int, addresses: Set[str]):
        """Buffer cluster data for CSV export."""
        total_balance = 0
        total_utxos = 0
        
        for addr in addresses:
            if addr in self.utxo_data:
                total_balance += self.utxo_data[addr]['balance']
                total_utxos += self.utxo_data[addr]['count']
        
        self.clusters_buffer.append({
            'timestamp': datetime.now().isoformat(),
            'cluster_id': cluster_id,
            'address_count': len(addresses),
            'total_balance_btc': total_balance / 1e8,
            'total_balance_satoshi': total_balance,
            'total_utxos': total_utxos,
            'addresses': ';'.join(list(addresses)[:20])  # First 20 addresses
        })
    
    def export_all_to_csv(self):
        """Export all buffered data to CSV files organized by sections."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        exported_files = []
        
        # Export Blocks
        if self.blocks_buffer:
            filename = os.path.join(EXPORT_DIR, f"blocks_{timestamp}.csv")
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.blocks_buffer[0].keys())
                writer.writeheader()
                writer.writerows(self.blocks_buffer)
            exported_files.append(filename)
            print(f"✓ Exported {len(self.blocks_buffer)} blocks to {filename}")
        
        # Export Transactions
        if self.transactions_buffer:
            filename = os.path.join(EXPORT_DIR, f"transactions_{timestamp}.csv")
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.transactions_buffer[0].keys())
                writer.writeheader()
                writer.writerows(self.transactions_buffer)
            exported_files.append(filename)
            print(f"✓ Exported {len(self.transactions_buffer)} transactions to {filename}")
        
        # Export UTXOs
        if self.utxos_buffer:
            filename = os.path.join(EXPORT_DIR, f"utxos_{timestamp}.csv")
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.utxos_buffer[0].keys())
                writer.writeheader()
                writer.writerows(self.utxos_buffer)
            exported_files.append(filename)
            print(f"✓ Exported {len(self.utxos_buffer)} UTXOs to {filename}")
        
        # Export Clusters
        if self.clusters_buffer:
            filename = os.path.join(EXPORT_DIR, f"wallet_clusters_{timestamp}.csv")
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.clusters_buffer[0].keys())
                writer.writeheader()
                writer.writerows(self.clusters_buffer)
            exported_files.append(filename)
            print(f"✓ Exported {len(self.clusters_buffer)} clusters to {filename}")
        
        # Export Watched Addresses Summary
        if self.watched_addresses:
            watched_data = []
            for addr in self.watched_addresses:
                if addr in self.utxo_data:
                    watched_data.append({
                        'timestamp': datetime.now().isoformat(),
                        'address': addr,
                        'balance_btc': self.utxo_data[addr]['balance'] / 1e8,
                        'balance_satoshi': self.utxo_data[addr]['balance'],
                        'utxo_count': self.utxo_data[addr]['count'],
                        'last_updated': self.utxo_data[addr]['last_updated']
                    })
            
            if watched_data:
                filename = os.path.join(EXPORT_DIR, f"watched_addresses_{timestamp}.csv")
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=watched_data[0].keys())
                    writer.writeheader()
                    writer.writerows(watched_data)
                exported_files.append(filename)
                print(f"✓ Exported {len(watched_data)} watched addresses to {filename}")
        
        if not exported_files:
            print("No data to export yet. Scan some blocks or stalk some addresses first.")
        else:
            print(f"\nAll data exported to {EXPORT_DIR}/ directory!")
        
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
    
    def get_block_by_height(self, height: int, show_raw: bool = True) -> Dict:
        """Fetch block data by height."""
        block = self.make_request(f"{API_BASE}/block/{height}?format=json")
        if block and show_raw:
            self._display_raw_json(block, f"RAW BLOCK DATA - Height {height}")
            self._buffer_block_data(block)
            # Buffer transactions too
            for tx in block.get('tx', [])[:10]:  # First 10 transactions
                self._buffer_transaction_data(tx, height)
        return block
    
    def get_block_by_hash(self, block_hash: str, show_raw: bool = True) -> Dict:
        """Fetch block data by hash."""
        block = self.make_request(f"{API_BASE}/rawblock/{block_hash}")
        if block and show_raw:
            self._display_raw_json(block, f"RAW BLOCK DATA - Hash {block_hash[:16]}...")
            self._buffer_block_data(block)
            for tx in block.get('tx', [])[:10]:
                self._buffer_transaction_data(tx, block.get('height'))
        return block
    
    def get_address_details(self, address: str, show_raw: bool = True) -> Dict:
        """Get detailed information about an address."""
        data = self.make_request(f"{API_BASE}/rawaddr/{address}")
        if data and show_raw:
            self._display_raw_json(data, f"RAW ADDRESS DATA - {address[:12]}...{address[-12:]}")
        return data
    
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
            
            # Display raw UTXO data
            self._display_raw_json({'address': addr, 'unspent_outputs': utxos}, f"RAW UTXO DATA - {addr[:12]}...{addr[-12:]}")
            
            # Buffer UTXO data for CSV
            self._buffer_utxo_data(addr, utxos, total_balance)
            
            if verbose:
                print(f"  - Balance: {total_balance / 1e8:.8f} BTC")
                print(f"  - UTXO Count: {len(utxos)}")
                
            results[addr] = self.utxo_data[addr]
        return results
    
    def cluster_addresses_by_inputs(self, tx_hash: str, show_raw: bool = True) -> Set[str]:
        """
        Heuristic: If multiple addresses are inputs in the same transaction,
        they likely belong to the same wallet/entity.
        """
        time.sleep(0.2)  # Rate limiting
        tx_data = self.make_request(f"{API_BASE}/rawtx/{tx_hash}")
        if not tx_data or 'inputs' not in tx_data:
            return set()
        
        if show_raw:
            self._display_raw_json(tx_data, f"RAW TRANSACTION DATA - {tx_hash[:16]}...")
        
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
            # Buffer cluster data
            self._buffer_cluster_data(cluster_id, input_addresses)
            
        return input_addresses
    
    def analyze_block_for_clustering(self, height: int) -> Dict[int, Set[str]]:
        """Scan a block and identify potential wallet clusters based on common inputs."""
        block = self.get_block_by_height(height, show_raw=False)  # Already shown if called directly
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
                
            inputs = self.cluster_addresses_by_inputs(tx_hash, show_raw=False)
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
    print("Features: RAW JSON display + CSV export organized by sections")
    print(f"Export directory: {EXPORT_DIR}/")
    
    while True:
        print("\n--- MENU ---")
        print("1. Get Latest Block Height")
        print("2. Get Block by Height (shows RAW JSON + buffers for CSV)")
        print("3. Get Block by Hash (shows RAW JSON + buffers for CSV)")
        print("4. Scan Block Range for Clusters")
        print("5. Stalk Address UTXOs (shows RAW JSON + buffers for CSV)")
        print("6. View Watched Wallets/Clusters")
        print("7. Analyze Transaction for Clustering (shows RAW JSON)")
        print("8. EXPORT ALL DATA TO CSV")
        print("9. Exit")
        
        choice = input("\nEnter choice (1-9): ").strip()
        
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
                print(f"\nCluster detected! Addresses likely belonging to same wallet:")
                for inp in inputs:
                    print(f"  - {inp}")
            else:
                print("No multi-input cluster detected in this transaction.")
                
        elif choice == '8':
            print("\n" + "="*60)
            print("EXPORTING DATA TO CSV...")
            print("="*60)
            scanner.export_all_to_csv()
            
        elif choice == '9':
            print("Exiting scanner.")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()
