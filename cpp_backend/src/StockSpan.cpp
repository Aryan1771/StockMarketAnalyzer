#include "../include/StockSpan.h"
#include <iomanip>
#include <iostream>
#include <stack>
using namespace std;
vector<int> StockSpan::calculateSpan(const vector<StockData> &data) {
  vector<int> span(data.size());
  stack<int> st;

  for (int i = 0; i < data.size(); i++) {
    while (!st.empty() && data[st.top()].close <= data[i].close) {
      st.pop();
    }
    span[i] = st.empty() ? (i + 1) : (i - st.top());
    st.push(i);
  }

  return span;
}

void StockSpan::displaySpan(const string &symbol,
                            const vector<StockData> &data) {
  if (data.empty()) {
    cout << " No data available for " << symbol << endl;
    return;
  }

  vector<int> span = calculateSpan(data);

  cout << "\n========================================" << endl;
  cout << " STOCK SPAN ANALYSIS: " << symbol << endl;
  cout << "========================================" << endl;
  cout << left << setw(15) << "Date" << setw(12) << "Close Price" << setw(10)
       << "Span" << endl;
  cout << "----------------------------------------" << endl;
  int start = max(0, (int)data.size() - 10);

  for (int i = start; i < data.size(); i++) {
    cout << left << setw(15) << data[i].date << "₹" << setw(11) << fixed
         << setprecision(2) << data[i].close << setw(10) << span[i] << " days"
         << endl;
  }

  cout << "========================================\n" << endl;
}