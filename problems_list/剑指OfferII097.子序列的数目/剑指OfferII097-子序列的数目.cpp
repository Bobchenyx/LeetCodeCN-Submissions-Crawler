class Solution {
public:
    int numDistinct(string s, string t) {
        //f[i][j]��ʾs��ǰiλ����tǰjλ��ƥ�����
        int n = s.size(), m = t.size();
        vector <vector<unsigned long long>> f(n + 1, vector <unsigned long long> (m + 1));
        for(int i = 0; i < n; i++) f[i][0] = 1;
        for(int i = 1; i <= n; i++){
            for(int j = 1; j <= min(i, m); j++){
                f[i][j] = max(f[i][j], f[i - 1][j]);
                if(f[i - 1][j - 1] && s[i - 1] == t[j - 1]){
                    f[i][j] += f[i - 1][j - 1];
                }
            }
        }
        return f[n][m];
    }
};