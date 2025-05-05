#pragma once

#include <string>
#include <vector>
#include "topology.h"  // This provides the definition for struct Link

class DotExporter {
public:
    // Export the topology to a Graphviz DOT file
    static void exportToDot(const std::string& filename, const std::vector<Link>& links, int canvasWidth = 2048);
};
