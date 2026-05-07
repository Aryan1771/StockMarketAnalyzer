#include "../include/DataLoader.h"
#include "../include/MovingAverage.h"
#include "../include/RankingEngine.h"
#include "../include/StockSpan.h"
#include <iostream>

using namespace std;

int main() {
    string filename;

    // Step 1: Get CSV file path from Python
    getline(cin, filename);

    if (filename.empty()) {
        cout << "Error: No input file provided for this\n";
        return 1;
    }

    DataLoader loader;

    // Step 2: Load CSV data
    if (!loader.loadCSV(filename)) {
        cout << "Error: Failed to load CSV\n";
        return 1;
    }

    // Step 3: Basic summary
    vector<string> symbols = loader.getAllSymbols();

    if (symbols.empty()) {
        cout << "Error: No stock data\n";
        return 1;
    }

    string symbol = symbols[0]; // take first stock (TEMP for API)
    vector<StockData> data = loader.getStockData(symbol);

    if (data.empty()) {
        cout << "Error: No data for stock\n";
        return 1;
    }

    // Step 4: Latest Price
    double latestPrice = data.back().close;

    // Step 5: Price Change %
    double changePercent = loader.getPriceChangePercent(symbol);

    // Step 6: Moving Average (5-day)
    MovingAverage ma;
    double latestMA = ma.getLatestMA(data, 5);

    // Step 7: Stock Span (last value)
    StockSpan span;
    vector<int> spans = span.calculateSpan(data);
    int latestSpan = spans.back();

    // Step 8: Output (IMPORTANT → Python reads this)
    cout << "{\n";
    cout << "  \"symbol\": \"" << symbol << "\",\n";
    cout << "  \"latest_price\": " << latestPrice << ",\n";
    cout << "  \"change_percent\": " << changePercent << ",\n";
    cout << "  \"moving_average\": " << latestMA << ",\n";
    cout << "  \"stock_span\": " << latestSpan << "\n";
    cout << "}\n";

    return 0;
}