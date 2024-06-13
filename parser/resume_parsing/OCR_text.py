import pytesseract
import cv2
from pdf2image import convert_from_path
import numpy as np
import pandas as pd

pages = convert_from_path("resume/DocScanner Oct 16, 2023 12-53 PM.pdf")
img = np.array(pages[0])
# for i in pages :
#     img.append(np.array(i))
img = cv2.resize(img, None, fx=0.4, fy=0.4)

# img = cv2.imread("page_image.jpg")
# print(img)
text_img = pytesseract.image_to_data(img)
txt_t = pytesseract.image_to_string(img)
print(txt_t)
# txt = list(map(lambda x: x.split('\t'), text_img.split('\n')))
# df = pd.DataFrame(txt[1:], columns=txt[0])
# df.dropna(inplace=True)
# col_int = ['level', 'page_num', 'block_num', 'par_num', 'line_num', 'word_num',
#        'left', 'top', 'width', 'height', 'conf']
# df[col_int] = df[col_int].astype(int)
# for l,x,y,w,h,c,txt in df[['level','left','top','width','height','conf','text']].values:
#     if l == 5 :
#         cv2.rectangle(img,(x,y),(x+w, y+h), (0,0,0), 2)
#         cv2.putText(img, txt, (x,y), cv2.FONT_HERSHEY_PLAIN, 1, (255,0,0), 1)
# cv2.imshow("bounding box", img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()