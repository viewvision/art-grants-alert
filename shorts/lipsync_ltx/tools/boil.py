import sys, cv2, numpy as np
for p in sys.argv[1:]:
    c=cv2.VideoCapture(p); fr=[]
    while True:
        ok,f=c.read()
        if not ok: break
        fr.append(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY))
    fr=np.stack(fr).astype(np.int16)
    e=cv2.dilate((cv2.Canny(fr[len(fr)//2].astype(np.uint8),50,150)>0).astype(np.uint8),np.ones((5,5),np.uint8))>0
    print(p, round(float((np.abs(np.diff(fr,axis=0))[:,e]>40).mean()*100),2))
