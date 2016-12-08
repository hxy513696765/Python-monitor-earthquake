import urllib2
import re
import sys
import math

from PIL import Image,ImageDraw,ImageFont,ImageOps
im = Image.open('bmng.jpg')
img_w = im.size[0]/2;   #获取图片的宽度
img_h = im.size[1]/2;   #获取图片的高度
img_a = img_w /180;
lin_with = 4;           #画标记十字架的线宽
lin_long = 10;          #十字架的线长

dl = 25;        #画标注线的长度
angl = 70;      #画标注线的倾斜角度
offset_x = dl*  math.cos( math.radians(angl));      #标注线X坐标的偏移量
offset_y = dl*  math.sin( math.radians(angl));      #标注线Y坐标的偏移量

type = sys.getfilesystemencoding()

url = 'http://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.atom'

print url
# read url
content = urllib2.urlopen(url).read()
# 
content = content.decode("UTF-8").encode(type)
#网页内容的格式
#</id><title>M 2.7 - 22km NW of Nikiski, Alaska</title><updated>2016-11-24T02:57:07.027Z</updated><link rel="alternate" type="text/html" href="http://earthquake.usgs.gov/earthquakes/eventpage/ak14401253"/><summary type="html"><![CDATA[<dl><dt>Time</dt><dd>2016-11-24 02:33:16 UTC</dd><dd>2016-11-23 17:33:16 -09:00 at epicenter</dd><dt>Location</dt><dd>60.854&deg;N 151.518&deg;W</dd><dt>Depth</dt><dd>72.70 km (45.17 mi)</dd></dl>]]></summary><georss:point>60.8539 -151.5176</georss:point><georss:elev>-72700</georss:elev><category label="Age" term="Past Day"/><category label="Magnitude" term="Magnitude 2"/><category label="Contributor" term="ak"/><category label="Author" term="ak"/></entry>
#nation = re.findall(r'</id><title>M (.*) - (.*) of (.*), (.*)</title><updated>', content)

#获取地震地点名称
nation = re.findall(r'</id><title>M (.*) - (.*?)</title><updated>', content)
#获取地震地点的发生时间
utc_time = re.findall(r'Time</dt><dd>(.*?) (.*?) UTC</dd><dd>', content)
#获取地震地点的地理经纬度坐标
location = re.findall(r'</dd><dt>Location</dt><dd>(.*)&deg;(.*) (.*)&deg;(.*)</dd><dt>', content)


def lngToPx(num,lng):   #经度值转换为地图上的X坐标
    if lng=='E':
        #num = 2700 +  (num*15);
        num = img_w +  (num*img_a);
    elif lng=='W':        
        #num = 2700 -  (num*15);
        num = img_w -  (num*img_a);
    else:
        return -1;        
    return num;

def latToPy(num,lat):   #维度值转换为地图上的Y坐标  
    if   lat == 'N':
        #num = 1350*(1 - (num/90));
        num = img_h*(1 - (num/90));
    elif lat == 'S':
        #num = 1350*(1 + (num/90));
        num = img_h*(1 + (num/90));
    else :
        return -1;
    return num;
    


#申请一个二维数组用来存储处理的数据
coord_num = [[0 for col in range(5)] for row in range(len(nation))] 

