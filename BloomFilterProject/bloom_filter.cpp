#include "bloom_filter.h"
#include <iostream>
#include <functional>
#include <cmath>

BloomFilter::BloomFilter(int size, int num_hashes)
    : bit_array(size, false), num_hashes(num_hashes), size(size) {}

bool BloomFilter::insert(const std::string& item) {
    bool already_present = true;

    for (int i = 0; i < num_hashes; ++i) {
        std::size_t hash = std::hash<std::string>{}(item + std::to_string(i)) % size;
        if (!bit_array[hash]) {
            already_present = false;
            bit_array[hash] = true;
        }
    }

    if (!already_present)
        ++inserted_count;

    return !already_present;
}

bool BloomFilter::possiblyContains(const std::string& item) {
    for (int i = 0; i < num_hashes; ++i) {
        std::size_t hash = std::hash<std::string>{}(item + std::to_string(i)) % size;
        if (!bit_array[hash]) {
            return false;
        }
    }
    return true;
}

void BloomFilter::printStats() const {
    int set_bits = 0;
    for (bool bit : bit_array) {
        if (bit) ++set_bits;
    }

    double load_factor = static_cast<double>(set_bits) / size;
    double est_fp_rate = std::pow(load_factor, num_hashes);

    std::cout << "\n🧠 Bloom Filter Stats:\n";
    std::cout << "- Bit array size: " << size << "\n";
    std::cout << "- Hash functions used: " << num_hashes << "\n";
    std::cout << "- Unique elements inserted: " << inserted_count << "\n";
    std::cout << "- Bits set: " << set_bits << " (" << static_cast<int>(load_factor * 100) << "% full)\n";
    std::cout << "- Estimated false positive rate: ~" << est_fp_rate * 100 << "%\n";
}
