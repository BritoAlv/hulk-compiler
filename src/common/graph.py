class Graph:
    def __init__(self) -> None:
        self.vertices: dict[str, list[str]] = {}

    def neighbors(self, vertex : str) -> list[str]:
        if vertex not in self.vertices:
            raise Exception("Vertex is not in graph")
        return self.vertices[vertex]

    def contains_edge(self, pair: tuple[str, str]) -> bool:
        return pair[0] in self.vertices and pair[1] in self.vertices[pair[0]]

    def add(self, pair: tuple[str, str]) -> None:

        if pair[0] in self.vertices: # Verify that the first vertex is in the graph
            # Verify that the edge already exists 
            if pair[1] in self.vertices[pair[0]]:
                raise RuntimeError("Edge already exists in the graph")
            # If the edge does not exist then add it
            self.vertices[pair[0]].append(pair[1])
        else: # Add first vertex and the edge
            self.vertices[pair[0]] = [pair[1]]
        
        # Add second vertex if it does not exist
        if pair[1] not in self.vertices:
            self.vertices[pair[1]] = []

    def remove(self, pair: tuple[str, str]) -> None:
        if pair[0] in self.vertices and pair[1] in self.vertices[pair[0]]:
            self.vertices[pair[0]].remove(pair[1])
        else:
            raise RuntimeError("Edge does not exist")
    
    def is_cyclic(self) -> bool:
        # Initialize vertex tracks
        visited_track: dict[str, bool] = {}
        stack_track: dict[str, bool] = {}
        for vertex in self.vertices:
            visited_track[vertex] = False;
            stack_track[vertex] = False;

        for vertex in self.vertices:
            if not visited_track[vertex]:
                if self._is_cyclic(vertex, visited_track, stack_track):
                    return True
        
        return False
                
    def _is_cyclic(self, vertex: str, visited_track: dict[str, bool], stack_track: dict[str, bool]) -> bool:
        # Mark vertex as True on tracks
        visited_track[vertex] = True
        stack_track[vertex] = True

        for edge_vertex in self.vertices[vertex]:
            # If the stack_track is true, it means there's a path from the edge_vertex to vertex besides of this existing edge, therefore it's a cycle
            if stack_track[edge_vertex]:
                return True
            # If not visited, keep moving forward
            if not visited_track[edge_vertex]:
                if self._is_cyclic(edge_vertex, visited_track, stack_track):
                    return True

        # Set stack_track to false, since we are done with the recursion
        stack_track[vertex] = False
        return False