"""
TwinSecure - Advanced Cybersecurity Platform
Copyright © 2024 TwinSecure. All rights reserved.

This file is part of TwinSecure, a proprietary cybersecurity platform.
Unauthorized copying, distribution, modification, or use of this software
is strictly prohibited without explicit written permission.

For licensing inquiries: kunalsingh2514@gmail.com
"""

import os
import requests
import tarfile
import shutil
from pathlib import Path
import logging
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_geolite2(license_key: str, output_dir: Path) -> None:
    """
    Download and extract the GeoLite2 City database.
    
    Args:
        license_key: Your MaxMind license key
        output_dir: Directory to save the database file
    """
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Download URL for GeoLite2 City database
    url = f"https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-City&license_key={license_key}&suffix=tar.gz"
    
    try:
        # Download the file
        logger.info("Downloading GeoLite2 City database...")
        response = requests.get(url)
        response.raise_for_status()
        
        # Save the downloaded file
        tar_path = output_dir / "GeoLite2-City.tar.gz"
        with open(tar_path, 'wb') as f:
            f.write(response.content)
        
        # Extract the tar.gz file
        logger.info("Extracting database file...")
        with tarfile.open(tar_path, 'r:gz') as tar:
            # Find the .mmdb file in the archive
            mmdb_file = None
            for member in tar.getmembers():
                if member.name.endswith('.mmdb'):
                    mmdb_file = member
                    break
            
            if mmdb_file is None:
                raise Exception("Could not find .mmdb file in the archive")
            
            # Extract the .mmdb file
            tar.extract(mmdb_file, path=output_dir)
            
            # Move the file to the correct location
            extracted_path = output_dir / mmdb_file.name
            final_path = output_dir / "GeoLite2-City.mmdb"
            shutil.move(extracted_path, final_path)
        
        # Clean up the tar.gz file
        tar_path.unlink()
        
        logger.info(f"GeoLite2 City database successfully downloaded and extracted to {final_path}")
        
    except Exception as e:
        logger.error(f"Error downloading or extracting GeoLite2 database: {e}")
        raise

def main():
    """Main function to set up GeoLite2 database."""
    parser = argparse.ArgumentParser(description='Download and set up GeoLite2 database')
    parser.add_argument('--license-key', required=True, help='MaxMind license key')
    parser.add_argument('--output-dir', default='E:/ts', help='Output directory for the database file')
    args = parser.parse_args()
    
    # Set up output directory
    output_dir = Path(args.output_dir)
    
    try:
        download_geolite2(args.license_key, output_dir)
    except Exception as e:
        logger.error(f"Failed to set up GeoLite2 database: {e}")
        return

if __name__ == "__main__":
    main() 