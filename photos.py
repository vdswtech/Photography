#!/usr/bin/python

# Copyright 2023 Victoria Wolter

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the “Software”), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from PIL import Image
import argparse
import exifread
import hashlib
import os
import re
import sys

class IMAGE:
    def __init__(self, img, thumb, web, check):
        self.image_filepath = img
        self.thumbnail_filepath = thumb
        self.webpage_filepath = web
        self.checksum_filepath = check
        self.exif = {}
        self.next_img = None
        self.previous_img = None

    def thumbnail(self):
        baseheight = 256
        img = Image.open(self.image_filepath)
        hpercent = (baseheight / float(img.size[0]))
        wsize = int((float(img.size[1]) * float(hpercent)))
        img = img.resize((baseheight, wsize), Image.LANCZOS)
        img.save(self.thumbnail_filepath)

    def get_exif(self):
        img = open(self.image_filepath, 'rb')
        tags = exifread.process_file(img)
        for tag in ('EXIF ExposureTime', 'EXIF FocalLength', 'EXIF RecommendedExposureIndex'):
            self.exif[tag] = tags[tag]

    def get_checksum(self):
        md5 = None
        if os.path.exists(self.checksum_filepath):
            md5 = None
        else:
            md5_sum = open(self.checksum_filepath)
            md5 = md5_sum.read()
            md5_sum.close()
        return md5

    def nav_menu(self):
        code = "\t\t<table width=\"1024\" class=\"nav\">\n"
        code += "\t\t\t<tr>\n"
        code += "\t\t\t\t<td align=\"center\">"
        if self.previous_img is None:
            code += "PREV"
        else:
            code += "<a href=\"" + self.previous_img + "\">PREV</a>"
        code += "</td>\n"
        code += "\t\t\t\t<td align=\"center\">"
        code += "<a href=\"../index.html\">Home</a></td>\n"
        code += "\t\t\t\t<td align=\"center\">"
        if self.next_img is None:
            code += "NEXT"
        else:
            code += "<a href=\"" + self.next_img + "\">NEXT</a>"
        code += "</td>\n"
        code += "\t\t\t</tr>\n"
        code += "\t\t<table>\n"
        return code

    def generate_html(self):
        title = self.image_filepath.split('/')[-1]
        code = html_header(title)
        code += self.nav_menu()
        code += "\t\t<table>\n"
        code += "\t\t\t<tr>\n"
        code += "\t\t\t\t<td><img src=\"" + self.image_filepath + "\" /></td>\n"
        code += "\t\t\t</tr>\n"
        code += "\t\t</table>\n"
        code += self.nav_menu()
        code += "\t</body>\n"
        code += "</html>"
        code = code.replace(self.image_filepath, title)
        write_to_file(self.webpage_filepath, code)

    def generate_index_html(self):
        results = "<a href=\"" + self.webpage_filepath + "\">"
        results += "<img src=\"" + self.thumbnail_filepath + "\" /></a><br />"
        results += self.image_filepath.split('/')[-1] + "<br />"
        results += str(self.exif['EXIF ExposureTime']) + " second"
        if '/' not in str(self.exif['EXIF ExposureTime']):
            results += "s"
        results += "<br />ISO " + str(self.exif['EXIF RecommendedExposureIndex'])
        results += "<br />"
        results += str(self.exif['EXIF FocalLength']) + "mm"
        return results

def arguments():
    parser = argparse.ArgumentParser(prog='photos')
    parser.add_argument('filepath', help='Specify the location of the photos')
    return parser.parse_args()
    
def generate_css(args):
    css = "td.top_description\n{\n\tvertical-align:top;\n}\n\n"
    css += "td.bottom_description\n{\n\tvertical-align:bottom;\n}\n\n"
    css += "img\n{\n\tmax-height:1024;\n\theight:auto;\n}\n\n"
    css += "table.nav\n{\n\tborder-style:ridge;\n}"
    write_to_file(args.filepath + "style.css", css)

def generate_index(args, images):
    index = html_header("Victoria Wolter Photography")
    for image in images:
        count = 0
        index += "\t\t<h2>" + image + "</h2>\n\t\t<hr />\n"
        index += "\t\t<table>\n"
        for element in range(0, len(images[image])):
            if element != 0:
                images[image][element].previous_img = images[image][element-1].webpage_filepath.split('/')[-1]
            if element != len(images[image])-1:
                images[image][element].next_img = images[image][element+1].webpage_filepath.split('/')[-1]
            images[image][element].get_exif()
            images[image][element].thumbnail()
            images[image][element].generate_html()
            index += "\t\t\t<td class=\"bottom_description\">"
            index += images[image][element].generate_index_html()
            index += "</td>\n"
            if count == 5:
                index += "\t\t\t</tr>\n"
                index += "\t\t\t<tr>\n"
                count = 0
            else:
                count = count + 1
        index += "\t\t\t</tr>\n\t\t</table>\n"
    index += "\t</body>\n</html>"
    index = index.replace(args.filepath, '')
    write_to_file(args.filepath + "index.html", index)

def html_header(title):
    data = "<!DOCTYPE HTML>\n"
    data += "<html>\n\t<head>\n"
    data += "\t\t<title>" + title + "</title>\n"
    data += "\t\t<link rel=\"stylesheet\" href=\"style.css\" />\n"
    data += "\t</head>\n\t<body>\n"
    return data

def process_images(args):
    images = {}
    for entries in sorted(os.listdir(args.filepath)):
        arr = []
        if not re.search('css', entries) and not re.search('html', entries):
            for image in sorted(os.listdir(args.filepath + entries)):
                if re.search('IMG_[0-9]{4}.jpg', image):
                    main = args.filepath + entries + "/" + image
                    thumb = args.filepath + entries + "/" + image.split('.')[0] + "_thumb." +  main.split('.')[1]
                    web = args.filepath + entries + "/" + image.split('.')[0] + ".html"
                    check = args.filepath + entries + "/" + image.split('.')[0] + ".md5"
                    arr.append(IMAGE(main, thumb, web, check))
                    images[entries] = arr
    return images

def write_to_file(filepath, data):
    output = open(filepath, "w")
    output.write(data)
    output.close()

if __name__ == "__main__":
    args = arguments()
    generate_index(args, process_images(args))
    generate_css(args)
