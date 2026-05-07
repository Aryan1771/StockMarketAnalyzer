#ifndef STOCKANALYZER_H
#define STOCKANALYZER_H

#include "DataLoader.h"
#include "MovingAverage.h"
#include "RangeQuery.h"
#include "RankingEngine.h"
#include "StockSpan.h"

#include <string>
#include <vector>

using namespace std;

class StockAnalyzer {
private:
    DataLoader loader;
    MovingAverage movingAvg;
    RangeQuery rangeQuery;
    RankingEngine ranking;
    StockSpan span;

public:
    StockAnalyzer();

    // Load data
    bool loadData(const string &filename);

    // Display all stocks summary
    void displaySummary();

    // Stock Span
    void runStockSpan(const string &symbol);

    // Moving Average
    void runMovingAverage(const string &symbol, int windowSize);

    // Range Query
    void runRangeQuery(const string &symbol, int start, int end);

    // Ranking
    void runRanking(int topN);

    // Utility
    vector<string> getSymbols();
    bool isValidSymbol(const string &symbol);
};

#endif