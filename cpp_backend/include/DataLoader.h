#ifndef DATALOADER_H
#define DATALOADER_H

#include "StockData.h"
#include <unordered_map>
#include <vector>
#include <string>

using namespace std;

class DataLoader {
private:
    unordered_map<string, vector<StockData>> stockMap;

public:
    DataLoader();
    ~DataLoader();

    string trim(const string &str);
    bool loadCSV(const string &filename);

    vector<StockData> getStockData(const string &symbol) const;
    vector<string> getAllSymbols() const;

    bool hasSymbol(const string &symbol) const;
    int getStockCount() const;

    void displaySummary() const;
    void clearData();

    double getLatestPrice(const string &symbol) const;
    double getPriceChangePercent(const string &symbol) const;
};

#endif