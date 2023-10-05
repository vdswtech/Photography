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
import os
import re
import sys


class IMAGE:
    def __init__(self, img, thumb, web):
        self.image_filepath = img
        self.thumbnail_filepath = thumb
        self.webpage_filepath = web
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
        for tag in tags.keys():
            if tag in ('EXIF ExposureTime', 'EXIF FocalLength', 'EXIF RecommendedExposureIndex'):
                self.exif[tag] = tags[tag]

    def get_img_path(self):
        return self.webpage_filepath

    def set_next(self, next_photo):
        self.next_img = next_photo

    def set_previous(self, previous_photo):
        self.previous_img = previous_photo

    def nav_menu(self):
        code = "\t\t<table width=\"100%\" border=\"1\">\n"
        code += "\t\t\t<tr>\n"
        if self.previous_img is None:
            code += "\t\t\t\t<td align=\"center\">PREV</td>\n"
        else:
            code += "\t\t\t\t<td align=\"center\"><a href=\"" + self.previous_img + "\">PREV</a></td>\n"
        code += "\t\t\t\t<td align=\"center\">"
        code += "<a href=\"../index.html\">Home</a></td>\n"
        if self.next_img is None:
            code += "\t\t\t\t<td align=\"center\">NEXT</td>\n"
        else:
            code += "\t\t\t\t<td align=\"center\"><a href=\"" + self.next_img + "\">NEXT</a></td>\n"
        code += "\t\t\t</tr>\n"
        code += "\t\t<table>\n"

        return code

    def generate_html(self):
        title = self.image_filepath.split('/')[-1]
        code = "<!DOCTYPE html>\n"
        code += "<html>\n\t<head>\n"
        code += "\t\t<title>" + title + "</title>\n"
        code += "\t\t<link rel=\"stylesheet\" href=\"../style.css\">\n"
        code += "\t<head>\n\t<body>\n"
        code += self.nav_menu()
        code += "\t\t\t<tr>\n"
        code += "\t\t\t\t<td><img src=\"" + self.image_filepath + "\" /></td>\n"
        code += "\t\t\t</tr>\n"
        code += "\t\t</table>\n"
        code += self.nav_menu()
        code += "\t</body>\n"
        code += "</html>"
        code = code.replace(self.image_filepath, title)

        output = open(self.webpage_filepath, 'w')
        output.write(code)
        output.close()

    def generate_index_html(self):
        name = self.image_filepath.split('/')[-1]
        results = "<a href=\"" + self.webpage_filepath + "\">"
        results += "<img src=\"" + self.thumbnail_filepath + "\" /></a><br />"
        results += name + "<br />"
        if '/' in str(self.exif['EXIF ExposureTime']):
            results += str(self.exif['EXIF ExposureTime']) + " second<br />"
        else:
            results += str(self.exif['EXIF ExposureTime']) + " seconds<br />"
        results += "ISO " + str(self.exif['EXIF RecommendedExposureIndex'])
        results += "<br />"
        results += str(self.exif['EXIF FocalLength'])
        results += "mm"
        return results


def arguments():
    parser = argparse.ArgumentParser(prog='photos')

    parser.add_argument('filepath', help='Specify the location of the photos')

    return parser.parse_args()


def write_to_file(filepath, data):
    output = open(filepath, "w")
    output.write(data)
    output.close()


def generate_css(args):
    css = "td.top_description\n{\n\tvertical-align:top;\n}\n\n"
    css += "td.bottom_description\n{\n\tvertical-align:bottom;\n}\n\n"
    css += "img\n{\n\tmax-height:1024;\n\theight:auto;\n}"

    write_to_file(args.filepath + "style.css", css)


def generate_index(args, images):
    index = "<!DOCTYPE html>\n"
    index += "<html>\n\t<head>\n"
    index += "\t\t<title>Victoria Wolter photography</title>\n"
    index += "\t\t<link rel=\"stylesheet\" href=\"style.css\" />\n"
    index += "\t</head>\n\t<body>\n"

    for image in images:
        count = 0
        index += "\t\t<h2>" + image + "</h2>\n\t\t<hr />\n"
        index += "\t\t<table>\n"
        for element in range(0, len(images[image])):
            images[image][element].get_exif()
            images[image][element].thumbnail()
            if element == 0:
                images[image][element].set_previous(None)
            else:
                images[image][element].set_previous(images[image][element-1].get_img_path().split('/')[-1])

            if element == len(images[image])-1:
                images[image][element].set_next(None)
            else:
                images[image][element].set_next(images[image][element+1].get_img_path().split('/')[-1])

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


def main():
    images = {}
    args = arguments()

    for entries in sorted(os.listdir(args.filepath)):
        arr = []
        if not re.search('css', entries) and not re.search('js', entries) and not re.search('html', entries):
            for image in sorted(os.listdir(args.filepath + entries)):
                if re.search('IMG_[0-9]{4}.jpg', image):
                    main = args.filepath + entries + "/" + image
                    thumb = args.filepath + entries + "/" + image.split('.')[0] + "_thumb." +  main.split('.')[1]
                    web = args.filepath + entries + "/" + image.split('.')[0] + ".html"
                    arr.append(IMAGE(main, thumb, web))
                    images[entries] = arr

    generate_index(args, images)
    generate_css(args)


if __name__ == "__main__":
    main()
