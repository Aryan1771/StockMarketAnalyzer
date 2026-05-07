#include "../include/MovingAverage.h"
#include <deque>
#include <iostream>
#include <cmath>
using namespace std;

vector<double> MovingAverage::calculate(const vector<StockData> &data,
                                        int windowSize)
{
    vector<double> movingAvg;
    deque<double> window;
    double sum = 0.0;

    for (int i = 0; i < data.size(); i++) {
        window.push_back(data[i].close);
        sum += data[i].close;

        if (window.size() > windowSize) {
            sum -= window.front();
            window.pop_front();
        }

        double avg = sum / window.size();
        avg = round(avg * 100) / 100;   // rounding to 2 decimals
        movingAvg.push_back(avg);
    }

    return movingAvg;
}

void MovingAverage::display(const string &symbol,
                            const vector<StockData> &data,
                            int windowSize)
{
    if (data.empty()) {
        cout << "No data available for " << symbol << endl;
        return;
    }

    vector<double> ma = calculate(data, windowSize);

    cout << "\n========================================\n";
    cout << windowSize << "-DAY MOVING AVERAGE: " << symbol << "\n";
    cout << "========================================\n";
    cout << "Date\t\tClose\tMA\t\tSignal\n";
    cout << "----------------------------------------\n";

    int start = max(0, (int)data.size() - 10);

    for (int i = start; i < data.size(); i++) {
        double roundedClose = round(data[i].close * 100) / 100;

        string signal;
        if (data[i].close > ma[i])
            signal = "BULLISH";
        else if (data[i].close < ma[i])
            signal = "BEARISH";
        else
            signal = "NEUTRAL";

        cout << data[i].date << "\t"
             << roundedClose << "\t"
             << ma[i] << "\t\t"
             << signal << endl;
    }

    cout << "========================================\n" << endl;
}

double MovingAverage::getLatestMA(const vector<StockData> &data,
                                  int windowSize)
{
    if (data.empty())
        return 0.0;

    vector<double> ma = calculate(data, windowSize);
    return ma.back();
}