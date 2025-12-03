from app.models import TransitNode, Business
from app import db
import json

def insert_transit_nodes(overpass_json):
    """
    Insert transit nodes from Overpass API JSON into the database.
    Requires Flask app context to be active.
    """
    elements = overpass_json.get("elements", [])
    inserted_count = 0
    skipped_count = 0
    updated_count = 0

    for el in elements:
        if el["type"] != "node":
            continue

        node_id = str(el["id"])
        lat = el.get("lat")
        lon = el.get("lon")
        tags = el.get("tags", {})

        # Determine transit type
        transit_type = None
        if "highway" in tags and tags["highway"] == "bus_stop":
            transit_type = "bus_stop"
        elif "railway" in tags and tags["railway"] == "station":
            transit_type = "railway_station"
        elif "railway" in tags and tags["railway"] == "subway_entrance":
            transit_type = "subway_entrance"

        # Skip unknown types or missing coordinates
        if not transit_type or lat is None or lon is None:
            skipped_count += 1
            continue

        # Extract name from tags (prefer name:en, then name, then ref, then loc_name)
        name = (
            tags.get("name:en") or 
            tags.get("name") or 
            tags.get("ref") or 
            tags.get("loc_name") or 
            None
        )

        # Check if node already exists
        existing_node = TransitNode.query.filter_by(osm_id=node_id).first()
        
        if existing_node:
            # Update existing node
            existing_node.type = transit_type
            existing_node.name = name
            existing_node.latitude = lat
            existing_node.longitude = lon
            updated_count += 1
        else:
            # Create new node
            node = TransitNode(
                osm_id=node_id,
                type=transit_type,
                name=name,
                latitude=lat,
                longitude=lon
            )
            db.session.add(node)
            inserted_count += 1

    # Commit all changes to database
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e
    
    return inserted_count, skipped_count, updated_count


def parse_business_elements(elements):
    """
    Parse Overpass API elements and convert them to Business objects.
    
    Args:
        elements: List of elements from Overpass API response
        
    Returns:
        List of Business objects ready to be inserted
    """
    business_objects = []
    
    for el in elements:
        # Handle both nodes and ways/relations (which have center coordinates)
        if el["type"] == "node":
            osm_id = el.get("id")
            lat = el.get("lat")
            lon = el.get("lon")
        elif el["type"] in ["way", "relation"]:
            osm_id = el.get("id")
            # Ways and relations have center coordinates
            center = el.get("center", {})
            lat = center.get("lat")
            lon = center.get("lon")
        else:
            continue
        
        # Skip if missing coordinates or ID
        if lat is None or lon is None or osm_id is None:
            continue
        
        tags = el.get("tags", {})
        
        # Determine category
        category = "other"
        if "amenity" in tags:
            category = "amenity"
        elif "shop" in tags:
            category = "shop"
        elif "office" in tags:
            category = "office"
        
        # Extract name
        name = (
            tags.get("name:en") or 
            tags.get("name") or 
            tags.get("ref") or 
            None
        )
        
        business_objects.append({
            "osm_id": osm_id,
            "name": name,
            "category": category,
            "latitude": lat,
            "longitude": lon,
            "raw_tags": tags
        })
    
    return business_objects


def insert_business_nodes(overpass_json):
    """
    Insert business nodes from Overpass API JSON into the database.
    Requires Flask app context to be active.
    
    Args:
        overpass_json: JSON response from Overpass API
        
    Returns:
        Tuple of (inserted_count, skipped_count, updated_count)
    """
    elements = overpass_json.get("elements", [])
    inserted_count = 0
    skipped_count = 0
    updated_count = 0
    
    for el in elements:
        # Handle both nodes and ways/relations
        if el["type"] == "node":
            osm_id = el.get("id")
            lat = el.get("lat")
            lon = el.get("lon")
        elif el["type"] in ["way", "relation"]:
            osm_id = el.get("id")
            center = el.get("center", {})
            lat = center.get("lat")
            lon = center.get("lon")
        else:
            skipped_count += 1
            continue
        
        # Skip if missing coordinates or ID
        if lat is None or lon is None or osm_id is None:
            skipped_count += 1
            continue
        
        tags = el.get("tags", {})
        
        # Determine category
        category = "other"
        if "amenity" in tags:
            category = "amenity"
        elif "shop" in tags:
            category = "shop"
        elif "office" in tags:
            category = "office"
        
        # Extract name
        name = (
            tags.get("name:en") or 
            tags.get("name") or 
            tags.get("ref") or 
            None
        )
        
        # Check if business already exists
        existing_business = Business.query.filter_by(osm_id=osm_id).first()
        
        if existing_business:
            # Update existing business
            existing_business.name = name
            existing_business.category = category
            existing_business.latitude = lat
            existing_business.longitude = lon
            existing_business.raw_tags = tags
            updated_count += 1
        else:
            # Create new business
            business = Business(
                osm_id=osm_id,
                name=name,
                category=category,
                latitude=lat,
                longitude=lon,
                raw_tags=tags
            )
            db.session.add(business)
            inserted_count += 1
    
    # Commit all changes to database
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e
    
    return inserted_count, skipped_count, updated_count
