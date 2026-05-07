#include "../include/StockAnalyzer.h"
#include <iostream>

using namespace std;

StockAnalyzer::StockAnalyzer() {}

bool StockAnalyzer::loadData(const string &filename) {
    return loader.loadCSV(filename);
}

void StockAnalyzer::displaySummary() {
    loader.displaySummary();
}

vector<string> StockAnalyzer::getSymbols() {
    return loader.getAllSymbols();
}

bool StockAnalyzer::isValidSymbol(const string &symbol) {
    return loader.hasSymbol(symbol);
}

void StockAnalyzer::runStockSpan(const string &symbol) {
    if (!loader.hasSymbol(symbol)) {
        cout << "Invalid symbol!\n";
        return;
    }

    auto data = loader.getStockData(symbol);
    span.displaySpan(symbol, data);
}

void StockAnalyzer::runMovingAverage(const string &symbol, int windowSize) {
    if (!loader.hasSymbol(symbol)) {
        cout << "Invalid symbol!\n";
        return;
    }

    auto data = loader.getStockData(symbol);
    movingAvg.display(symbol, data, windowSize);
}

void StockAnalyzer::runRangeQuery(const string &symbol, int start, int end) {
    if (!loader.hasSymbol(symbol)) {
        cout << "Invalid symbol!\n";
        return;
    }

    auto data = loader.getStockData(symbol);
    rangeQuery.displayRangeAnalysis(symbol, data, start, end);
}

void StockAnalyzer::runRanking(int topN) {
    ranking.displayRankings(loader, topN);
}