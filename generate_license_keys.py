#!/usr/bin/env python3
"""
TwinSecure License Key Generator
Copyright © 2024 TwinSecure. All rights reserved.

This script generates license keys for TwinSecure customers.
Contact: kunalsingh2514@gmail.com
"""

import random
import string
import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path


class LicenseKeyGenerator:
    """Generates and manages TwinSecure license keys."""

    def __init__(self):
        self.prefix = "TS"
        self.generated_keys = set()
        self.load_existing_keys()

    def load_existing_keys(self):
        """Load previously generated keys to avoid duplicates."""
        keys_file = Path("generated_license_keys.json")
        if keys_file.exists():
            try:
                with open(keys_file, 'r') as f:
                    data = json.load(f)
                    self.generated_keys = set(data.get('keys', []))
            except Exception:
                pass

    def save_generated_keys(self):
        """Save generated keys to file."""
        keys_file = Path("generated_license_keys.json")
        data = {
            'keys': list(self.generated_keys),
            'generated_at': datetime.now().isoformat(),
            'total_count': len(self.generated_keys)
        }
        with open(keys_file, 'w') as f:
            json.dump(data, f, indent=2)

    def generate_segment(self, length=4):
        """Generate a random alphanumeric segment."""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

    def generate_key(self, license_type="DEMO", customer_name="", unique_id=""):
        """Generate a unique license key."""
        attempts = 0
        max_attempts = 100

        while attempts < max_attempts:
            if license_type == "DEMO":
                key = f"{self.prefix}-DEMO-{self.generate_segment()}-{self.generate_segment()}"
            elif license_type == "PERSONAL":
                key = f"{self.prefix}-PERSONAL-{self.generate_segment()}-{self.generate_segment()}"
            elif license_type == "COMMERCIAL":
                key = f"{self.prefix}-COMMERCIAL-{self.generate_segment()}-{self.generate_segment()}"
            elif license_type == "ENTERPRISE":
                key = f"{self.prefix}-ENTERPRISE-{self.generate_segment()}-{self.generate_segment()}"
            elif license_type == "CUSTOM":
                # Custom key with customer name
                name_part = customer_name.upper().replace(" ", "")[:8] if customer_name else "CUSTOM"
                key = f"{self.prefix}-{name_part}-{self.generate_segment()}-{self.generate_segment()}"
            else:
                # Generic key
                key = f"{self.prefix}-{self.generate_segment()}-{self.generate_segment()}-{self.generate_segment()}"

            if key not in self.generated_keys:
                self.generated_keys.add(key)
                return key

            attempts += 1

        raise Exception("Could not generate unique key after maximum attempts")

    def generate_batch(self, count=10, license_type="DEMO"):
        """Generate a batch of license keys."""
        keys = []
        for i in range(count):
            try:
                key = self.generate_key(license_type)
                keys.append(key)
            except Exception as e:
                print(f"Error generating key {i+1}: {e}")

        return keys

    def create_license_info(self, key, license_type, customer_info=None):
        """Create detailed license information."""
        return {
            'license_key': key,
            'license_type': license_type,
            'generated_at': datetime.now().isoformat(),
            'customer_info': customer_info or {},
            'status': 'active',
            'features': self.get_features_for_type(license_type)
        }

    def get_features_for_type(self, license_type):
        """Get features available for each license type."""
        features = {
            'DEMO': {
                'ml_enabled': True,
                'api_access': True,
                'advanced_analytics': True,
                'max_users': 1,
                'expires_days': 7
            },
            'PERSONAL': {
                'ml_enabled': True,
                'api_access': True,
                'advanced_analytics': False,
                'max_users': 1,
                'expires_days': 365
            },
            'COMMERCIAL': {
                'ml_enabled': True,
                'api_access': True,
                'advanced_analytics': True,
                'max_users': 10,
                'expires_days': 365
            },
            'ENTERPRISE': {
                'ml_enabled': True,
                'api_access': True,
                'advanced_analytics': True,
                'max_users': -1,  # Unlimited
                'expires_days': 365
            }
        }
        return features.get(license_type, features['DEMO'])


def main():
    """Main function to generate license keys."""
    generator = LicenseKeyGenerator()

    print("🔑 TwinSecure License Key Generator")
    print("=" * 50)
    print("Contact: kunalsingh2514@gmail.com")
    print()

    # Generate demo keys
    print("📋 Demo/Testing Keys:")
    demo_keys = [
        "TS-DEMO-2024-KUNAL-SINGH",
        "TS-DEV-UNLIMITED-ACCESS",
        "TS-CREATOR-KUNAL-SINGH-2024",
        "TS-TRIAL-BYPASS-KEY-2024"
    ]

    for key in demo_keys:
        print(f"  {key}")
        generator.generated_keys.add(key)

    print()

    # Generate new keys for different license types
    license_types = ['DEMO', 'PERSONAL', 'COMMERCIAL', 'ENTERPRISE']

    for license_type in license_types:
        print(f"🎫 {license_type} License Keys:")
        keys = generator.generate_batch(3, license_type)
        for key in keys:
            print(f"  {key}")
        print()

    # Generate custom keys for specific customers
    print("👤 Custom Customer Keys:")
    custom_customers = [
        ("John Smith", "PERSONAL"),
        ("Acme Corp", "COMMERCIAL"),
        ("TechStart Inc", "ENTERPRISE")
    ]

    for customer_name, license_type in custom_customers:
        key = generator.generate_key("CUSTOM", customer_name)
        print(f"  {customer_name}: {key}")

    print()

    # Save all generated keys
    generator.save_generated_keys()

    # Create license database
    license_db = []
    for key in generator.generated_keys:
        if key.startswith("TS-DEMO"):
            license_type = "DEMO"
        elif key.startswith("TS-PERSONAL"):
            license_type = "PERSONAL"
        elif key.startswith("TS-COMMERCIAL"):
            license_type = "COMMERCIAL"
        elif key.startswith("TS-ENTERPRISE"):
            license_type = "ENTERPRISE"
        else:
            license_type = "CUSTOM"

        license_info = generator.create_license_info(key, license_type)
        license_db.append(license_info)

    # Save license database
    with open("license_database.json", 'w') as f:
        json.dump(license_db, f, indent=2)

    print("💾 Files Created:")
    print("  - generated_license_keys.json (key list)")
    print("  - license_database.json (detailed license info)")
    print()

    print("🚀 Usage Instructions:")
    print("  1. Choose a license key from above")
    print("  2. Set environment variable:")
    print("     export TWINSECURE_LICENSE_KEY=\"TS-DEMO-2024-KUNAL-SINGH\"")
    print("  3. Start TwinSecure:")
    print("     cd backend && python -m uvicorn app.main:app --reload")
    print()

    print("📧 For customer licenses, contact: kunalsingh2514@gmail.com")
    print(f"📊 Total keys generated: {len(generator.generated_keys)}")


if __name__ == "__main__":
    main()
