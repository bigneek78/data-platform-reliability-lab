import java.util.*;
class Transit {
 public static void main(String[] args){Scanner sc=new Scanner(System.in);sc.useLocale(Locale.ROOT);double target=sc.nextDouble(),hold=sc.nextDouble();int n=sc.nextInt();double previous=0;
  System.out.print("[");for(int i=0;i<n;i++){double arrival=sc.nextDouble();double depart=i==0?arrival:Math.max(arrival,Math.min(arrival+hold,previous+target));previous=depart;if(i>0)System.out.print(",");System.out.print(depart);}System.out.println("]");
 }
}
