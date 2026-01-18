import pandas as pd
import numpy as np
from pathlib import Path


def analyze_accident_data(accident_file: str):
    """Comprehensive analysis of Karnataka accident dataset."""
    
    print("="*70)
    print("KARNATAKA ACCIDENT DATASET ANALYSIS")
    print("="*70)
    
    try:
        # Load data
        df = pd.read_csv(accident_file, encoding='utf-8')

        print(f"\n✓ Successfully loaded: {accident_file}")
        print(f"  Total records: {len(df):,}")
        
        # Column overview
        print(f"\n{'='*70}")
        print("COLUMN OVERVIEW")
        print(f"{'='*70}")
        print(f"Total columns: {len(df.columns)}")
        print(f"\nAll columns:")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i:2d}. {col}")
        
        # Check for critical columns
        print(f"\n{'='*70}")
        print("CRITICAL COLUMNS CHECK")
        print(f"{'='*70}")
        
        critical_cols = {
            'Latitude': 'Latitude' in df.columns,
            'Longitude': 'Longitude' in df.columns,
            'Severity': 'Severity' in df.columns,
            'Year': 'Year' in df.columns,
            'DISTRICTNAME': 'DISTRICTNAME' in df.columns
        }
        
        for col, exists in critical_cols.items():
            status = "✓ Found" if exists else "✗ Missing"
            print(f"  {status}: {col}")
        
        # Coordinate validation
        if 'Latitude' in df.columns and 'Longitude' in df.columns:
            print(f"\n{'='*70}")
            print("COORDINATE VALIDATION")
            print(f"{'='*70}")
            
            total = len(df)
            valid_coords = df.dropna(subset=['Latitude', 'Longitude'])
            
            # Karnataka bounds: roughly 11.5-18.5 N, 74-78.5 E
            in_karnataka = valid_coords[
                (valid_coords['Latitude'] >= 11.5) & 
                (valid_coords['Latitude'] <= 18.5) &
                (valid_coords['Longitude'] >= 74.0) & 
                (valid_coords['Longitude'] <= 78.5)
            ]
            
            print(f"  Total records: {total:,}")
            print(f"  With coordinates: {len(valid_coords):,} ({len(valid_coords)/total*100:.1f}%)")
            print(f"  Within Karnataka bounds: {len(in_karnataka):,} ({len(in_karnataka)/total*100:.1f}%)")
            print(f"  Invalid/Missing: {total - len(in_karnataka):,} ({(total-len(in_karnataka))/total*100:.1f}%)")
            
            if len(in_karnataka) > 0:
                print(f"\n  Coordinate ranges:")
                print(f"    Latitude:  {in_karnataka['Latitude'].min():.4f} to {in_karnataka['Latitude'].max():.4f}")
                print(f"    Longitude: {in_karnataka['Longitude'].min():.4f} to {in_karnataka['Longitude'].max():.4f}")
        
        # Severity analysis
        if 'Severity' in df.columns:
            print(f"\n{'='*70}")
            print("SEVERITY BREAKDOWN")
            print(f"{'='*70}")
            
            severity_counts = df['Severity'].value_counts()
            print(f"\n  Total severity categories: {len(severity_counts)}")
            print(f"\n  Distribution:")
            
            for severity, count in severity_counts.items():
                pct = count / len(df) * 100
                bar = "█" * int(pct / 2)
                print(f"    {severity:30s}: {count:5,} ({pct:5.1f}%) {bar}")
        
        # Year distribution
        if 'Year' in df.columns:
            print(f"\n{'='*70}")
            print("TEMPORAL COVERAGE")
            print(f"{'='*70}")
            
            year_counts = df['Year'].value_counts().sort_index()
            print(f"\n  Year range: {year_counts.index.min()} to {year_counts.index.max()}")
            print(f"\n  Records per year:")
            
            for year, count in year_counts.items():
                pct = count / len(df) * 100
                bar = "█" * int(pct / 3)
                print(f"    {year}: {count:5,} ({pct:5.1f}%) {bar}")
        
        # District distribution
        if 'DISTRICTNAME' in df.columns:
            print(f"\n{'='*70}")
            print("DISTRICT DISTRIBUTION (Top 15)")
            print(f"{'='*70}")
            
            district_counts = df['DISTRICTNAME'].value_counts().head(15)
            print(f"\n  Total unique districts: {df['DISTRICTNAME'].nunique()}")
            print(f"\n  Top districts:")
            
            for district, count in district_counts.items():
                pct = count / len(df) * 100
                bar = "█" * int(pct / 2)
                print(f"    {district:25s}: {count:5,} ({pct:5.1f}%) {bar}")
        
        # Main cause analysis
        if 'Main_Cause' in df.columns:
            print(f"\n{'='*70}")
            print("TOP ACCIDENT CAUSES (Top 10)")
            print(f"{'='*70}")
            
            cause_counts = df['Main_Cause'].value_counts().head(10)
            
            for cause, count in cause_counts.items():
                pct = count / len(df) * 100
                cause_short = cause[:40] if isinstance(cause, str) else str(cause)
                print(f"    {cause_short:40s}: {count:5,} ({pct:5.1f}%)")
        
        # Data quality summary
        print(f"\n{'='*70}")
        print("DATA QUALITY SUMMARY")
        print(f"{'='*70}")
        
        missing_summary = []
        for col in ['Latitude', 'Longitude', 'Severity', 'Year', 'DISTRICTNAME']:
            if col in df.columns:
                missing = df[col].isna().sum()
                missing_pct = missing / len(df) * 100
                missing_summary.append((col, missing, missing_pct))
        
        print(f"\n  Missing values:")
        for col, missing, pct in missing_summary:
            status = "✓ Good" if pct < 5 else "⚠ Warning" if pct < 20 else "✗ Poor"
            print(f"    {status} {col:20s}: {missing:5,} ({pct:5.1f}%)")
        
        # Usability assessment
        print(f"\n{'='*70}")
        print("SENTIMENT ANALYSIS USABILITY")
        print(f"{'='*70}")
        
        usable = len(in_karnataka) if 'Latitude' in df.columns else 0
        usability_score = (usable / len(df) * 100) if len(df) > 0 else 0
        
        print(f"\n  Records usable for sentiment: {usable:,} / {len(df):,} ({usability_score:.1f}%)")
        
        if usability_score > 80:
            print(f"  ✓ Excellent - Dataset is highly suitable for sentiment analysis")
        elif usability_score > 60:
            print(f"  ⚠ Good - Dataset is suitable with minor gaps")
        elif usability_score > 40:
            print(f"  ⚠ Fair - Dataset can be used but has significant gaps")
        else:
            print(f"  ✗ Poor - Dataset has too many missing/invalid coordinates")
        
        print(f"\n  Recommendations:")
        if usability_score < 80:
            print(f"    • Clean data to remove records with missing coordinates")
            print(f"    • Verify coordinate accuracy for outliers")
        if 'Severity' in df.columns and df['Severity'].isna().sum() > 0:
            print(f"    • Fill missing severity values or use default weighting")
        
        print(f"\n{'='*70}")
        print("ANALYSIS COMPLETE")
        print(f"{'='*70}\n")
        
        return df
        
    except FileNotFoundError:
        print(f"\n✗ Error: File not found: {accident_file}")
        print(f"  Please check the file path and try again.\n")
        return None
        
    except Exception as e:
        print(f"\n✗ Error loading data: {e}\n")
        return None


if __name__ == '__main__':
    # Run analysis
    accident_file = 'data/karnataka_accidents.csv'
    
    # Check if file exists
    if not Path(accident_file).exists():
        print("\n⚠ File not found!")
        print(f"  Looking for: {accident_file}")
        print(f"\n  Please place your accident CSV in the data/ folder")
        print(f"  Expected location: backend/sentiment/data/karnataka_accidents.csv\n")
    else:
        df = analyze_accident_data(accident_file)
        
        if df is not None:
            print("\n💡 TIP: This dataset is ready to use with the multi-source sentiment framework!")
            print("   Next step: python test_accident_sentiment.py\n")