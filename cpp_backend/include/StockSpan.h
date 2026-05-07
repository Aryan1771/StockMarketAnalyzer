#ifndef STOCKSPAN_H
#define STOCKSPAN_H

#include "StockData.h"
#include <vector>
#include <string>

using namespace std;

class StockSpan {
public:
    vector<int> calculateSpan(const vector<StockData> &data);
    void displaySpan(const string &symbol, const vector<StockData> &data);
};

#endif