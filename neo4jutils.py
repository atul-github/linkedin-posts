from py2neo import Graph, Node, Relationship

def init_neo4j(G):
  # G = nx.Graph()
  # G.add_edges_from([(1, 2), (2, 3), (3, 4), (4, 1)])

    graph = Graph("bolt://localhost:7687", auth=None)

    graph.run("MATCH (n) DETACH DELETE n")

    nodes_array = []
#  for node in G.nodes():
    for node, attrs in G.nodes(data=True):
      item = {"id": node, "name": attrs.get("name", ""), "title": attrs.get("title", "")} 
      nodes_array.append(item)
      # graph.merge(Node("Node", id=node, name=attrs.get("name", ""), title=attrs.get("title", "")), "Node", "id")

    query = """
    UNWIND $batch AS row
    MERGE (n:Node {id: row.id})
    SET n.name = row.name, n.title = row.title
    """

    batch_size = 5000
    for i in range(0, len(nodes_array), batch_size):
        graph.run(query, batch=nodes_array[i : i + batch_size])


    edge_array = []
    for node1, node2, attrs in G.edges(data=True):
       item = {"source": node1, "target": node2, "relation": attrs.get("relation", "UNKNOWN"), "weight": attrs.get("weight", 0)}
       edge_array.append(item)

    query = """
    UNWIND $batch AS row
    MATCH (a:Node {id: row.source}), (b:Node {id: row.target})
    CALL apoc.create.relationship(a, row.relation, {weight: row.weight}, b) YIELD rel
    RETURN rel
    """

    batch_size = 5000
    for i in range(0, len(edge_array), batch_size):
        graph.run(query, batch=edge_array[i : i + batch_size])       

    

    # for node1, node2, data in G.edges(data=True):
    #     node1 = graph.nodes.match("Node", id=node1).first()
    #     node2 = graph.nodes.match("Node", id=node2).first()
    #     if node1 and node2:
    #         rel = Relationship(node1, data.get("relation", "UNKNOWN"), node2, 
    #                            relation=data.get("relation", ""),
    #                            weight=data.get("weight", 0))
    #         graph.merge(rel)