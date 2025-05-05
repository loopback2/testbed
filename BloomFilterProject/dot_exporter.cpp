#include "dot_exporter.h"
#include <fstream>
#include <iostream>
#include <unordered_set>
#include <unordered_map>

// Determines the vertical rank group (layer) of each node
std::string getRankGroup(const std::string& device) {
    if (device == "R1" || device == "R2") return "spine";
    if (device == "R3" || device == "R4" || device == "R5" || device == "R6") return "leaf";
    return "switch";
}

void DotExporter::exportToDot(const std::string& filename, const std::vector<Link>& links, int canvasWidth) {
    std::ofstream file(filename);
    if (!file.is_open()) {
        std::cerr << "❌ Failed to open " << filename << " for writing.\n";
        return;
    }

    file << "digraph G {\n";
    file << "  layout=dot;\n";
    file << "  rankdir=TB;\n";
    file << "  dpi=150;\n";
    file << "  splines=polyline;\n";
    file << "  pad=0.5;\n";
    file << "  nodesep=1.2;\n";
    file << "  ranksep=1.2;\n";
    file << "  size=\"" << canvasWidth / 100 << ",10\";\n";
    file << "  node [shape=box style=filled fontname=Helvetica fontsize=14];\n";

    std::unordered_set<std::string> nodes;
    std::unordered_map<std::string, std::string> nodeRanks;

    // Draw Links
    for (const auto& link : links) {
        nodes.insert(link.node1);
        nodes.insert(link.node2);
        nodeRanks[link.node1] = getRankGroup(link.node1);
        nodeRanks[link.node2] = getRankGroup(link.node2);

        file << "  \"" << link.node1 << "\" -> \"" << link.node2 << "\" [dir=none label=\""
             << link.intf1 << " ⟷ " << link.intf2 << "\"];\n";
    }

    // Define node styles
    for (const auto& node : nodes) {
        std::string color;
        if (node == "R1" || node == "R2") {
            color = "khaki";
        } else if (node.find("SW") != std::string::npos) {
            color = "white";
        } else {
            color = "gray";
        }

        file << "  \"" << node << "\" [fillcolor=" << color << "];\n";
    }

    // Define rank groups
    std::unordered_map<std::string, std::vector<std::string>> groups;
    for (const auto& pair : nodeRanks) {
        groups[pair.second].push_back(pair.first);
    }

    for (const auto& group : groups) {
        file << "  { rank=same;";
        for (const auto& node : group.second) {
            file << " \"" << node << "\"";
        }
        file << " }\n";
    }

    file << "}\n";
    file.close();
    std::cout << "✅ DOT file exported to: " << filename << "\n";
}
