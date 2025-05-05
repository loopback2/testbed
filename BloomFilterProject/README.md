# 🌐 Scalable Network Topology Mapping using a Bloom Filter

This C++ project implements a scalable and memory-efficient network topology discovery tool using a **Bloom Filter**. It ingests a set of device-to-device links, eliminates duplicate entries probabilistically, constructs an adjacency list, and visualizes the network in a Graphviz DOT diagram.

> **Course**: Data Structures & Algorithms  
> **Author**: Jacob Pando  
> **Term Project** – C++

---

## ✨ Overview

Modern networks often involve large-scale topologies with hundreds or thousands of interconnections. Repeated scanning, redundant links, and misconfigurations can lead to duplicate topology entries that clutter visualization or lead to inefficient processing.

This project addresses this challenge using a **Bloom Filter**, a probabilistic data structure that efficiently identifies duplicates while minimizing memory usage.

---

## 🔧 Features

- Processes a list of network links  
- Detects and filters duplicate connections using a Bloom Filter  
- Constructs a clean device-level adjacency list  
- Exports topology to a `.dot` file for Graphviz rendering  
- Displays link stats and Bloom Filter diagnostics in the console  
- Clean and modular C++ code using STL containers and algorithms  

---

## 📦 Project Structure

.
├── main.cpp # Entry point
├── bloom_filter.h/.cpp # Bloom Filter implementation
├── topology.h/.cpp # Adjacency list and logic
├── dot_exporter.h/.cpp # DOT file export for Graphviz
├── topology.dot # DOT output
├── topology.png # Rendered image
└── README.md # This file

---

## 🚀 Build & Run

### Requirements

- C++17 compiler (e.g., `g++`)
- [Graphviz](https://graphviz.org/download/) installed

### Compile

```bash
g++ -std=c++17 main.cpp bloom_filter.cpp topology.cpp dot_exporter.cpp -o bloom_project

RUN

./bloom_project

VISUALIZE

dot -Tpng topology.dot -o topology.png
open topology.png  # macOS; or use any image viewer