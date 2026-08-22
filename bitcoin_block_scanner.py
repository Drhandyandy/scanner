#!/usr/bin/env python3
"""
Bitcoin Block Scanner

A simple tool to scan and display information about Bitcoin blocks
using the Blockchain.com API.
"""

import requests
import json
from datetime import datetime


class BitcoinBlockScanner:
    """Scanner for retrieving and displaying Bitcoin block information."""

    API_BASE_URL = "https://blockchain.info"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; BitcoinBlockScanner/1.0)'
        })

    def get_latest_block_height(self) -> int:
        """Get the current latest block height."""
        try:
            response = self.session.get(f"{self.API_BASE_URL}/q/getblockcount")
            response.raise_for_status()
            return int(response.text.strip())
        except requests.RequestException as e:
            print(f"Error fetching latest block height: {e}")
            return -1

    def get_block_hash(self, height: int) -> str:
        """Get block hash for a given height."""
        try:
            response = self.session.get(f"{self.API_BASE_URL}/block-height/{height}?format=json")
            response.raise_for_status()
            data = response.json()
            if 'blocks' in data and len(data['blocks']) > 0:
                return data['blocks'][0]['hash']
            return None
        except requests.RequestException as e:
            print(f"Error fetching block hash for height {height}: {e}")
            return None

    def get_block_info(self, block_hash: str = None, height: int = None) -> dict:
        """
        Get detailed information about a block.
        
        Args:
            block_hash: The hash of the block
            height: The height of the block (used if hash not provided)
        
        Returns:
            Dictionary containing block information
        """
        try:
            if block_hash:
                url = f"{self.API_BASE_URL}/rawblock/{block_hash}"
            elif height is not None:
                url = f"{self.API_BASE_URL}/block-height/{height}"
            else:
                print("Error: Either block_hash or height must be provided")
                return None

            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()

            # If querying by height, extract the first block
            if height is not None and 'blocks' in data:
                if len(data['blocks']) == 0:
                    print(f"No block found at height {height}")
                    return None
                data = data['blocks'][0]

            return self._parse_block_data(data)

        except requests.RequestException as e:
            print(f"Error fetching block info: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return None

    def _parse_block_data(self, raw_data: dict) -> dict:
        """Parse raw block data into a more readable format."""
        parsed = {
            'hash': raw_data.get('hash', 'N/A'),
            'height': raw_data.get('height', 'N/A'),
            'time': raw_data.get('time', 0),
            'datetime': datetime.fromtimestamp(raw_data.get('time', 0)).strftime('%Y-%m-%d %H:%M:%S') if raw_data.get('time') else 'N/A',
            'previous_block': raw_data.get('prev_block', 'N/A'),
            'merkle_root': raw_data.get('mrkl_root', 'N/A'),
            'size': raw_data.get('size', 0),
            'weight': raw_data.get('weight', 0),
            'version': raw_data.get('ver', 0),
            'nonce': raw_data.get('nonce', 0),
            'bits': raw_data.get('bits', 0),
            'difficulty': raw_data.get('difficulty', 0),
            'n_tx': raw_data.get('n_tx', 0),
            'total_fees': raw_data.get('fee', 0),
            'reward': raw_data.get('reward', 0),
            'relayed_by': raw_data.get('relayed_by', 'N/A'),
            'main_chain': raw_data.get('main_chain', False),
            'transaction_count': len(raw_data.get('tx', [])),
        }
        return parsed

    def display_block_info(self, block_info: dict):
        """Display block information in a formatted way."""
        if not block_info:
            print("No block information to display.")
            return

        print("\n" + "=" * 70)
        print("BITCOIN BLOCK INFORMATION")
        print("=" * 70)
        print(f"Hash:              {block_info['hash']}")
        print(f"Height:            {block_info['height']}")
        print(f"Timestamp:         {block_info['datetime']} (Unix: {block_info['time']})")
        print(f"Previous Block:    {block_info['previous_block']}")
        print(f"Merkle Root:       {block_info['merkle_root']}")
        print("-" * 70)
        print(f"Size:              {block_info['size']} bytes")
        print(f"Weight:            {block_info['weight']} weight units")
        print(f"Version:           {block_info['version']}")
        print(f"Nonce:             {block_info['nonce']}")
        print(f"Bits:              {block_info['bits']}")
        print(f"Difficulty:        {block_info['difficulty']:.2f}")
        print("-" * 70)
        print(f"Transactions:      {block_info['transaction_count']} (n_tx: {block_info['n_tx']})")
        print(f"Total Fees:        {block_info['total_fees']} satoshis ({block_info['total_fees'] / 100000000:.8f} BTC)")
        print(f"Block Reward:      {block_info['reward']} satoshis ({block_info['reward'] / 100000000:.8f} BTC)")
        print(f"Relayed By:        {block_info['relayed_by']}")
        print(f"Main Chain:        {block_info['main_chain']}")
        print("=" * 70 + "\n")

    def get_transactions(self, block_hash: str, limit: int = 10) -> list:
        """Get transactions from a block."""
        try:
            response = self.session.get(f"{self.API_BASE_URL}/rawblock/{block_hash}")
            response.raise_for_status()
            data = response.json()
            
            transactions = data.get('tx', [])
            limited_txs = transactions[:limit]
            
            tx_list = []
            for tx in limited_txs:
                tx_info = {
                    'hash': tx.get('hash', 'N/A'),
                    'size': tx.get('size', 0),
                    'weight': tx.get('weight', 0),
                    'version': tx.get('ver', 0),
                    'lock_time': tx.get('lock_time', 0),
                    'input_count': len(tx.get('inputs', [])),
                    'output_count': len(tx.get('out', [])),
                }
                tx_list.append(tx_info)
            
            return tx_list

        except requests.RequestException as e:
            print(f"Error fetching transactions: {e}")
            return []

    def display_transactions(self, transactions: list):
        """Display transaction information."""
        if not transactions:
            print("No transactions to display.")
            return

        print(f"\nTRANSACTIONS (showing {len(transactions)}):")
        print("-" * 70)
        for i, tx in enumerate(transactions, 1):
            print(f"\n{i}. Hash: {tx['hash']}")
            print(f"   Size: {tx['size']} bytes | Weight: {tx['weight']}")
            print(f"   Inputs: {tx['input_count']} | Outputs: {tx['output_count']}")
            print(f"   Version: {tx['version']} | Lock Time: {tx['lock_time']}")
        print("-" * 70 + "\n")

    def scan_range(self, start_height: int, end_height: int):
        """Scan a range of blocks and display summary information."""
        print(f"\nScanning blocks from {start_height} to {end_height}...")
        print("=" * 70)
        
        for height in range(start_height, end_height + 1):
            block_info = self.get_block_info(height=height)
            if block_info:
                print(f"Height: {block_info['height']:7d} | "
                      f"Hash: {block_info['hash'][:16]}... | "
                      f"TXs: {block_info['transaction_count']:4d} | "
                      f"Time: {block_info['datetime']}")
            else:
                print(f"Height: {height:7d} | Failed to retrieve block info")
        
        print("=" * 70 + "\n")


def main():
    """Main function to run the Bitcoin Block Scanner."""
    scanner = BitcoinBlockScanner()
    
    print("\n" + "=" * 70)
    print("BITCOIN BLOCK SCANNER")
    print("=" * 70)
    
    while True:
        print("\nOptions:")
        print("1. Get latest block height")
        print("2. Get block by height")
        print("3. Get block by hash")
        print("4. Scan block range")
        print("5. Get transactions from block")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            height = scanner.get_latest_block_height()
            if height > 0:
                print(f"\nLatest block height: {height}")
        
        elif choice == '2':
            try:
                height = int(input("Enter block height: ").strip())
                block_info = scanner.get_block_info(height=height)
                scanner.display_block_info(block_info)
            except ValueError:
                print("Invalid height. Please enter a number.")
        
        elif choice == '3':
            block_hash = input("Enter block hash: ").strip()
            if block_hash:
                block_info = scanner.get_block_info(block_hash=block_hash)
                scanner.display_block_info(block_info)
        
        elif choice == '4':
            try:
                start = int(input("Enter start height: ").strip())
                end = int(input("Enter end height: ").strip())
                if start <= end:
                    scanner.scan_range(start, end)
                else:
                    print("Start height must be less than or equal to end height.")
            except ValueError:
                print("Invalid height. Please enter numbers.")
        
        elif choice == '5':
            block_input = input("Enter block hash or height: ").strip()
            try:
                height = int(block_input)
                block_hash = scanner.get_block_hash(height)
                if not block_hash:
                    print("Could not retrieve block hash.")
                    continue
            except ValueError:
                block_hash = block_input
            
            try:
                limit = int(input("Number of transactions to display (default 10): ").strip() or "10")
                transactions = scanner.get_transactions(block_hash, limit)
                scanner.display_transactions(transactions)
            except ValueError:
                print("Invalid number. Using default limit of 10.")
                transactions = scanner.get_transactions(block_hash, 10)
                scanner.display_transactions(transactions)
        
        elif choice == '6':
            print("\nExiting Bitcoin Block Scanner. Goodbye!\n")
            break
        
        else:
            print("Invalid choice. Please enter a number between 1 and 6.")


if __name__ == "__main__":
    main()
