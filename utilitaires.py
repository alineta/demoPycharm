import networkx as nx

def getRoot(elements):
    graph = nx.DiGraph()
    r = []
    for i in elements :
        d = i['data']
        if d.get('label',0) == 0 :
            r.append((d['source'],d['target']))

    graph.add_edges_from(r)
    return list(nx.dfs_tree(graph).edges())[0][0]
