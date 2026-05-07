#ifndef STOCKDATA_H
#define STOCKDATA_H

#include <string>
using namespace std;

struct StockData {
    string date;
    double open;
    double high;
    double low;
    double close;
    long volume;

    StockData() {
        open = high = low = close = 0.0;
        volume = 0;
    }
};

#endif