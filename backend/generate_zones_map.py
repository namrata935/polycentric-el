"""
Standalone script to generate zones CSV and interactive map.
This script uses the zone classification logic to create visualizations.
"""
import os
import sys
from dotenv import load_dotenv
import pandas as pd
import folium
from app import create_app, db
from app.services.zone_service import get_zones_classified

# Load environment variables
load_dotenv()

def color_zone(zone_type: str) -> str:
    """Get color for zone type"""
    if zone_type == "Commercial Zone":
        return "red"
    elif zone_type == "Balanced Zone":
        return "orange"
    return "blue"


def main():
    """Generate zones CSV and map"""
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        try:
            print("🔄 Processing zones...")
            
            # Get classified zones
            zones = get_zones_classified()
            
            if len(zones) == 0:
                print("❌ No zones found. Make sure you have loaded business and transit data.")
                print("   Run: python load_business_data.py")
                print("   Run: python load_transit_data.py")
                sys.exit(1)
            
            # STEP 10: SUMMARY PRINT
            print("\n📊 ZONE SUMMARY")
            print(f"Total zones: {len(zones)}")
            print(zones["zone_type"].value_counts())
            
            # STEP 11: SAVE CSV
            csv_path = "zones_classified_fixed.csv"
            zones.to_csv(csv_path, index=False)
            print(f"\n✅ CSV saved: {csv_path}")
            
            # STEP 12: CREATE MAP
            # Calculate center point
            center_lat = zones["zone_lat"].mean()
            center_lon = zones["zone_lon"].mean()
            
            m = folium.Map(
                location=[center_lat, center_lon],
                zoom_start=11,
                tiles="CartoDB positron"
            )
            
            # Add zones to map
            for _, row in zones.iterrows():
                folium.CircleMarker(
                    location=[row["zone_lat"], row["zone_lon"]],
                    radius=5 + row["zone_score"] * 12,
                    color=color_zone(row["zone_type"]),
                    fill=True,
                    fill_opacity=0.75,
                    popup=folium.Popup(
                        f"""
                        <b>Zone ({row['zone_lat']:.2f}, {row['zone_lon']:.2f})</b><br>
                        Type: {row['zone_type']}<br>
                        Score: {row['zone_score']:.2f}<br>
                        Businesses: {int(row['business_count'])}<br>
                        Transport Nodes: {int(row['transport_count'])}<br>
                        Estimated Population: {int(row['population'])}
                        """,
                        max_width=300
                    )
                ).add_to(m)
            
            # Add legend
            legend_html = '''
            <div style="position: fixed; 
                        bottom: 50px; left: 50px; width: 200px; height: 120px; 
                        background-color: white; border:2px solid grey; z-index:9999; 
                        font-size:14px; padding: 10px">
            <h4>Zone Types</h4>
            <p><span style="color:red;">●</span> Commercial Zone</p>
            <p><span style="color:orange;">●</span> Balanced Zone</p>
            <p><span style="color:blue;">●</span> Opportunity Zone</p>
            </div>
            '''
            m.get_root().html.add_child(folium.Element(legend_html))
            
            # Save map
            map_path = "polycentric_zones_map_fixed.html"
            m.save(map_path)
            print(f"✅ Map saved: {map_path}")
            
            print("\n✅ DONE")
            print("📄 zones_classified_fixed.csv created")
            print("🗺️ polycentric_zones_map_fixed.html created")
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    main()

