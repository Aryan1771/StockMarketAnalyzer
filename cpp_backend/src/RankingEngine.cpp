#include "../include/RankingEngine.h"
#include <algorithm>
#include <iostream>

using namespace std;

// Calculate percentage change between last two days
double RankingEngine::calculateChange(vector<StockData> &hist)
{
    if (hist.size() < 2)
        return 0.0;

    double curr = hist.back().close;
    double prev = hist[hist.size() - 2].close;

    return ((curr - prev) / prev) * 100.0;
}

// Get Top Gainers
vector<StockPerformance> RankingEngine::getTopGainers(DataLoader &loader, int n)
{
    vector<StockPerformance> result;

    vector<string> symbols = loader.getAllSymbols();

    for (auto &sym : symbols)
    {
        vector<StockData> hist = loader.getStockData(sym);
        if (hist.empty()) continue;

        double change = calculateChange(hist);
        double price = hist.back().close;

        result.push_back(StockPerformance(sym, change, price));
    }

    // Sort descending (highest gain first)
    sort(result.begin(), result.end(),
         [](const StockPerformance &a, const StockPerformance &b)
         {
             return a.change_percent > b.change_percent;
         });

    if (result.size() > n)
        result.resize(n);

    return result;
}

// Get Top Losers
vector<StockPerformance> RankingEngine::getTopLosers(DataLoader &loader, int n)
{
    vector<StockPerformance> result;

    vector<string> symbols = loader.getAllSymbols();

    for (auto &sym : symbols)
    {
        vector<StockData> hist = loader.getStockData(sym);
        if (hist.empty()) continue;

        double change = calculateChange(hist);
        double price = hist.back().close;

        result.push_back(StockPerformance(sym, change, price));
    }

    // Sort ascending (biggest loss first)
    sort(result.begin(), result.end(),
         [](const StockPerformance &a, const StockPerformance &b)
         {
             return a.change_percent < b.change_percent;
         });

    if (result.size() > n)
        result.resize(n);

    return result;
}

// Display Rankings
void RankingEngine::displayRankings(DataLoader &loader, int n)
{
    vector<StockPerformance> gainers = getTopGainers(loader, n);
    vector<StockPerformance> losers = getTopLosers(loader, n);

    cout << "\n========================================\n";
    cout << "        TOP " << n << " GAINERS\n";
    cout << "========================================\n";
    cout << "Symbol\tPrice\tChange%\n";

    for (auto &g : gainers)
    {
        cout << g.symbol << "\t₹" << g.current_price
             << "\t+" << g.change_percent << "%\n";
    }

    cout << "\n========================================\n";
    cout << "        TOP " << n << " LOSERS\n";
    cout << "========================================\n";
    cout << "Symbol\tPrice\tChange%\n";

    for (auto &l : losers)
    {
        cout << l.symbol << "\t₹" << l.current_price
             << "\t" << l.change_percent << "%\n";
    }

    cout << "========================================\n";
}