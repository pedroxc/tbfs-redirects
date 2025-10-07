import pandas as pd
import re
from urllib.parse import urlparse

def extract_slug_from_url(url):
    """Extract meaningful slug from URL"""
    try:
        parsed = urlparse(url)
        path = parsed.path.strip('/')
        if path:
            # Get the last meaningful part
            parts = path.split('/')
            return parts[-1] if parts[-1] else (parts[-2] if len(parts) > 1 else '')
        return ''
    except:
        return ''

def is_blog_url(url):
    """Check if URL is blog-related"""
    blog_indicators = [
        '/blog/', 'crossdressing', 'tutorial', 'tips', 'guide', 'how-to',
        'transgender', 'feminization', 'makeup', 'beauty', 'story', 'experience'
    ]
    url_lower = url.lower()
    return any(indicator in url_lower for indicator in blog_indicators)

def find_blog_match(old_url, blog_urls):
    """Find best matching blog URL"""
    old_slug = extract_slug_from_url(old_url)
    
    if not old_slug:
        return None
    
    # Direct matches
    for blog_url in blog_urls:
        blog_slug = extract_slug_from_url(blog_url)
        if old_slug == blog_slug:
            return blog_url
    
    # Partial matches
    for blog_url in blog_urls:
        blog_slug = extract_slug_from_url(blog_url)
        if old_slug in blog_slug or blog_slug in old_slug:
            return blog_url
    
    # Keyword matches
    old_keywords = re.findall(r'\b\w+\b', old_slug.replace('-', ' '))
    best_match = None
    best_score = 0
    
    for blog_url in blog_urls:
        blog_slug = extract_slug_from_url(blog_url)
        blog_keywords = re.findall(r'\b\w+\b', blog_slug.replace('-', ' '))
        
        # Count matching keywords
        matches = len(set(old_keywords) & set(blog_keywords))
        if matches > best_score:
            best_score = matches
            best_match = blog_url
    
    return best_match if best_score > 0 else None

def create_blog_redirects():
    """Create corrected blog redirects"""
    print("Loading data...")
    
    # Load old URLs
    old_df = pd.read_csv(r'c:\Users\Pedro\Desktop\tbfs-sitemap\old\old.csv')
    old_urls = old_df['url'].tolist()
    
    # Load new URLs
    new_df = pd.read_csv(r'c:\Users\Pedro\Desktop\tbfs-sitemap\new\new.csv')
    new_urls = new_df['url'].tolist()
    
    # Filter blog URLs from new site
    blog_urls = [url for url in new_urls if '/blogs/' in url]
    print(f"Found {len(blog_urls)} blog URLs in new site")
    
    # Find blog URLs from old site
    old_blog_urls = [url for url in old_urls if is_blog_url(url)]
    print(f"Found {len(old_blog_urls)} blog URLs in old site")
    
    # Create blog redirects
    blog_redirects = []
    matched_count = 0
    
    for old_url in old_blog_urls:
        path = old_url.replace('https://thebreastformstore.com', '')
        
        # Find best match
        best_match = find_blog_match(old_url, blog_urls)
        
        if best_match:
            matched_count += 1
            target = best_match
        else:
            # Use category-specific fallbacks
            if any(x in old_url.lower() for x in ['beauty', 'makeup', 'feminine']):
                target = 'https://tbfsna.myshopify.com/blogs/beauty'
            elif any(x in old_url.lower() for x in ['tips', 'crossdressing', 'tutorial']):
                target = 'https://tbfsna.myshopify.com/blogs/cd-tg-tips'
            elif any(x in old_url.lower() for x in ['breast-form', 'bra', 'lingerie']):
                target = 'https://tbfsna.myshopify.com/blogs/breast-forms-breast-form-care'
            elif any(x in old_url.lower() for x in ['body', 'shaping', 'curve']):
                target = 'https://tbfsna.myshopify.com/blogs/body-shaping'
            else:
                target = 'https://tbfsna.myshopify.com/blogs/community-stories'
        
        blog_redirects.append({
            'path': path,
            'target': target,
            'old_url': old_url,
            'matched': best_match is not None
        })
    
    print(f"Matched {matched_count} blog URLs directly")
    print(f"Created {len(blog_redirects)} blog redirects")
    
    # Convert to DataFrame
    blog_df = pd.DataFrame(blog_redirects)
    
    # Save detailed analysis
    blog_df.to_excel('blog_redirects_corrected.xlsx', index=False)
    print("Saved blog redirects to: blog_redirects_corrected.xlsx")
    
    # Create Shopify import files (only path and target columns)
    shopify_df = blog_df[['path', 'target']].copy()
    
    # Create batches
    batch_size = 250
    total_batches = (len(shopify_df) + batch_size - 1) // batch_size
    
    for i in range(total_batches):
        start_idx = i * batch_size
        end_idx = min((i + 1) * batch_size, len(shopify_df))
        batch_df = shopify_df.iloc[start_idx:end_idx]
        
        batch_filename = f'blog_redirects_batch_{i+1}.csv'
        batch_df.to_csv(batch_filename, index=False)
        print(f"Created batch {i+1}: {len(batch_df)} redirects -> {batch_filename}")
    
    # Show distribution
    print(f"\nBlog redirect distribution:")
    target_counts = blog_df['target'].value_counts()
    for target, count in target_counts.items():
        print(f"  {target}: {count} redirects")
    
    # Test specific case
    test_url = "https://thebreastformstore.com/crossdressing-101-how-to-walk-in-high-heels/"
    test_match = find_blog_match(test_url, blog_urls)
    print(f"\nTest case:")
    print(f"  Old: {test_url}")
    print(f"  Found match: {test_match}")
    
    return blog_df

if __name__ == "__main__":
    create_blog_redirects()