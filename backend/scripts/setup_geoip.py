#!/usr/bin/env python
"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.

Script to download and setup MaxMind GeoLite2 City database.
Required for IP geolocation enrichment.

Usage:
    export MAXMIND_LICENSE_KEY="your_license_key"
    python scripts/setup_geoip.py
    
    OR
    
    python scripts/setup_geoip.py --license-key YOUR_KEY --output-dir /path/to/dir
"""

import argparse
import logging
import os
import shutil
import sys
import tarfile
from pathlib import Path

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def download_geolite2(license_key: str, output_dir: Path) -> bool:
    """
    Download and extract the GeoLite2 City database from MaxMind.
    
    Args:
        license_key: Your MaxMind license key
        output_dir: Directory to save the database file
        
    Returns:
        True if successful, False otherwise
    """
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Download URL for GeoLite2 City database
    url = (
        f"https://download.maxmind.com/app/geoip_download?"
        f"edition_id=GeoLite2-City&license_key={license_key}&suffix=tar.gz"
    )
    
    tar_path = output_dir / "GeoLite2-City.tar.gz"
    final_path = output_dir / "GeoLite2-City.mmdb"
    
    try:
        # Check if database already exists
        if final_path.exists():
            logger.info(f"✓ GeoLite2 database already exists at {final_path}")
            
            response = input("  Overwrite? (y/N): ").lower()
            if response != 'y':
                logger.info("Skipping download")
                return True
        
        # Download the file
        logger.info("Downloading GeoLite2 City database...")
        logger.info(f"  URL: {url.split('?')[0]}?...")
        
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        
        # Save the downloaded file
        logger.info(f"  Saving to: {tar_path}")
        with open(tar_path, 'wb') as f:
            f.write(response.content)
        
        logger.info(f"  Downloaded {len(response.content) / 1024 / 1024:.2f} MB")
        
        # Extract the tar.gz file
        logger.info("Extracting database file...")
        
        with tarfile.open(tar_path, 'r:gz') as tar:
            # Find the .mmdb file in the archive
            mmdb_member = None
            
            for member in tar.getmembers():
                if member.name.endswith('.mmdb'):
                    mmdb_member = member
                    logger.info(f"  Found: {member.name}")
                    break
            
            if mmdb_member is None:
                raise FileNotFoundError("Could not find .mmdb file in the archive")
            
            # Extract the .mmdb file
            tar.extract(mmdb_member, path=output_dir)
            
            # Move the file to the correct location
            extracted_path = output_dir / mmdb_member.name
            
            if final_path.exists():
                final_path.unlink()
            
            shutil.move(str(extracted_path), str(final_path))
            
            # Clean up extracted directory
            extracted_dir = extracted_path.parent
            if extracted_dir != output_dir and extracted_dir.exists():
                shutil.rmtree(extracted_dir)
        
        # Clean up the tar.gz file
        tar_path.unlink()
        
        logger.info(f"✓ GeoLite2 City database successfully downloaded to:")
        logger.info(f"  {final_path}")
        logger.info(f"  Size: {final_path.stat().st_size / 1024 / 1024:.2f} MB")
        
        return True
    
    except requests.exceptions.RequestException as e:
        logger.error(f"✗ Network error: {e}")
        
        if "401" in str(e):
            logger.error("  Invalid license key. Get one at: https://www.maxmind.com/en/geolite2/signup")
        
        return False
    
    except FileNotFoundError as e:
        logger.error(f"✗ File error: {e}")
        return False
    
    except Exception as e:
        logger.error(f"✗ Error downloading or extracting GeoLite2 database: {e}")
        return False
    
    finally:
        # Clean up tar file if it still exists
        if tar_path.exists():
            try:
                tar_path.unlink()
            except Exception:
                pass


def main():
    """Main function to set up GeoLite2 database."""
    parser = argparse.ArgumentParser(
        description='Download and set up MaxMind GeoLite2 City database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Using environment variable
  export MAXMIND_LICENSE_KEY="your_key_here"
  python scripts/setup_geoip.py
  
  # Using command line argument
  python scripts/setup_geoip.py --license-key YOUR_KEY
  
  # Custom output directory
  python scripts/setup_geoip.py --license-key YOUR_KEY --output-dir /path/to/data

Get your free license key at: https://www.maxmind.com/en/geolite2/signup
        """
    )
    
    parser.add_argument(
        '--license-key',
        help='MaxMind license key (or set MAXMIND_LICENSE_KEY env var)'
    )
    
    parser.add_argument(
        '--output-dir',
        default='data',
        help='Output directory for the database file (default: data/)'
    )
    
    args = parser.parse_args()
    
    # Get license key from args or environment
    license_key = args.license_key or os.getenv('MAXMIND_LICENSE_KEY')
    
    if not license_key:
        logger.error("✗ MaxMind license key required!")
        logger.error("\nProvide it via:")
        logger.error("  1. Environment: export MAXMIND_LICENSE_KEY='your_key'")
        logger.error("  2. Argument: --license-key YOUR_KEY")
        logger.error("\nGet a free key at: https://www.maxmind.com/en/geolite2/signup")
        sys.exit(1)
    
    # Set up output directory
    output_dir = Path(args.output_dir)
    
    logger.info("\n" + "="*60)
    logger.info("MaxMind GeoLite2 Database Setup")
    logger.info("="*60 + "\n")
    
    logger.info(f"Output directory: {output_dir.absolute()}")
    
    success = download_geolite2(license_key, output_dir)
    
    if success:
        logger.info("\n" + "="*60)
        logger.info("✓ Setup completed successfully!")
        logger.info("="*60 + "\n")
        sys.exit(0)
    else:
        logger.error("\n" + "="*60)
        logger.error("✗ Setup failed")
        logger.error("="*60 + "\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
