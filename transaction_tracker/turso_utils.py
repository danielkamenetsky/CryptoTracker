from django.conf import settings

def execute_query(query, params=None):
    """
    Execute a SQL query against Turso database
    
    Args:
        query (str): SQL query to execute
        params (list, optional): Query parameters
        
    Returns:
        list: Query results
    """
    client = settings.get_turso_client()
    if params:
        results = client.execute(query, params)
    else:
        results = client.execute(query)
    return results.rows 