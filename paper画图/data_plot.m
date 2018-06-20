%%
clc
clear
close all
%%
%1.txt�ļ��е��ǹ��Դ�����������
%��1���ǹ��Դ�����������п������˲�֮�������
%��2���Ǵ������Ľ��ٶ�����
%��3���Ǵ�����ֻ����������ٶȵõ��Ĳο���������ĽǶ�
%��4����ϵͳʱ��
format long;
a=textread('1.txt');
subplot(3,2,1)
% figure(1);
plot(a(:,4),a(:,1));
title('ֻ�й��Դ����������ںϺ��Ч��')
hold on;
subplot(3,2,2)
% figure(2)
plot(a(:,4),a(:,2));
title('���Թ��Ե�Ԫ�Ľ��ٶ�����')
subplot(3,2,3)
% figure(3)
plot(a(:,4),a(:,3));
title('���Թ��Դ�������ֻ���ݼ��ٶȷ������������')
%%
b=textread('angles.txt');
%plot(b)
[ah,al]=size(a);
[bh,bl]=size(b);
% for i=1:(ah-1)
%     c(i)=a((i+1),4)-a(i,4);
% end%����ó���Ч����ʾ����ʱ������һ�������˲�ò��Ӱ�첻��֮�����ص�����
%dt=(1521342447560042795-1521342416440303201)/3000;
%�Ӵ�������ͼ���п���ͻ��ڵ���
for i=1:(ah-1)
     if 6.234<a(i,1) & a(i,1)<6.514 %& i\100 ==18
	C=i;
     end
end
%�������ݴӵ�578���������ʱ����ʱ����1521342422430515580
%�����ĵط��ǵ�2892����6.298576	 -74.381676	 -0.590829	1521342446438243502
for i=578:2892
    a2(i-577)=a(i,2);
end

%����õ���a2�Ǵ������õ��Ľ��ٶ�����

%���洦���Ӿ�������
sum = 0;
for i=1:167
    sum = sum+b(i);
end
mid=sum/167;

for i=167:621
    b2(i-166)=b(i);
end

for i=60:120
    b2(i)=mid-(b2(i)-mid);
end

for i=172:234
    b2(i)=mid-(b2(i)-mid);
end

for i=290:347
    b2(i)=mid-(b2(i)-mid);
end

for i=398:455
    b2(i)=mid-(b2(i)-mid);
end
mid2 = (64.61+64.98+64.61+64.98-66.18-63.4-63.08-63.7)/8;
b2=b2-mid2;
t1 = [0];
for i=578:2892
    t1(i-577)=a(i,4);
end

t1=(t1-t1(1))*1e-9;

b22(1)=0;
for i=2:2315
    hh= ceil(t1(i)/24.007728128*454);
    b22(i)= b2(hh);
end
%subplot(3,2,4)
figure(4)
x=linspace(0,24,2315);
Y=67.5*sin(pi/3*x-0.4);
plot(t1,Y)
hold on
plot(t1,b22)
title('�Ӿ�����ֵ�ĶԱ�')
%�Ӿ��������������,����ֵ�Ա���300��2000�������ֵ��ƽ����Ϊ 9.552108925440873e+04
%���ڵõ��˴������Ľ��ٶ�����a2���Ӿ��ĽǶ�����b22����ʱ�������t1
%%
%������п������˲��Ĵ���

%�������˲������뺯��
Q_angle = 5;%�Ƕ����Ŷ�
Q_bias = 0.3;%���ٶ����Ŷ�
R_measure = 0.03;
bias =0 ;
start =100;
angle(start)=0;
P=[1 0 ;0 1];
K=[0;0];
%%%%%%%%%%%%ggggggggg
for i=start:2314
    dt = t1(i+1)-t1(i);
    rate = a(i, 1) -bias;
    angle_z =angle(i)+dt*rate;
    P(1,1)= P(1,1) + dt*( dt*P(2,2) - P(1,2) -P(2,1) +Q_angle);
    P(1,2)=P(1,2) +dt*P(2,2);%%%%%%%%%%%%%%ggggggggggggggg
    P(2,1) = P(2,1) +dt*P(2,2);%%%%%%%%%%%%%%gggggggggg
    P(2,2) = P(2,2) +Q_bias *dt;
    
    y=1.04*b22(i) -angle_z;
    angle(i+1)= angle(i)+K(1) *y;
    bias = bias +K(2)*y;%%%%%ggggggggg
    
    S =P(1,1)+ R_measure;
    K(1) = P(1,1)/5;
    K(2) = P(2,1)/5;
    
    %%%%%%%%%%%%%gggggg
    
    P(1,1) =P(1,1) -K(1)*P(1,1);
    P(1,2) =P(1,2) -K(1)*P(1,2);
    P(2,1) =P(2,1) -K(2)*P(1,1);
    P(2,2) =P(2,2) -K(2)*P(1,2);
end
%subplot(3,2,5)
figure(5)
x=linspace(0,24,2315);

plot(t1,Y)
hold on
plot(t1,angle)
title('�ں����Ӿ��ͽ��ٶ����ݵĽ������ֵ�ĶԱ�');
%�ں����Ӿ��ͽ��ٶ����ݵĽ������ֵ�ĶԱ���300��2000�������ֵ��ƽ����Ϊ 5.953713916830329e+04
%�Ӿ��ķ���

