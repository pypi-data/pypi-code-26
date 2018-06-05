import time
import sys
import os

def logo1():
    r=r"""      ,           ,
     /             \                     
    ((__---,,,---__))                    
       (_) O O (_)____________          
          \ _ /               |\        
           o_o \Clash Of King | \       
                \   ________  |  *      
                 |||      WW|||
                 |||        |||
"""
    print(r)
def logo2(s):
 sys.stdout.write(s+"\r")
 sys.stdout.flush()
 time.sleep(0.5)
 for i in range(0,len(s)):
    
    a=s[:i]+s[i].upper()+s[i+1:]

    sys.stdout.write(a+"\r")
    sys.stdout.flush()
    time.sleep(0.2)
    


def logo3(s):
    for i in range(0,len(s)):
        sys.stdout.write(s[:i]+"\r")
        sys.stdout.flush()
        time.sleep(0.8)




def logo4(s):
    global flag
    sys.stdout.write(s)
    while 1:
        for i in ["-","\\","/"]:
            if flag==0:
                break
            sys.stdout.write(i+"\b")
            sys.stdout.flush()
            time.sleep(0.2)




def log5():
    s1="   $$$$    $$   $$$$$$ $$     $$ $$$$$$    $$    $$ $$$$$$ $$  $$"
    s2="    $$     $$   $$  $$ $$     $$ $$         $$  $$  $$  $$ $$  $$"
    s3="    $$     $$   $$  $$ $$     $$ $$          $$$$   $$  $$ $$  $$"
    s4="    $$     $$   $$  $$  $$   $$  $$$$$$       $$    $$  $$ $$  $$"
    s5="    $$     $$   $$  $$   $$ $$   $$           $$    $$  $$ $$  $$"
    s6="   $$$$    $$$$ $$$$$$    $$$    $$$$$$       $$    $$$$$$ $$$$$$"
    s = s1+"\n"+s2+"\n"+s3+"\n"+s4+"\n"+s5+"\n"+s6
    L=[s1,s2,s3,s4,s5,s6]

    time.sleep(0.7)
    for i in L:
        print(i)
        time.sleep(0.7)

    for i in "ILOVEYOU":
        time.sleep(0.8)
        os.system("cls")
        print("\n\n\n")
        print(s.replace("$",i))
    #os.system("cls")


