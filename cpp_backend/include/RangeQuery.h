#ifndef RANGEQUERY_H
#define RANGEQUERY_H

#include "StockData.h"
#include <vector>
#include <string>

using namespace std;

class RangeQuery {
public:
    void displayRangeAnalysis(const string &symbol,
                             const vector<StockData> &data,
                             int start, int end);
};

#endif