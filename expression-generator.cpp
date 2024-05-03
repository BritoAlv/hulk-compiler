#include <bits/stdc++.h>
#define endl '\n'
#define wp ' '
#define forn for (int i = 0; i < n; i++)
#define form for (int j = 0; j < m; j++)
#define fork for (int i = 0; i < k; i++)
#define pb push_back
#define ull unsigned long long
#define pi pair<int, int>
#define sz size()
// je m appelle Alvaro j ai 21 ans.

using namespace std;

const vector<string> values = {
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "+", "-", "*", "/", "^", "(", ")", "**",
};

void Solve()
{
    int n = rand() % 10 + 1;
    forn
    {
        cout << values[rand() % values.sz];
    }
    cout << endl;
    return;
}

int main()
{
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);
    int test_cases;
    cin >> test_cases;
    cout << test_cases << endl;
    while (test_cases-- > 0)
    {
        srand(test_cases);
        Solve();
    }
    return 0;
}
