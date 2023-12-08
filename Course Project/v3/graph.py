with open("values.txt", "r") as file:
    values = [[int(num) for num in line.split()] for line in file]

class Graph:
    def __init__(self, switches, hosts, links):
        shift = len(switches)
        self.vertices = {}
        self.hosts = hosts
        self.switches = switches
        self.ports = [
            [0 for column in range(len(switches))] for row in range(len(switches))
        ]
        for i in links:
            data = i.to_dict()
            src = int(data["src"]["dpid"]) - 1
            dest = int(data["dst"]["dpid"]) - 1
            port = int(data["src"]["port_no"])
            self.ports[src][dest] = port

        print("----------------------------------------------------------")
        print("All ports:")
        self.print_matrix(self.ports, len(self.switches))

        self.nodes = len(switches) + len(hosts)
        self.edges = [
            [1e7 for column in range(self.nodes)] for row in range(self.nodes)
        ]
        self.distances = [
            [1e7 for column in range(self.nodes)] for row in range(self.nodes)
        ]
        self.parents = [
            [-1 for column in range(self.nodes)] for row in range(self.nodes)
        ]

        for i in switches:
            switch = i.to_dict()
            value = int(switch["dpid"]) - 1
            self.vertices[i] = value
        # Switches are indexed by DPID

        for i in hosts:
            self.vertices[i.mac] = shift
            shift += 1
        # Hosts are added at the end in random order

        self.host_map = {}
        for i in hosts:
            self.host_map["H" + i.mac[-1]] = i.mac

        self.main()

    def print_matrix(self, matrix, size):
        for i in range(size):
            for j in range(size):
                if matrix[i][j] == 1e7:
                    print(" ∞", end=" ")
                else:
                    print(f"{int(matrix[i][j]):02}", end=" ")
            print()

    def cost(self, delay, bandwidth):
        return delay - bandwidth + 5

    def create_graph(self):
        for i in self.hosts:
            dpid = i.port.dpid - 1
            delay, bandwidth = values[dpid]
            self.edges[self.vertices[i.mac]][dpid] = self.cost(delay, bandwidth)
            self.edges[dpid][self.vertices[i.mac]] = self.cost(delay, bandwidth)

        shift = len(self.switches)
        for i in range(shift, len(values)):
            delay, bandwidth = values[i][2:]
            self.edges[values[i][0]][values[i][1]] = self.cost(delay, bandwidth)
            self.edges[values[i][1]][values[i][0]] = self.cost(delay, bandwidth)

    def min_distance(self, distances, shortest_path):
        min = 1e7
        for v in range(self.nodes):
            if distances[v] < min and shortest_path[v] == False:
                min = distances[v]
                min_index = v

        return min_index

    def dijkstra(self, src):
        self.distances[src][src] = 0
        shortest_path = [False] * self.nodes

        for _ in range(self.nodes):
            u = self.min_distance(self.distances[src], shortest_path)
            shortest_path[u] = True
            for v in range(self.nodes):
                if (
                    self.edges[u][v] > 0
                    and shortest_path[v] == False
                    and self.distances[src][v]
                    > self.distances[src][u] + self.edges[u][v]
                ):
                    self.parents[src][v] = u
                    self.distances[src][v] = self.distances[src][u] + self.edges[u][v]

    def all_pair_shortest_paths(self):
        min_cost = [
            [0 for column in range(len(self.hosts))] for row in range(len(self.hosts))
        ]
        for i in self.hosts:
            for j in self.hosts:
                src = self.vertices[i.mac]
                dst = self.vertices[j.mac]
                min_cost[int(i.mac[-1]) - 1][int(j.mac[-1]) - 1] = self.distances[src][
                    dst
                ]
        self.print_matrix(min_cost, len(self.hosts))

    def cost_all_links(self):
        for i in range(len(self.switches)):
            print(f"S{i+1} - H{i+1}: {self.cost(values[i][0], values[i][1])}")
        for j in range(len(self.switches), len(values)):
            print(
                f"S{values[j][0]} - S{values[j][1]}: {self.cost(values[j][2], values[j][3])}"
            )

    def floyd_warshall(self):
        for k in range(self.nodes):
            for i in range(self.nodes):
                for j in range(self.nodes):
                    if (
                        self.distances[i][j]
                        > self.distances[i][k] + self.distances[k][j]
                    ):
                        self.distances[i][j] = (
                            self.distances[i][k] + self.distances[k][j]
                        )
                        self.parents[i][j] = k

    def compute_all_paths(self):
        print("Enter Source Host:", end=" ")
        src_host = input()
        for i in self.hosts:
            dest_host = "H" + i.mac[-1]
            print(f"{src_host} - {dest_host}:", end=" ")
            src_index = self.vertices[self.host_map[src_host]]
            dest_index = self.vertices[i.mac]
            self.all_path(src_index, dest_index, src_host, dest_host)
            print()

    def all_path(self, src_index, dest_index, src_host, dest_host):
        if self.parents[src_index][dest_index] == -1:
            print(src_host, end=" ")
            return
        self.all_path(
            src_index, self.parents[src_index][dest_index], src_host, dest_host
        )
        if dest_index >= len(self.hosts):
            print(f"-> {dest_host}", end=" ")
        else:
            print(f"-> S{dest_index+1}", end=" ")

    def compute_path(self):
        self.switch_path = []
        print("Enter Source Host:", end=" ")
        src_host = input()
        print("Enter Destination Host:", end=" ")
        dest_host = input()
        print("Enter Bandwidth:", end=" ")
        weight = int(input())

        print(f"{src_host} - {dest_host}:", end=" ")
        src_index = self.vertices[self.host_map[src_host]]
        dest_index = self.vertices[self.host_map[dest_host]]
        self.switch_path = []
        self.path(src_index, dest_index, src_host, dest_host, weight)
        print()

    def path(self, src_index, dest_index, src_host, dest_host, weight):
        dest = self.parents[src_index][dest_index]

        if dest == -1:
            print(src_host, end=" ")
            return

        self.edges[dest][dest_index] += weight
        self.edges[dest_index][dest] += weight

        self.path(src_index, dest, src_host, dest_host, weight)
        if dest_index >= len(self.hosts):
            print(f"-> {dest_host}", end=" ")
        else:
            print(f"-> S{dest_index+1}", end=" ")
            self.switch_path.append(dest_index)

    def main(self):
        print("\nCost of all Links:")
        self.create_graph()
        self.cost_all_links()

        print("\nApplying All Pair shortest path")
        for i in range(self.nodes):
            self.dijkstra(i)

        print("Adjacency Matrix is:")
        self.print_matrix(self.edges, self.nodes)
        print("\nDistances from Source to Dest:")
        self.print_matrix(self.distances, self.nodes)
        print("\nParent Matrix:")
        self.print_matrix(self.parents, self.nodes)

        print("\nAll Pair Shortest Paths are:")
        self.all_pair_shortest_paths()

        print("\nCompute Path from Source to All Hosts:")
        self.compute_all_paths()

        print("\nCompute Path between Source and Destination Hosts:")
        self.compute_path()

        print("\nSwitches where configuration needs to be added:")
        for i in range(len(self.switch_path)):
            print(f"S{self.switch_path[i]+1}", end=" ")

        print("\n\nNew Adjacency Matrix is:")
        self.print_matrix(self.edges, self.nodes)
        print("\nApplying All Pair shortest path")
        for i in range(self.nodes):
            self.dijkstra(i)
        print("\nDistances from Source to Dest:")
        self.print_matrix(self.distances, self.nodes)
        print("\nParent Matrix:")
        self.print_matrix(self.parents, self.nodes)
        

