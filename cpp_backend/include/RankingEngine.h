#ifndef RANKINGENGINE_H
#define RANKINGENGINE_H

#include "DataLoader.h"
#include <vector>
#include <string>

using namespace std;

struct StockPerformance {
    string symbol;
    double change_percent;
    double current_price;

    
    StockPerformance() {
        symbol = "";
        change_percent = 0.0;
        current_price = 0.0;
    }

    // existing constructor
    StockPerformance(string s, double c, double p) {
        symbol = s;
        change_percent = c;
        current_price = p;
    }
};

class RankingEngine {
public:
    double calculateChange(vector<StockData> &hist);
    vector<StockPerformance> getTopGainers(DataLoader &loader, int n);
    vector<StockPerformance> getTopLosers(DataLoader &loader, int n);
    void displayRankings(DataLoader &loader, int n);
};

#endif