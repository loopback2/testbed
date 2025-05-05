#pragma once
#include <vector>
#include <string>

class BloomFilter {
private:
    std::vector<bool> bit_array;
    int num_hashes;
    int size;
    int inserted_count = 0;

public:
    BloomFilter(int size, int num_hashes);
    bool insert(const std::string& item);
    bool possiblyContains(const std::string& item);
    void printStats() const;
};
