#pragma once
#include <string>
#include <vector>
#include <unordered_map>
#include <unordered_set>

// Represents a single physical connection between two devices
struct Link {
    std::string node1;  // First device name
    std::string intf1;  // Interface on first device
    std::string node2;  // Second device name
    std::string intf2;  // Interface on second device
};

class Topology {
private:
    std::unordered_map<std::string, std::vector<std::string>> adjacency;
    std::unordered_set<std::string> seen_links;
    int total_links;

public:
    Topology();
    void processLink(const Link& link);
    void printAdjacencyList() const;
    void printStats() const;
};
