import urllib2
import re
import sys
import math

from PIL import Image,ImageDraw,ImageFont,ImageOps
im = Image.open('bmng.jpg')
img_w = im.size[0]/2;   #��ȡͼƬ�Ŀ��
img_h = im.size[1]/2;   #��ȡͼƬ�ĸ߶�
img_a = img_w /180;
lin_with = 4;           #�����ʮ�ּܵ��߿�
lin_long = 10;          #ʮ�ּܵ��߳�

dl = 25;        #����ע�ߵĳ���
angl = 70;      #����ע�ߵ���б�Ƕ�
offset_x = dl*  math.cos( math.radians(angl));      #��ע��X�����ƫ����
offset_y = dl*  math.sin( math.radians(angl));      #��ע��Y�����ƫ����

type = sys.getfilesystemencoding()

url = 'http://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.atom'

print url
# read url
content = urllib2.urlopen(url).read()
# 
content = content.decode("UTF-8").encode(type)
#��ҳ���ݵĸ�ʽ
#</id><title>M 2.7 - 22km NW of Nikiski, Alaska</title><updated>2016-11-24T02:57:07.027Z</updated><link rel="alternate" type="text/html" href="http://earthquake.usgs.gov/earthquakes/eventpage/ak14401253"/><summary type="html"><![CDATA[<dl><dt>Time</dt><dd>2016-11-24 02:33:16 UTC</dd><dd>2016-11-23 17:33:16 -09:00 at epicenter</dd><dt>Location</dt><dd>60.854&deg;N 151.518&deg;W</dd><dt>Depth</dt><dd>72.70 km (45.17 mi)</dd></dl>]]></summary><georss:point>60.8539 -151.5176</georss:point><georss:elev>-72700</georss:elev><category label="Age" term="Past Day"/><category label="Magnitude" term="Magnitude 2"/><category label="Contributor" term="ak"/><category label="Author" term="ak"/></entry>
#nation = re.findall(r'</id><title>M (.*) - (.*) of (.*), (.*)</title><updated>', content)

#��ȡ����ص�����
nation = re.findall(r'</id><title>M (.*) - (.*?)</title><updated>', content)
#��ȡ����ص�ķ���ʱ��
utc_time = re.findall(r'Time</dt><dd>(.*?) (.*?) UTC</dd><dd>', content)
#��ȡ����ص�ĵ���γ������
location = re.findall(r'</dd><dt>Location</dt><dd>(.*)&deg;(.*) (.*)&deg;(.*)</dd><dt>', content)


def lngToPx(num,lng):   #����ֵת��Ϊ��ͼ�ϵ�X����
    if lng=='E':
        #num = 2700 +  (num*15);
        num = img_w +  (num*img_a);
    elif lng=='W':        
        #num = 2700 -  (num*15);
        num = img_w -  (num*img_a);
    else:
        return -1;        
    return num;

def latToPy(num,lat):   #ά��ֵת��Ϊ��ͼ�ϵ�Y����  
    if   lat == 'N':
        #num = 1350*(1 - (num/90));
        num = img_h*(1 - (num/90));
    elif lat == 'S':
        #num = 1350*(1 + (num/90));
        num = img_h*(1 + (num/90));
    else :
        return -1;
    return num;
    


#����һ����ά���������洢���������
coord_num = [[0 for col in range(5)] for row in range(len(nation))] 

