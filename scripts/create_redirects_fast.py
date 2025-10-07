import pandas as pd
import re
from urllib.parse import urlparse
import os

def extract_slug(url):
    """Extract the last part of URL path as slug"""
    try:
        parsed = urlparse(url)
        path = parsed.path.strip('/')
        if path:
            return path.split('/')[-1]
        return ''
    except:
        return ''

def categorize_url(url):
    """Quick categorization of URLs"""
    url_lower = url.lower()
    
    if '/blog' in url_lower or 'crossdressing' in url_lower or 'tutorial' in url_lower:
        return 'blog'
    elif any(x in url_lower for x in ['breast-form', 'bra', 'wig', 'product', 'brand', 'size']):
        return 'product'
    else:
        return 'other'

def create_redirects_optimized():
    """Create redirects with optimized performance"""
    print("Loading CSV files...")
    
    # Load old URLs
    old_df = pd.read_csv(r'c:\Users\Pedro\Desktop\tbfs-sitemap\old\old.csv')
    old_urls = old_df['url'].tolist()
    
    # Load new URLs
    new_df = pd.read_csv(r'c:\Users\Pedro\Desktop\tbfs-sitemap\new\new.csv')
    new_urls = new_df['url'].tolist()
    
    print(f"Loaded {len(old_urls)} old URLs and {len(new_urls)} new URLs")
    
    # Pre-process new URLs for faster lookup
    new_slugs = {}
    blog_urls = []
    product_urls = []
    
    for url in new_urls:
        slug = extract_slug(url)
        if slug:
            new_slugs[slug] = url
        
        if '/blogs/' in url:
            blog_urls.append(url)
        elif '/collections/' in url or '/products/' in url:
            product_urls.append(url)
    
    print(f"Indexed {len(new_slugs)} new URL slugs")
    
    # Define fallback URLs
    fallback_urls = {
        'blog': 'https://tbfsna.myshopify.com/blogs/community-stories',
        'product': 'https://tbfsna.myshopify.com/collections/breast-forms',
        'other': 'https://tbfsna.myshopify.com/'
    }
    
    # Create redirects
    redirects = []
    
    for i, old_url in enumerate(old_urls):
        if i % 1000 == 0:
            print(f"Processing URL {i+1}/{len(old_urls)}")
        
        # Skip if already new domain
        if 'tbfsna.myshopify.com' in old_url:
            continue
        
        # Extract path for redirect
        path = old_url.replace('https://thebreastformstore.com', '')
        old_slug = extract_slug(old_url)
        category = categorize_url(old_url)
        
        # Find matching new URL
        new_url = None
        
        # Try direct slug match first
        if old_slug and old_slug in new_slugs:
            new_url = new_slugs[old_slug]
        else:
            # Try partial matches
            if old_slug:
                for new_slug, url in new_slugs.items():
                    if old_slug in new_slug or new_slug in old_slug:
                        new_url = url
                        break
        
        # Use fallback if no match found
        if not new_url:
            new_url = fallback_urls[category]
        
        redirects.append({
            'path': path,
            'target': new_url
        })
    
    # Convert to DataFrame
    redirects_df = pd.DataFrame(redirects)
    
    # Remove duplicates
    redirects_df = redirects_df.drop_duplicates(subset=['path'])
    
    print(f"Created {len(redirects_df)} unique redirects")
    
    # Save main file
    output_file = 'shopify_redirects_new.xlsx'
    redirects_df.to_excel(output_file, index=False)
    print(f"Saved redirects to: {output_file}")
    
    # Create batches for Shopify import (250 redirects per file)
    batch_size = 250
    total_batches = (len(redirects_df) + batch_size - 1) // batch_size
    
    print(f"Creating {total_batches} batch files...")
    
    for i in range(total_batches):
        start_idx = i * batch_size
        end_idx = min((i + 1) * batch_size, len(redirects_df))
        batch_df = redirects_df.iloc[start_idx:end_idx]
        
        batch_filename = f'shopify_batch_{i+1}_new.csv'
        batch_df.to_csv(batch_filename, index=False)
        print(f"  Batch {i+1}: {len(batch_df)} redirects -> {batch_filename}")
    
    # Analyze redirect distribution
    print(f"\n=== REDIRECT SUMMARY ===")
    print(f"Total redirects created: {len(redirects_df)}")
    print(f"Batch files created: {total_batches}")
    
    print("\nTop redirect targets:")
    target_counts = redirects_df['target'].value_counts()
    for target, count in target_counts.head(10).items():
        print(f"  {target}: {count} redirects")
    
    return redirects_df

if __name__ == "__main__":
    create_redirects_optimized()