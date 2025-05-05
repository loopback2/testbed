#include <iostream>
#include <vector>
#include "topology.h"
#include "bloom_filter.h"
#include "dot_exporter.h"

int main() {
    // Create test topology links (replace this with your actual topology loader)
    std::vector<Link> links = {
        {"R1", "xe-0/0/0", "R3", "xe-0/0/1"},
        {"R1", "xe-0/0/1", "R4", "xe-0/0/0"},
        {"R1", "xe-0/0/2", "R5", "xe-0/0/0"},
        {"R1", "xe-0/0/3", "R6", "xe-0/0/0"},
        {"R2", "xe-0/0/0", "R3", "xe-0/0/1"},
        {"R2", "xe-0/0/1", "R4", "xe-0/0/1"},
        {"R2", "xe-0/0/2", "R5", "xe-0/0/1"},
        {"R2", "xe-0/0/3", "R6", "xe-0/0/1"},
        {"R4", "xe-0/0/3", "SW1", "ge-0/0/0"},
        {"R4", "xe-0/0/3", "SW1", "ge-0/0/0"},
        {"R4", "xe-0/0/3", "SW1", "ge-0/0/0"},
        {"R4", "xe-0/0/3", "SW1", "ge-0/0/0"},
        {"R4", "xe-0/0/3", "SW1", "ge-0/0/0"},
        {"R4", "xe-0/0/3", "SW1", "ge-0/0/0"},
        {"R6", "xe-0/0/3", "SW2", "ge-0/0/0"}
    };

    // Initialize Bloom Filter
    BloomFilter bloomFilter(1024, 3);
    Topology topology;

    for (const auto& link : links) {
        std::string key = link.node1 + link.intf1 + link.node2 + link.intf2;
        if (bloomFilter.insert(key)) {
            topology.processLink(link);
            std::cout << "🔗 Link added: " << link.node1 << " (" << link.intf1 << ") ⟷ "
                      << link.node2 << " (" << link.intf2 << ")\n";
        } else {
            std::cout << "⚠️  Duplicate detected (Bloom Filter): " << link.node1 << " ⟷ " << link.node2 << "\n";
        }
    }

    topology.printAdjacencyList();
    topology.printStats();
    bloomFilter.printStats();

    // Export to Graphviz DOT file
    DotExporter::exportToDot("topology.dot", links);

    return 0;
}