#�������ҳ��ȡ����������Ϣ��ת��Ϊ����ֱ���ڵ�ͼ�ϻ��Ƶ�����
def coordinate_process():    
    for loop_c in range(0,len(nation),1):        
        text_pixe = len(nation[loop_c][1])*6; #��������ռ�õ����ص㳤��

        #��ҳ��ȡ�ľ���ֵת��ΪX����
        coord_num[loop_c][0] = int(lngToPx(float(location[loop_c][2]),location[loop_c][3]));
        #��ҳ��ȡ��ά��ֵת��ΪY����
        coord_num[loop_c][1] = int(latToPy(float(location[loop_c][0]),location[loop_c][1]));

        if (coord_num[loop_c][0] > 5100):   #������Ƶ��������ַ���Խ���ͼ
            coord_num[loop_c][2] = coord_num[loop_c][0] - offset_x;
            if (coord_num[loop_c][1] > offset_y):
                coord_num[loop_c][3] = coord_num[loop_c][1] - offset_y;
        else:
            coord_num[loop_c][2] = coord_num[loop_c][0] + offset_x;
            if (coord_num[loop_c][1] > offset_y):
                coord_num[loop_c][3] = coord_num[loop_c][1] - offset_y;

         #������������ַ������µļ�������������Ƶ��ַ������ǵ�ǰ���Ѿ������˵��ַ���
        for compl in range(0,loop_c,1):
            #��������ַ���֮���Y�����X������غ�
            if ((abs(coord_num[loop_c][3] - coord_num[compl][3]) < 25 ) and (abs(coord_num[loop_c][2] - coord_num[compl][2]) < text_pixe+5)):
                if (coord_num[loop_c][3] < img_h - 25):
                    coord_num[loop_c][3] = coord_num[compl][3] + 25;    #���غϾ���������֮��ļ��

        if (coord_num[loop_c][0] > 5100):   #������Ƶ��������ַ���Խ���ͼ
            coord_num[loop_c][4] = coord_num[loop_c][2] - text_pixe - 5;
        else:
            coord_num[loop_c][4] = coord_num[loop_c][2] + text_pixe + 5;

#�ڵ�ͼͼƬ�ϵĵ�������ʮ�ּܱ�Ǻ͵���ص��ע��
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

        #�ڵ�ͼͼƬ�ϵĵ�������ʮ�ּܱ��
        draw.line((coord_num[loop][0]-lin_long,coord_num[loop][1]-lin_long,coord_num[loop][0]+lin_long,coord_num[loop][1]+lin_long), (R,G,B),width = lin_with)
        draw.line((coord_num[loop][0]-lin_long,coord_num[loop][1]+lin_long,coord_num[loop][0]+lin_long,coord_num[loop][1]-lin_long), (R,G,B),width = lin_with)

        #�ڵ�ͼͼƬ�ϵĵ���ص���Ʊ�ע��
        draw.line((coord_num[loop][0],coord_num[loop][1],coord_num[loop][2],coord_num[loop][3]), (R,G,B),width = 1);
        draw.line((coord_num[loop][2],coord_num[loop][3],coord_num[loop][4],coord_num[loop][3]), (R,G,B),width = 1)


        if loop == (len(nation)-1):
            im.save("out.jpg")
            del draw

        print "--------------------------------------"

#�ڵ���صص���Ʊ��ע�߸������Ƶ�����Ϣ�͵�����ʱ���Ѿ�ǿ��ֵ
def draw_text():
    out = Image.open('out.jpg');
    draw_out = ImageDraw.Draw(out);

    for loop_text in range(0,len(nation),1):
        if (coord_num[loop_text][0] > 5100):    #������Ƶ��������ַ���Խ���ͼ
            draw_out.text([coord_num[loop_text][4],coord_num[loop_text][3]],nation[loop_text][0]+"M "+utc_time[loop_text][0]+" "+utc_time[loop_text][1]+" UTC",(0,255,255))
            draw_out.text([coord_num[loop_text][4],coord_num[loop_text][3]-10],nation[loop_text][1],(128,255,0))  
        else:   #���Ƶ��������ַ���
            draw_out.text([coord_num[loop_text][2]+5,coord_num[loop_text][3]],nation[loop_text][0]+"M "+utc_time[loop_text][0]+" "+utc_time[loop_text][1]+" UTC",(0,255,255))
            draw_out.text([coord_num[loop_text][2]+5,coord_num[loop_text][3]-10],nation[loop_text][1],(128,255,0))  

    if loop_text == (len(nation)-1):
        out.save("out.jpg")
        del draw_out 
    
        

coordinate_process();
draw_cross();
draw_text();

print "----Done----"

