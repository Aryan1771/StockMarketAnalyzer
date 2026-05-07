#ifndef MOVINGAVERAGE_H
#define MOVINGAVERAGE_H

#include "StockData.h"
#include <vector>
#include <string>

using namespace std;

class MovingAverage {
public:
    vector<double> calculate(const vector<StockData> &data, int windowSize);
    void display(const string &symbol, const vector<StockData> &data, int windowSize);
    double getLatestMA(const vector<StockData> &data, int windowSize);
};

#endif