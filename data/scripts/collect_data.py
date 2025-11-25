#!/usr/bin/env python3
"""
Collect and prepare training data for URL phishing detection.

This script downloads phishing URLs from PhishTank and benign URLs from Tranco,
then combines and splits them into train/validation/test sets.
"""
import pandas as pd
import requests
from pathlib import Path
import logging
import argparse
import sys
from io import StringIO

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"


def download_phishing_urls(count=2500):
    """
    Download phishing URLs from PhishTank.
    
    Args:
        count: Number of phishing URLs to download
        
    Returns:
        DataFrame with columns: url, label, source
    """
    logger.info(f"Downloading up to {count} phishing URLs from PhishTank...")
    
    # PhishTank verified phishing URLs (updated hourly)
    url = "http://data.phishtank.com/data/online-valid.csv"
    
    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        
        # Save raw data
        raw_file = RAW_DIR / "phishtank_raw.csv"
        raw_file.write_text(response.text)
        logger.info(f"Saved raw PhishTank data to {raw_file}")
        
        # Parse CSV
        df = pd.read_csv(StringIO(response.text))
        
        # PhishTank CSV has columns: phish_id, url, phish_detail_url, submission_time, verified, verification_time, online, target
        if 'url' not in df.columns:
            logger.error(f"Unexpected PhishTank format. Columns: {df.columns.tolist()}")
            return pd.DataFrame()
        
        # Sample requested count
        df = df.head(count)
        
        # Create standardized format
        result_df = pd.DataFrame({
            'url': df['url'],
            'label': 1,  # 1 = phishing
            'source': 'phishtank'
        })
        
        logger.info(f"✅ Downloaded {len(result_df)} phishing URLs")
        return result_df
        
    except Exception as e:
        logger.error(f"❌ Failed to download phishing URLs: {e}")
        logger.info("You can manually download from: http://www.phishtank.com/developer_info.php")
        return pd.DataFrame()


def download_benign_urls(count=2500):
    """
    Download benign URLs from Tranco Top 1M list.
    
    Args:
        count: Number of benign URLs to download
        
    Returns:
        DataFrame with columns: url, label, source
    """
    logger.info(f"Downloading {count} benign URLs from Tranco Top 1M...")
    
    try:
        # Get latest Tranco list
        # First, get the latest list ID
        list_url = "https://tranco-list.eu/top-1m.csv.zip"
        
        response = requests.get(list_url, timeout=60)
        response.raise_for_status()
        
        # Save zip file
        zip_file = RAW_DIR / "tranco.csv.zip"
        zip_file.write_bytes(response.content)
        logger.info(f"Saved Tranco data to {zip_file}")
        
        # Read CSV from zip (Tranco format: rank,domain)
        df = pd.read_csv(zip_file, names=['rank', 'domain'], header=None)
        
        # Sample requested count
        df = df.head(count)
        
        # Convert domains to HTTPS URLs
        result_df = pd.DataFrame({
            'url': 'https://' + df['domain'],
            'label': 0,  # 0 = benign
            'source': 'tranco'
        })
        
        logger.info(f"✅ Downloaded {len(result_df)} benign URLs")
        return result_df
        
    except Exception as e:
        logger.error(f"❌ Failed to download benign URLs: {e}")
        logger.info("You can manually download from: https://tranco-list.eu/")
        return pd.DataFrame()


