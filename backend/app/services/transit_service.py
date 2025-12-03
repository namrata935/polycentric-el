from sklearn.cluster import KMeans
import pandas as pd
from app.models import TransitNode
from app import db

def cluster_transit_nodes():
    nodes = TransitNode.query.all()
    data = pd.DataFrame([{
        'id': n.id, 'lat': n.latitude, 'lon': n.longitude
    } for n in nodes])

    kmeans = KMeans(n_clusters=3)
    data['cluster'] = kmeans.fit_predict(data[['lat', 'lon']])
    return data
