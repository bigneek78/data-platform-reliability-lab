#include <iostream>
#include <vector>
#include <queue>
#include <tuple>
#include <algorithm>
#include <cmath>
int main(){
 int h,w,sr,sc,gr,gc;if(!(std::cin>>h>>w>>sr>>sc>>gr>>gc))return 2;
 std::vector<std::string> g(h);for(auto &r:g)std::cin>>r;
 int s=sr*w+sc,t=gr*w+gc;std::vector<int> d(h*w,1000000000),parent(h*w,-1);
 using Q=std::tuple<int,int,int>;std::priority_queue<Q,std::vector<Q>,std::greater<Q>>q;
 auto heuristic=[&](int v){return std::abs(v/w-gr)+std::abs(v%w-gc);};
 d[s]=0;q.emplace(heuristic(s),0,s);int expanded=0;
 while(!q.empty()){
  auto [f,c,u]=q.top();q.pop();(void)f;if(c!=d[u])continue;++expanded;if(u==t)break;
  const int dr[]={-1,0,0,1},dc[]={0,-1,1,0};
  for(int k=0;k<4;k++){int r=u/w+dr[k],col=u%w+dc[k];if(r<0||col<0||r>=h||col>=w||g[r][col]=='#')continue;
   int v=r*w+col;if(c+1<d[v]){d[v]=c+1;parent[v]=u;q.emplace(d[v]+heuristic(v),d[v],v);}}
 }
 std::vector<int> path;if(d[t]<1000000000){for(int v=t;v!=-1;v=parent[v])path.push_back(v);std::reverse(path.begin(),path.end());}
 std::cout<<"{\"cost\":"<<(path.empty()?-1:d[t])<<",\"expanded\":"<<expanded<<",\"path\":[";
 for(size_t i=0;i<path.size();i++){if(i)std::cout<<",";std::cout<<"["<<path[i]/w<<","<<path[i]%w<<"]";}std::cout<<"]}\n";
}
