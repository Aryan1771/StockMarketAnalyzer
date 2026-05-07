#include "../include/RangeQuery.h"
#include <iostream>
#include <algorithm>

using namespace std;

void RangeQuery::displayRangeAnalysis(const string &symbol,
                                      const vector<StockData> &data,
                                      int start, int end)
{
    double minP = data[start].low;
    double maxP = data[start].high;
    double sum = 0;

    for (int i = start; i <= end; i++) {
        minP = min(minP, data[i].low);
        maxP = max(maxP, data[i].high);
        sum += data[i].close;
    }

    cout << "\nRange Analysis\n";
    cout << "Min: " << minP << "\nMax: " << maxP
         << "\nAvg: " << sum/(end-start+1) << endl;
}