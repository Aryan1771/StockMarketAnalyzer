#include "../include/DataLoader.h"
#include <fstream>
#include <sstream>
#include <iostream>

using namespace std;

DataLoader::DataLoader() {}
DataLoader::~DataLoader() {}

string DataLoader::trim(const string &str) {
    size_t first = str.find_first_not_of(" \t\r\n");
    size_t last = str.find_last_not_of(" \t\r\n");
    return (first == string::npos) ? "" : str.substr(first, last - first + 1);
}

bool DataLoader::loadCSV(const string &filename) {
    ifstream file(filename);
    if (!file.is_open()) {
        cerr << "Error opening file\n";
        return false;
    }

    string line;
    getline(file, line); // skip header

    while (getline(file, line)) {
        stringstream ss(line);
        string token, symbol;
        StockData data;

        getline(ss, data.date, ',');
        getline(ss, symbol, ',');

        try {
            getline(ss, token, ','); data.open = stod(token);
            getline(ss, token, ','); data.high = stod(token);
            getline(ss, token, ','); data.low = stod(token);
            getline(ss, token, ','); data.close = stod(token);
            getline(ss, token, ','); data.volume = stol(token);
        } catch (...) {
            continue;
        }

        stockMap[symbol].push_back(data);
    }

    return true;
}

vector<StockData> DataLoader::getStockData(const string &symbol) const {
    if (stockMap.count(symbol))
        return stockMap.at(symbol);
    return {};
}

vector<string> DataLoader::getAllSymbols() const {
    vector<string> res;
    for (auto &p : stockMap) res.push_back(p.first);
    return res;
}

bool DataLoader::hasSymbol(const string &symbol) const {
    return stockMap.count(symbol);
}

int DataLoader::getStockCount() const {
    return stockMap.size();
}

void DataLoader::displaySummary() const {
    for (auto &p : stockMap) {
        cout << p.first << " (" << p.second.size() << " records)\n";
    }
}

void DataLoader::clearData() {
    stockMap.clear();
}

double DataLoader::getLatestPrice(const string &symbol) const {
    if (!hasSymbol(symbol)) return 0;
    auto &v = stockMap.at(symbol);
    return v.back().close;
}

double DataLoader::getPriceChangePercent(const string &symbol) const {
    if (!hasSymbol(symbol)) return 0;
    auto &v = stockMap.at(symbol);
    if (v.size() < 2) return 0;

    return ((v.back().close - v[v.size()-2].close) /
            v[v.size()-2].close) * 100.0;
}
