#include <stdio.h>
int main(void){double limit,age;int n,stop=0,e,r;if(scanf("%lf %d",&limit,&n)!=2)return 2;
printf("[");for(int i=0;i<n;i++){if(scanf("%lf %d %d",&age,&e,&r)!=3)return 2;
int fault=e||age>limit;if(fault)stop=1;else if(r)stop=0;if(i)printf(",");printf("\"%s\"",stop?"STOP":"READY");}puts("]");return 0;}