def combine_and_split(phishing_df, benign_df, train_ratio=0.7, val_ratio=0.15, test_ratio=0.15):
    """
    Combine phishing and benign datasets and split into train/val/test.
    
    Args:
        phishing_df: DataFrame with phishing URLs
        benign_df: DataFrame with benign URLs
        train_ratio: Proportion for training set
        val_ratio: Proportion for validation set
        test_ratio: Proportion for test set
        
    Returns:
        Tuple of (train_df, val_df, test_df)
    """
    logger.info("Combining and splitting datasets...")
    
    # Combine
    df = pd.concat([phishing_df, benign_df], ignore_index=True)
    logger.info(f"Combined dataset: {len(df)} URLs ({len(phishing_df)} phishing, {len(benign_df)} benign)")
    
    # Shuffle with fixed seed for reproducibility
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Calculate split indices
    n = len(df)
    train_end = int(train_ratio * n)
    val_end = int((train_ratio + val_ratio) * n)
    
    # Split
    train_df = df[:train_end]
    val_df = df[train_end:val_end]
    test_df = df[val_end:]
    
    # Verify class balance
    logger.info(f"\nDataset Statistics:")
    logger.info(f"  Train: {len(train_df)} URLs (Phishing: {train_df['label'].sum()}, Benign: {len(train_df) - train_df['label'].sum()})")
    logger.info(f"  Val:   {len(val_df)} URLs (Phishing: {val_df['label'].sum()}, Benign: {len(val_df) - val_df['label'].sum()})")
    logger.info(f"  Test:  {len(test_df)} URLs (Phishing: {test_df['label'].sum()}, Benign: {len(test_df) - test_df['label'].sum()})")
    
    # Save to CSV
    train_path = PROCESSED_DIR / "train.csv"
    val_path = PROCESSED_DIR / "val.csv"
    test_path = PROCESSED_DIR / "test.csv"
    
    train_df.to_csv(train_path, index=False)
    val_df.to_csv(val_path, index=False)
    test_df.to_csv(test_path, index=False)
    
    logger.info(f"\n✅ Saved datasets:")
    logger.info(f"  Train: {train_path}")
    logger.info(f"  Val:   {val_path}")
    logger.info(f"  Test:  {test_path}")
    
    return train_df, val_df, test_df


def main():
    """Main data collection pipeline."""
    parser = argparse.ArgumentParser(description='Collect training data for URL phishing detection')
    parser.add_argument('--phishing-count', type=int, default=2500, help='Number of phishing URLs to download')
    parser.add_argument('--benign-count', type=int, default=2500, help='Number of benign URLs to download')
    parser.add_argument('--skip-download', action='store_true', help='Skip download and use existing raw data')
    
    args = parser.parse_args()
    
    # Create directories
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    
    if args.skip_download:
        logger.info("Skipping download, loading from raw files...")
        try:
            phishing_df = pd.read_csv(RAW_DIR / "phishtank_raw.csv")
            phishing_df = phishing_df.head(args.phishing_count)
            phishing_df = pd.DataFrame({
                'url': phishing_df['url'],
                'label': 1,
                'source': 'phishtank'
            })
            
            benign_df = pd.read_csv(RAW_DIR / "tranco.csv.zip", names=['rank', 'domain'], header=None)
            benign_df = benign_df.head(args.benign_count)
            benign_df = pd.DataFrame({
                'url': 'https://' + benign_df['domain'],
                'label': 0,
                'source': 'tranco'
            })
        except Exception as e:
            logger.error(f"Failed to load raw data: {e}")
            sys.exit(1)
    else:
        # Download data
        phishing_df = download_phishing_urls(count=args.phishing_count)
        benign_df = download_benign_urls(count=args.benign_count)
    
    # Validate downloads
    if phishing_df.empty or benign_df.empty:
        logger.error("❌ Failed to download data. Exiting.")
        logger.info("\nTroubleshooting:")
        logger.info("1. Check your internet connection")
        logger.info("2. Try downloading manually:")
        logger.info("   - PhishTank: http://www.phishtank.com/developer_info.php")
        logger.info("   - Tranco: https://tranco-list.eu/")
        logger.info("3. Place downloaded files in data/raw/ and run with --skip-download")
        sys.exit(1)
    
    # Combine and split
    train_df, val_df, test_df = combine_and_split(phishing_df, benign_df)
    
    logger.info("\n" + "="*60)
    logger.info("✅ Data collection complete!")
    logger.info("="*60)
    logger.info(f"\nNext steps:")
    logger.info(f"1. Inspect the data: head {PROCESSED_DIR}/train.csv")
    logger.info(f"2. Train the model: cd backend/app/ml && python train.py")
    logger.info("="*60)


if __name__ == "__main__":
    main()
