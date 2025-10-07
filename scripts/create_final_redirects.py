import pandas as pd
import re

def create_final_redirects():
    """Create final comprehensive redirects with manual fixes"""
    print("Creating final comprehensive redirects...")
    
    # Load the main redirect file
    main_df = pd.read_excel('shopify_redirects_new.xlsx')
    
    # Load blog redirects
    blog_df = pd.read_excel('blog_redirects_corrected.xlsx')
    blog_redirects = blog_df[['path', 'target']].copy()
    
    print(f"Main redirects: {len(main_df)}")
    print(f"Blog redirects: {len(blog_redirects)}")
    
    # Combine redirects, prioritizing blog redirects for blog URLs
    final_redirects = []
    blog_paths = set(blog_redirects['path'].tolist())
    
    # Add blog redirects first
    for _, row in blog_redirects.iterrows():
        final_redirects.append({
            'path': row['path'],
            'target': row['target']
        })
    
    # Add non-blog redirects from main file
    for _, row in main_df.iterrows():
        if row['path'] not in blog_paths:
            final_redirects.append({
                'path': row['path'],
                'target': row['target']
            })
    
    # Add manual fixes for specific cases
    manual_fixes = {
        '/crossdressing-101-how-to-walk-in-high-heels/': 'https://tbfsna.myshopify.com/blogs/community-stories/crossdressing-101-how-to-walk-in-high-heels',
        '/crossdressing-101-how-to-walk-in-high-heels': 'https://tbfsna.myshopify.com/blogs/community-stories/crossdressing-101-how-to-walk-in-high-heels',
        '/tag/crossdressing-101-how-to-walk-in-high-heels/': 'https://tbfsna.myshopify.com/blogs/community-stories/crossdressing-101-how-to-walk-in-high-heels'
    }
    
    # Apply manual fixes
    existing_paths = {redirect['path'] for redirect in final_redirects}
    for path, target in manual_fixes.items():
        if path not in existing_paths:
            final_redirects.append({
                'path': path,
                'target': target
            })
            print(f"Added manual fix: {path} -> {target}")
    
    # Convert to DataFrame
    final_df = pd.DataFrame(final_redirects)
    
    # Remove duplicates, keeping first occurrence
    final_df = final_df.drop_duplicates(subset=['path'], keep='first')
    
    print(f"Final redirects count: {len(final_df)}")
    
    # Save comprehensive file
    final_df.to_excel('shopify_redirects_FINAL.xlsx', index=False)
    print("Saved final redirects to: shopify_redirects_FINAL.xlsx")
    
    # Create final batches for Shopify import
    batch_size = 250
    total_batches = (len(final_df) + batch_size - 1) // batch_size
    
    print(f"Creating {total_batches} final batch files...")
    
    for i in range(total_batches):
        start_idx = i * batch_size
        end_idx = min((i + 1) * batch_size, len(final_df))
        batch_df = final_df.iloc[start_idx:end_idx]
        
        batch_filename = f'shopify_FINAL_batch_{i+1}.csv'
        batch_df.to_csv(batch_filename, index=False)
        print(f"  Final Batch {i+1}: {len(batch_df)} redirects -> {batch_filename}")
    
    # Show statistics
    print(f"\n=== FINAL REDIRECT SUMMARY ===")
    print(f"Total final redirects: {len(final_df)}")
    print(f"Final batch files: {total_batches}")
    
    print(f"\nTop redirect targets:")
    target_counts = final_df['target'].value_counts()
    for target, count in target_counts.head(10).items():
        print(f"  {target}: {count}")
    
    # Test the specific case
    test_paths = [
        '/crossdressing-101-how-to-walk-in-high-heels/',
        '/crossdressing-101-how-to-walk-in-high-heels',
        '/tag/crossdressing-101-how-to-walk-in-high-heels/'
    ]
    
    print(f"\nTest cases:")
    for test_path in test_paths:
        match = final_df[final_df['path'] == test_path]
        if not match.empty:
            print(f"  {test_path} -> {match.iloc[0]['target']}")
        else:
            print(f"  {test_path} -> NOT FOUND")
    
    return final_df

if __name__ == "__main__":
    create_final_redirects()