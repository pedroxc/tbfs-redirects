import pandas as pd
import re
from urllib.parse import urlparse

def fix_redirect_format():
    """Fix redirects to use relative paths instead of full URLs"""
    print("Fixing redirect format to use relative paths...")
    
    # Load the main Excel file
    df = pd.read_excel('shopify_redirects_FINAL.xlsx')
    
    print(f"Processing {len(df)} redirects...")
    
    # Convert full URLs to relative paths
    for i, row in df.iterrows():
        target_url = row['target']
        
        # Extract path from full URL
        if target_url.startswith('https://tbfsna.myshopify.com'):
            # Extract just the path part
            parsed = urlparse(target_url)
            relative_path = parsed.path
            df.at[i, 'target'] = relative_path
        elif target_url == 'https://tbfsna.myshopify.com/':
            # Homepage becomes just /
            df.at[i, 'target'] = '/'
        
        if i % 1000 == 0:
            print(f"Processed {i+1}/{len(df)} redirects")
    
    print("Fixed all redirects to use relative paths")
    
    # Show examples
    print("\nExamples of fixed redirects:")
    for i in range(min(10, len(df))):
        print(f"  {df.iloc[i]['path']} => {df.iloc[i]['target']}")
    
    # Save corrected Excel file
    df.to_excel('shopify_redirects_CORRECTED.xlsx', index=False)
    print("\nSaved corrected file: shopify_redirects_CORRECTED.xlsx")
    
    # Create new batch files with corrected format
    batch_size = 250
    total_batches = (len(df) + batch_size - 1) // batch_size
    
    print(f"\nCreating {total_batches} corrected batch files...")
    
    for i in range(total_batches):
        start_idx = i * batch_size
        end_idx = min((i + 1) * batch_size, len(df))
        batch_df = df.iloc[start_idx:end_idx]
        
        batch_filename = f'shopify_CORRECTED_batch_{i+1}.csv'
        batch_df.to_csv(batch_filename, index=False)
        print(f"  Batch {i+1}: {len(batch_df)} redirects -> {batch_filename}")
    
    # Show target distribution
    print(f"\nTop redirect targets (relative paths):")
    target_counts = df['target'].value_counts()
    for target, count in target_counts.head(10).items():
        print(f"  {target}: {count} redirects")
    
    return df

if __name__ == "__main__":
    fix_redirect_format()