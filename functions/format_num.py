import decimal
def currencyInIndiaFormat(n):
    d = decimal.Decimal(str(n))
    if d.as_tuple().exponent < -2:
        s = str(n)
    else:
        s = '{0:.2f}'.format(n)
    l = len(s)
    i = l-1;
    res = ''
    flag = 0
    k = 0
    while i>=0:
        if flag==0:
            res = res + s[i]
            if s[i]=='.':
                flag = 1
        elif flag==1:
            k = k + 1
            res = res + s[i]
            if k==3 and i-1>=0:
                res = res + ','
                flag = 2
                k = 0
        else:
            k = k + 1
            res = res + s[i]
            if k==2 and i-1>=0:
                res = res + ','
                flag = 2
                k = 0
        i = i - 1

    return res[::-1]


def main():
    n = 100.52
    print (currencyInIndiaFormat(n))  # INR 100.52
    n = 1000.108
    print (currencyInIndiaFormat(n))  # INR 1,000.108
    n = 1200000
    print ("INR " + currencyInIndiaFormat(n))  # INR 12,00,000.00

main()