import Image
import pytesseract
#open('1.py')
#a = Image.open('captcha.jpg')
#print a
a = pytesseract.image_to_string(Image.open('simple_number.jpeg'))
print type(a)
print len(a)
print a