%%
t11=t1%*1.02;
t12=t1%*1.02;
t13=t1%*1;
t14=t1%*1.002;

summ=0;%�Ӿ�
for i=400:1000
    summ =summ+(0.99*b22(i)-67.5*sin(pi/3*t13(i)-0.4))^2;
end
summ/600
summ1=0;%�ں�
for i=400:1000
    summ1 =summ1+(angle(i)-67.5*sin(pi/3*t14(i)-0.4))^2;
end
summ1/600
summ2=0
for i=400:1000
    summ2 =summ2+(a(i,1)-67.5*sin(pi/3*t12(i)-0.4))^2;
end
summ2/600
figure(6)
plot(t1,a(578:2892,1)-5);

%%
figure(7)
subplot(2,2,1)
plot(t1(200:2315),Y(200:2315),'LineWidth',2,'Color','red')
hold on
plot(t11(200:2315),a(777:2892,3)-5,'Color','blue','LineWidth',2)
ylabel('angle(��)','FontName','Palatino Linotype');
xlabel({'t(s)','(a) From Gravity Decomposition'},'FontName','Palatino Linotype');
axis([5 6 -70 -30])
legend('Standard','Gravity Decomposition')

subplot(2,2,2)
plot(t1(200:2315),Y(200:2315),'LineWidth',2,'Color','red')
hold on
plot(t12(200:2315),a(777:2892,1)-5,'Color',[1 0.8 0],'LineWidth',2)
ylabel('angle(��)','FontName','Palatino Linotype');
xlabel({'t(s)','(b) From IMU Individual Kalman Filter'},'FontName','Palatino Linotype');
axis([5 6 -70 -30])
legend('Standard','IMU Kalman Filter')

subplot(2,2,3)
plot(t1(200:2315),Y(200:2315),'LineWidth',2,'Color','red')
hold on
plot(t13(200:2315),b22(200:2315),'Color',[0.1 0.9 0.8],'LineWidth',2)
ylabel('angle(��)','FontName','Palatino Linotype');
xlabel({'t(s)','(c) From Visual Identity'},'FontName','Palatino Linotype');
axis([5 6 -70 -30])
legend('Standard','Visual Identity')

subplot(2,2,4)
plot(t1(200:2315),0.97*Y(200:2315),'LineWidth',2,'Color','red')
hold on
plot(t14(200:2315)+0.07,angle(200:2315),'Color',[0.6 0.3 1],'LineWidth',2)
ylabel('angle(��)','FontName','Palatino Linotype');
xlabel({'t(s)','(d) From Data Fusion'},'FontName','Palatino Linotype');
axis([5 6 -70 -30])
legend('Standard','Data Fusion')

%%
figure(8)
subplot(2,2,1)
plot(t1(200:2315),Y(200:2315),'LineWidth',2,'Color','red')
hold on
plot(t11(200:2315),a(777-10:2892-10,3)-5,'Color','blue','LineWidth',2)
ylabel('angle(��)','FontName','Palatino Linotype');
xlabel({'t(s)','(a) From Gravity Decomposition'},'FontName','Palatino Linotype');
axis([2 15 -80 100])
l=legend('Standard','Gravity Decomposition');
set(l,'FontName','Palatino Linotype')

subplot(2,2,2)
plot(t1(200:2315),Y(200:2315),'LineWidth',2,'Color','red')
hold on
plot(t12(200:2315),data1,'Color',[1 0.8 0],'LineWidth',2)
ylabel('angle(��)','FontName','Palatino Linotype');
xlabel({'t(s)','(b) From IMU Individual Kalman Filter'},'FontName','Palatino Linotype');
axis([2 15 -80 100])
l=legend('Standard','IMU Kalman Filter');
set(l,'FontName','Palatino Linotype')

subplot(2,2,3)
plot(t1(200:2315),Y(200:2315),'LineWidth',2,'Color','red')
hold on
% plot(t13(200:2315),1.04*b22(200-10:2315-10),'Color',[0.1 0.9 0.8],'LineWidth',2)
plot(t13(200:2315),data22,'Color',[0.1 0.9 0.8],'LineWidth',2)
ylabel('angle(��)','FontName','Palatino Linotype');
xlabel({'t(s)','(c) From Visual Identity'},'FontName','Palatino Linotype');
axis([2 15 -80 100])
l=legend('Standard','Visual Identity');
set(l,'FontName','Palatino Linotype')

subplot(2,2,4)
plot(t1(200:2315),0.97*Y(200-23:2315-23),'LineWidth',2,'Color','red')
hold on
% plot(t14(200:2315),angle(200:2315),'Color',[0.6 0.3 1],'LineWidth',2)
data1 = a(777-10:2892-10,1)-5;
data2 = 1.04*b22(200-10:2315-10);
result = kalman_filter(data1, data22, 1e-6, 4e-4, data1(1), 1);
plot(t14(200:2315),result,'Color',[0.6 0.3 1],'LineWidth',2)
ylabel('angle(��)','FontName','Palatino Linotype');
xlabel({'t(s)','(d) From Data Fusion'},'FontName','Palatino Linotype');
axis([2 15 -80 100])
l=legend('Standard','Data Fusion');
set(l,'FontName','Palatino Linotype')