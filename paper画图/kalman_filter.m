function X = kalman_filter(data1, data2, Q, R, x0, P0)
    N = length(data1);

    K = zeros(N,1);
    X = zeros(N,1);
    P = zeros(N,1);

    X(1) = x0;
    P(1) = P0;

    for i = 2:N
        K(i) = P(i-1) / (P(i-1) + R);
        weight = 2/3;
        if X(i-1) >50
            tmp = (1-weight)*data1(i)+weight*data2(i);
        elseif X(i-1) > -50
            tmp = weight*data1(i)+(1-weight)*data2(i);
        else
            tmp = (1-5/6)*data1(i)+5/6*data2(i);
        end
        
        X(i) = X(i-1) + K(i) * (tmp - X(i-1));
        P(i) = P(i-1) - K(i) * P(i-1) + Q;  
    end