#处理从网页获取到的坐标信息，转换为可以直接在地图上绘制的坐标
def coordinate_process():    
    for loop_c in range(0,len(nation),1):        
        text_pixe = len(nation[loop_c][1])*6; #地理名称占用的像素点长度

        #网页获取的经度值转换为X坐标
        coord_num[loop_c][0] = int(lngToPx(float(location[loop_c][2]),location[loop_c][3]));
        #网页获取的维度值转换为Y坐标
        coord_num[loop_c][1] = int(latToPy(float(location[loop_c][0]),location[loop_c][1]));

        if (coord_num[loop_c][0] > 5100):   #避免绘制地理名称字符串越界地图
            coord_num[loop_c][2] = coord_num[loop_c][0] - offset_x;
            if (coord_num[loop_c][1] > offset_y):
                coord_num[loop_c][3] = coord_num[loop_c][1] - offset_y;
        else:
            coord_num[loop_c][2] = coord_num[loop_c][0] + offset_x;
            if (coord_num[loop_c][1] > offset_y):
                coord_num[loop_c][3] = coord_num[loop_c][1] - offset_y;

         #处理地理名称字符串上下的间隔，避免后面绘制的字符串覆盖掉前面已经绘制了的字符串
        for compl in range(0,loop_c,1):
            #如果两个字符串之间的Y间隔和X间隔有重合
            if ((abs(coord_num[loop_c][3] - coord_num[compl][3]) < 25 ) and (abs(coord_num[loop_c][2] - coord_num[compl][2]) < text_pixe+5)):
                if (coord_num[loop_c][3] < img_h*2 - 25):
                    coord_num[loop_c][3] = coord_num[compl][3] + 25;    #有重合就增加两者之间的间隔

        if (coord_num[loop_c][0] > 5100):   #避免绘制地理名称字符串越界地图
            coord_num[loop_c][4] = coord_num[loop_c][2] - text_pixe - 5;
        else:
            coord_num[loop_c][4] = coord_num[loop_c][2] + text_pixe + 5;

#在地图图片上的地震点绘制十字架标记和地震地点标注线
def draw_cross():
    draw = ImageDraw.Draw(im) 
    for loop in range(0,len(nation),1):
        print "   Nation  : "+nation[loop][1]
       # print "   Area    : "+nation[loop][2]
        print " Magnitude : "+nation[loop][0]
        print "Origin Time: "+utc_time[loop][0]+" "+utc_time[loop][1]+" UTC"
        print " Location  : "+location[loop][0]+location[loop][1]+" "+location[loop][2]+location[loop][3]
        print ("X: ",coord_num[loop][0])
        print ("Y: ",coord_num[loop][1])

        R = 255;
        G = (loop*8)%256;
        B = ((loop%10)*27)%256;

        #在地图图片上的地震点绘制十字架标记
        draw.line((coord_num[loop][0]-lin_long,coord_num[loop][1]-lin_long,coord_num[loop][0]+lin_long,coord_num[loop][1]+lin_long), (R,G,B),width = lin_with)
        draw.line((coord_num[loop][0]-lin_long,coord_num[loop][1]+lin_long,coord_num[loop][0]+lin_long,coord_num[loop][1]-lin_long), (R,G,B),width = lin_with)

        #在地图图片上的地震地点绘制标注线
        draw.line((coord_num[loop][0],coord_num[loop][1],coord_num[loop][2],coord_num[loop][3]), (R,G,B),width = 1);
        draw.line((coord_num[loop][2],coord_num[loop][3],coord_num[loop][4],coord_num[loop][3]), (R,G,B),width = 1)


        if loop == (len(nation)-1):
            im.save("out.jpg")
            del draw

        print "--------------------------------------"

#在地震地地点绘制标的注线附近绘制地理信息和地震发生时间已经强度值
def draw_text():
    out = Image.open('out.jpg');
    draw_out = ImageDraw.Draw(out);

    for loop_text in range(0,len(nation),1):
        #把UTC时间转换成UTC+8的时间
        utc8 = str((int(utc_time[loop_text][1][0:2])+8)%24);
        if len(utc8) == 1:
            utc8 = '0'+ utc8;
        utc8 = utc8+utc_time[loop_text][1][2:];
        
        if (coord_num[loop_text][0] > 5100):    #避免绘制地理名称字符串越界地图            
            draw_out.text([coord_num[loop_text][4],coord_num[loop_text][3]],nation[loop_text][0]+"M "+utc_time[loop_text][0]+" "+utc8+" UTC+8",(0,255,255))
            draw_out.text([coord_num[loop_text][4],coord_num[loop_text][3]-10],nation[loop_text][1],(128,255,0))

        else:   #绘制地理名称字符串
            draw_out.text([coord_num[loop_text][2]+5,coord_num[loop_text][3]],nation[loop_text][0]+"M "+utc_time[loop_text][0]+" "+utc8+" UTC+8" ,(0,255,255))
            draw_out.text([coord_num[loop_text][2]+5,coord_num[loop_text][3]-10],nation[loop_text][1],(128,255,0))

    if loop_text == (len(nation)-1):
        out.save("out.jpg")
        del draw_out 
    
        

coordinate_process();
draw_cross();
draw_text();

print "----Done----"

