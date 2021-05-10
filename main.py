

#  This code/project is belong to dev__7
import os
import drowsy_predict as dp
import predict_eye as pe
def switch(case):
    if case==1:
        dp.main()

    if case==2:
        pe.main()



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print("Driver_Drowsy_Detection_System")
    print("press 1 for live prediction ")
    print("press 2 for prediction in images")
    ch=int(input())
    switch(ch)


