#!/usr/bin/env python3
"""
Extended Hidden Number Problem (HNP) Attack Workflow

This script demonstrates how to use the Extended HNP implementation to recover
(EC)DSA private keys when partial nonce bits are known.

Based on: Hlavac M., Rosa T., "Extended Hidden Number Problem and Its Cryptanalytic Applications"
Source: https://github.com/jvdsn/crypto-attacks

REQUIREMENTS: SageMath (install with: apt-get install sagemath)
"""

import sys

# Check for SageMath
try:
    from sage.all import ZZ, QQ
    SAGE_AVAILABLE = True
except ImportError:
    SAGE_AVAILABLE = False
    print("⚠️  WARNING: SageMath is not installed.")
    print("   Install with: sudo apt-get install sagemath")
    print("   Or run this script with: sage -python extended_hnp_workflow.py")
    print()

# Add workspace to path for imports
sys.path.insert(0, '/workspace')

# Import extended_hnp only if SageMath is available
if SAGE_AVAILABLE:
    from extended_hnp import dsa_known_bits, attack
    from shared.partial_integer import PartialInteger
else:
    # Define stub classes for documentation purposes
    dsa_known_bits = None
    attack = None
    
    class PartialInteger:
        def __init__(self):
            pass
        def add_unknown(self, bit_length):
            return self
        def add_known(self, value, bit_length):
            return self


def example_dsa_known_bits():
    """
    Example: Recover DSA private key with known nonce bits
    
    This demonstrates a basic scenario where we have:
    - Multiple DSA signatures (h, r, s values)
    - Partial knowledge of the nonces used
    - Partial knowledge of the private key (optional)
    """
    print("=" * 70)
    print("Extended HNP Attack - DSA Known Bits Example")
    print("=" * 70)
    
    if not SAGE_AVAILABLE:
        print("\n❌ Cannot run example: SageMath required")
        return
    
    # Parameters (example values - replace with real data)
    N = ZZ(2**256 - 2**32 - 977)  # Example modulus (secp256k1 order)
    
    # Example signature data (replace with actual signatures)
    # In practice, you would extract these from blockchain transactions
    h = [ZZ(0x1234567890abcdef), ZZ(0xfedcba0987654321)]  # Hashed messages
    r = [ZZ(0x1111111111111111), ZZ(0x2222222222222222)]  # r values
    s = [ZZ(0x3333333333333333), ZZ(0x4444444444444444)]  # s values
    
    # Construct partial private key (can be fully unknown)
    # Example: private key with some known bits
    x = PartialInteger()
    x.add_unknown(256)  # Fully unknown 256-bit private key
    
    # Construct partial nonces
    # Example: nonces with some known bits (e.g., from side-channel leakage)
    k_list = []
    for i in range(len(h)):
        ki = PartialInteger()
        # Example: know top 4 bits of each nonce
        ki.add_known(i, 4)
        ki.add_unknown(252)  # Remaining bits unknown
        k_list.append(ki)
    
    print(f"\nModulus N: {N}")
    print(f"Number of signatures: {len(h)}")
    print(f"Private key structure: {x.unknowns} unknown component(s)")
    print(f"Nonce structures:")
    for i, ki in enumerate(k_list):
        print(f"  k[{i}]: {ki.unknowns} unknown component(s), {ki.bit_length} total bits")
    
    print("\nRunning attack...")
    
    try:
        results = list(dsa_known_bits(N, h, r, s, x, k_list))
        
        if results:
            print(f"\n✓ Found {len(results)} candidate private key(s):")
            for i, key in enumerate(results):
                print(f"  Candidate {i+1}: {hex(key)}")
        else:
            print("\n✗ No candidates found (may need more signatures or better bit knowledge)")
            
    except Exception as e:
        print(f"\n✗ Attack failed: {e}")
        print("\nNote: This example uses dummy data. For real attacks:")
        print("  1. Use actual signature data from blockchain")
        print("  2. Ensure you have enough signatures")
        print("  3. Verify the known bit patterns are accurate")


def example_custom_attack():
    """
    Example: Direct use of the attack() function for custom scenarios
    
    This allows more fine-grained control over the attack parameters.
    """
    print("\n" + "=" * 70)
    print("Extended HNP Attack - Custom Parameters Example")
    print("=" * 70)
    
    if not SAGE_AVAILABLE:
        print("\n❌ Cannot run example: SageMath required")
        return
    
    # These parameters would be derived from your specific cryptanalytic scenario
    # See the paper for detailed parameter definitions
    
    N = ZZ(2**256 - 2**32 - 977)
    x_ = ZZ(0)  # Known bits of x
    
    # Pi and nu values (bit positions and lengths for known parts)
    pi = [0, 100]  # Bit positions
    nu = [10, 10]  # Bit lengths at those positions
    
    # Alpha, rho, mu, beta values
    a = [ZZ(1), ZZ(2)]
    p = [[ZZ(1), ZZ(2)], [ZZ(3), ZZ(4)]]
    u = [[5, 5], [5, 5]]
    b = [ZZ(100), ZZ(200)]
    
    print(f"\nAttack parameters:")
    print(f"  Modulus N: {N}")
    print(f"  Known x bits: {x_}")
    print(f"  Pi positions: {pi}")
    print(f"  Nu lengths: {nu}")
    print(f"  Alpha values: {a}")
    print(f"  Beta values: {b}")
    
    print("\nRunning custom attack...")
    
    try:
        results = list(attack(x_, N, pi, nu, a, p, u, b))
        
        if results:
            print(f"\n✓ Found {len(results)} candidate solution(s)")
            for i, sol in enumerate(results):
                print(f"  Solution {i+1}: {sol}")
        else:
            print("\n✗ No solutions found")
            
    except Exception as e:
        print(f"\n✗ Attack failed: {e}")


def workflow_guide():
    """Print a step-by-step guide for using the Extended HNP attack."""
    print("=" * 70)
    print("EXTENDED HNP ATTACK WORKFLOW GUIDE")
    print("=" * 70)
    print("""
STEP 1: COLLECT DATA
  - Gather (EC)DSA signatures (r, s, hash values)
  - Identify source of partial nonce information (side-channel, bias, etc.)
  
STEP 2: ANALYZE KNOWN BITS
  - Determine which bits of nonces are known/unknown
  - Map bit positions and lengths
  - Create PartialInteger objects for nonces
  
STEP 3: SETUP ATTACK
  - Choose appropriate modulus N (curve order)
  - Construct PartialInteger for private key (fully or partially unknown)
  - Prepare signature lists: h, r, s, k
  
STEP 4: EXECUTE ATTACK
  - Call dsa_known_bits(N, h, r, s, x, k)
  - Iterate through candidate private keys
  
STEP 5: VERIFY RESULTS
  - Test candidates against known public keys
  - Validate with additional signatures if available

REQUIREMENTS:
  - SageMath (for lattice operations)
  - Sufficient number of signatures
  - Accurate partial nonce information

TIPS:
  - More signatures generally improve success rate
  - More known bits per nonce reduces required signatures
  - Accuracy of known bit positions is critical
""")


if __name__ == "__main__":
    print("\n🔐 Extended Hidden Number Problem Attack Workflow\n")
    
    workflow_guide()
    
    print("\n" + "=" * 70)
    print("RUNNING EXAMPLES")
    print("=" * 70)
    
    # Run examples
    example_dsa_known_bits()
    example_custom_attack()
    
    print("\n" + "=" * 70)
    print("WORKFLOW COMPLETE")
    print("=" * 70)
