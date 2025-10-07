import pandas as pd
import re
from urllib.parse import urlparse
import os

def extract_slug(url):
    """Extract the last part of URL path as slug"""
    parsed = urlparse(url)
    path = parsed.path.strip('/')
    if path:
        return path.split('/')[-1]
    return ''

def extract_keywords(url):
    """Extract keywords for categorization"""
    url_lower = url.lower()
    
    # Blog-related keywords
    blog_keywords = [
        'blog', 'tips', 'tutorial', 'guide', 'how-to', 'crossdressing', 
        'transgender', 'feminization', 'makeup', 'beauty', 'stories', 
        'community', 'experience', 'coming-out', 'gender'
    ]
    
    # Product-related keywords
    product_keywords = [
        'breast-form', 'bra', 'wig', 'shoe', 'heel', 'lingerie', 'panty',
        'adhesive', 'tape', 'size', 'color', 'brand', 'style', 'product'
    ]
    
    # Check for blog keywords
    for keyword in blog_keywords:
        if keyword in url_lower:
            return 'blog'
    
    # Check for product keywords
    for keyword in product_keywords:
        if keyword in url_lower:
            return 'product'
    
    # Check URL structure patterns
    if '/blog/' in url_lower or '/blogs/' in url_lower:
        return 'blog'
    elif any(x in url_lower for x in ['product', 'shop', 'store', 'brand', 'size']):
        return 'product'
    
    return 'other'

def find_best_match(old_url, new_urls):
    """Find the best matching new URL for an old URL"""
    old_slug = extract_slug(old_url)
    old_category = extract_keywords(old_url)
    
    # Direct slug matches
    for new_url in new_urls:
        new_slug = extract_slug(new_url)
        if old_slug and new_slug and old_slug == new_slug:
            return new_url
    
    # Partial slug matches
    if old_slug:
        for new_url in new_urls:
            new_slug = extract_slug(new_url)
            if new_slug and (old_slug in new_slug or new_slug in old_slug):
                return new_url
    
    # Category-based fallbacks
    category_fallbacks = {
        'blog': [
            'https://tbfsna.myshopify.com/blogs/community-stories',
            'https://tbfsna.myshopify.com/blogs/cd-tg-tips',
            'https://tbfsna.myshopify.com/blogs/beauty',
            'https://tbfsna.myshopify.com/blogs/breast-forms-breast-form-care'
        ],
        'product': [
            'https://tbfsna.myshopify.com/collections/breast-forms',
            'https://tbfsna.myshopify.com/collections/bras-and-lingerie',
            'https://tbfsna.myshopify.com/collections/wigs',
            'https://tbfsna.myshopify.com/collections/shoes-and-boots'
        ]
    }
    
    # Return category fallback
    fallbacks = category_fallbacks.get(old_category, [])
    if fallbacks:
        return fallbacks[0]
    
    # Default fallback
    return 'https://tbfsna.myshopify.com/'

def create_redirects():
    """Create comprehensive redirect mapping"""
    print("Loading CSV files...")
    
    # Load old URLs
    old_df = pd.read_csv(r'c:\Users\Pedro\Desktop\tbfs-sitemap\old\old.csv')
    old_urls = old_df['url'].tolist()
    
    # Load new URLs
    new_df = pd.read_csv(r'c:\Users\Pedro\Desktop\tbfs-sitemap\new\new.csv')
    new_urls = new_df['url'].tolist()
    
    print(f"Loaded {len(old_urls)} old URLs and {len(new_urls)} new URLs")
    
    # Create redirects
    redirects = []
    
    for i, old_url in enumerate(old_urls):
        if i % 500 == 0:
            print(f"Processing URL {i+1}/{len(old_urls)}")
        
        # Skip if already new domain
        if 'tbfsna.myshopify.com' in old_url:
            continue
        
        # Find best match
        new_url = find_best_match(old_url, new_urls)
        
        redirects.append({
            'path': old_url.replace('https://thebreastformstore.com', ''),
            'target': new_url
        })
    
    # Convert to DataFrame
    redirects_df = pd.DataFrame(redirects)
    
    # Remove duplicates
    redirects_df = redirects_df.drop_duplicates(subset=['path'])
    
    print(f"Created {len(redirects_df)} unique redirects")
    
    # Analyze redirect distribution
    print("\nRedirect Distribution:")
    target_counts = redirects_df['target'].value_counts()
    for target, count in target_counts.head(10).items():
        print(f"  {target}: {count} redirects")
    
    # Save main file
    output_file = 'shopify_redirects_comprehensive.xlsx'
    redirects_df.to_excel(output_file, index=False)
    print(f"\nSaved comprehensive redirects to: {output_file}")
    
    # Create batches for Shopify import (250 redirects per file)
    batch_size = 250
    total_batches = (len(redirects_df) + batch_size - 1) // batch_size
    
    print(f"\nCreating {total_batches} batch files...")
    
    for i in range(total_batches):
        start_idx = i * batch_size
        end_idx = min((i + 1) * batch_size, len(redirects_df))
        batch_df = redirects_df.iloc[start_idx:end_idx]
        
        batch_filename = f'shopify_redirects_batch_{i+1}.csv'
        batch_df.to_csv(batch_filename, index=False)
        print(f"  Batch {i+1}: {len(batch_df)} redirects -> {batch_filename}")
    
    # Create summary statistics
    print(f"\n=== REDIRECT SUMMARY ===")
    print(f"Total old URLs processed: {len(old_urls)}")
    print(f"Total new URLs available: {len(new_urls)}")
    print(f"Total redirects created: {len(redirects_df)}")
    print(f"Batch files created: {total_batches}")
    print(f"Redirects per batch: {batch_size}")
    
    # Save detailed analysis
    analysis_data = []
    for old_url in old_urls[:100]:  # Sample first 100 for detailed analysis
        if 'tbfsna.myshopify.com' not in old_url:
            new_url = find_best_match(old_url, new_urls)
            category = extract_keywords(old_url)
            slug = extract_slug(old_url)
            
            analysis_data.append({
                'old_url': old_url,
                'new_url': new_url,
                'category': category,
                'old_slug': slug,
                'new_slug': extract_slug(new_url)
            })
    
    analysis_df = pd.DataFrame(analysis_data)
    analysis_df.to_excel('redirect_analysis_sample.xlsx', index=False)
    print(f"\nSaved analysis sample to: redirect_analysis_sample.xlsx")

if __name__ == "__main__":
    create_redirects()