"""
Verification script for ResilienceManager.
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.resilience import retry, CircuitBreaker, CircuitBreakerOpenError

# 1. Test Retry
attempts = 0

@retry(max_attempts=3, delay=0.1)
async def failing_func():
    global attempts
    attempts += 1
    print(f"Pokušaj {attempts}...")
    raise ValueError("Bum!")

# 2. Test Circuit Breaker
cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.5)

@cb
async def cb_failing_func():
    print("Izvršavam CB funkciju koja ne uspeva...")
    raise RuntimeError("CB Greška")

async def main():
    print("\n--- Testiranje Retry Decorator-a ---")
    try:
        await failing_func()
    except ValueError:
        print(f"Uhvaćena očekivana greška nakon {attempts} pokušaja.")

    print("\n--- Testiranje Circuit Breaker-a ---")
    # First failure
    try: await cb_failing_func()
    except: print("Prvi neuspeh zabeležen.")
    
    # Second failure -> should open the circuit
    try: await cb_failing_func()
    except: print("Drugi neuspeh zabeležen. Kolo bi trebalo da se otvori.")
    
    # Third call -> should fail immediately with CircuitBreakerOpenError
    print("\nPozivam funkciju dok je kolo OTVORENO:")
    try:
        await cb_failing_func()
    except CircuitBreakerOpenError as e:
        print(f"Uspeh! Uhvaćena: {e}")
    
    # Wait for recovery
    print("\nČekam recovery timeout (0.6s)...")
    await asyncio.sleep(0.6)
    
    print("Pozivam funkciju nakon timeout-a (trebalo bi da bude HALF_OPEN):")
    try:
        await cb_failing_func()
    except Exception as e:
        print(f"Funkcija i dalje ne uspeva, ali je izvršena (stanje: {cb.state})")

if __name__ == "__main__":
    asyncio.run(main())
