#include "topology.h"
#include <iostream>
#include <algorithm>

Topology::Topology() : total_links(0) {}

void Topology::processLink(const Link& link) {
    std::string key1 = link.node1 + "::" + link.intf1 + "--" + link.node2 + "::" + link.intf2;
    std::string key2 = link.node2 + "::" + link.intf2 + "--" + link.node1 + "::" + link.intf1;

    if (seen_links.find(key1) == seen_links.end() && seen_links.find(key2) == seen_links.end()) {
        adjacency[link.node1].push_back(link.node2);
        adjacency[link.node2].push_back(link.node1);
        seen_links.insert(key1);
        total_links++;

        std::cout << "🔗 Link added: " << link.node1 << " (" << link.intf1 << ") ⟷ "
                  << link.node2 << " (" << link.intf2 << ")\n";
    } else {
        std::cout << "⚠️  Duplicate link skipped: " << link.node1 << " ⟷ " << link.node2 << "\n";
    }
}

void Topology::printAdjacencyList() const {
    std::cout << "\n📘 Final Adjacency List:\n";
    for (const auto& [device, neighbors] : adjacency) {
        std::cout << "- " << device << ": ";
        for (const auto& neighbor : neighbors) {
            std::cout << neighbor << " ";
        }
        std::cout << "\n";
    }
}

void Topology::printStats() const {
    std::cout << "\n📊 Topology Stats:\n";
    std::cout << "- Total unique links processed: " << total_links << "\n";
    std::cout << "- Duplicate links skipped: " << seen_links.size() - total_links << "\n";
}
