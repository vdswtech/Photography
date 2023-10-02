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
import logging
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
            if tag in ('EXIF ExposureTime',
                       'EXIF FocalLength',
                       'EXIF RecommendedExposureIndex'):
                self.exif[tag] = tags[tag]

    def get_img_path(self):
        return self.webpage_filepath

    def set_next(self, next_photo):
        self.next_img = next_photo

    def set_previous(self, previous_photo):
        self.previous_img = previous_photo

    def generate_html(self):
        title = self.image_filepath.split('/')[-1]
        code = "<!DOCTYPE html>\n"
        code += "<html>\n\t<head>\n"
        code += "\t\t<title>" + title + "</title>\n"
        code += "\t\t<link rel=\"stylesheet\" href=\"../style.css\">\n"
        code += "\t<head>\n\t<body>\n"
        code += "\t\t<table>\n"
        code += "\t\t\t<tr>\n"
        code += "\t\t\t\t<td><img src=\""
        code += self.image_filepath
        code += "\" /></td>\n"
        code += "\t\t\t</tr>\n"
        code += "\t\t</table>\n"
        code += "\t</body>\n"
        code += "\t<footer>\n"
        code += "\t\t<table width=\"100%\" border=\"1\">\n"
        code += "\t\t\t<tr>\n"
        if self.previous_img is None:
            code += "\t\t\t\t<td align=\"center\">PREV</td>\n"
        else:
            code += "\t\t\t\t<td align=\"center\"><a href=\""
            code += self.previous_img
            code += "\">PREV</a></td>\n"
        code += "\t\t\t\t<td align=\"center\">"
        code += "<a href=\"../index.html\">Home</a></td>\n"
        if self.next_img is None:
            code += "\t\t\t\t<td align=\"center\">NEXT</td>\n"
        else:
            code += "\t\t\t\t<td align=\"center\"><a href=\""
            code += self.next_img
            code += "\">NEXT</a></td>\n"
        code += "\t\t\t</tr>\n"
        code += "\t\t</table>\n"
        code += "</html>"
        code = code.replace(self.image_filepath, title)

        output = open(self.webpage_filepath, 'w')
        output.write(code)
        output.close()

    def generate_index_html(self):
        name = self.image_filepath.split('/')[-1]
        if '/' in str(self.exif['EXIF ExposureTime']):
            return "<a href=\"" \
                    + self.webpage_filepath \
                    + "\"><img src=\"" \
                    + self.thumbnail_filepath \
                    + "\" class=\"tumbnail\" /></a><br />" \
                    + name \
                    + "<br />" \
                    + str(self.exif['EXIF ExposureTime']) \
                    + " second<br />ISO " \
                    + str(self.exif['EXIF RecommendedExposureIndex']) \
                    + "<br />" \
                    + str(self.exif['EXIF FocalLength']) \
                    + "mm"
        else:
            return "<a href=\"" \
                    + self.webpage_filepath \
                    + "\"><img src=\"" \
                    + self.thumbnail_filepath \
                    + "\" class=\"tumbnail\" /></a><br />" \
                    + name + "<br />" \
                    + str(self.exif['EXIF ExposureTime']) \
                    + " seconds<br />ISO " \
                    + str(self.exif['EXIF RecommendedExposureIndex']) \
                    + "<br />" \
                    + str(self.exif['EXIF FocalLength']) \
                    + "mm"


def arguments():
    parser = argparse.ArgumentParser(prog='photos')

    parser.add_argument('filepath',
                        help='Specify the location of the photos')
    parser.add_argument('-l', '--log',
                        action='store_true',
                        help='Log everything')
    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        help='Be verbose')

    return parser.parse_args()


def logme(args, message):
    if args.log:
        logging.info(message)


def alert(args, message):
    if args.verbose:
        print(message)


def main():
    images = {}
    args = arguments()

    logging.basicConfig(filename="/home/daemoneye/.photo.log",
                        level=logging.INFO)

    for entries in sorted(os.listdir(args.filepath)):
        arr = []
        if not re.search('css', entries) \
                and not re.search('js', entries) \
                and not re.search('html', entries):
            alert(args, "[+] Working on " + entries + " picture.")
            logme(args, "[+] Working on " + entries + " picture.")
            for image in sorted(os.listdir(args.filepath + entries)):
                if re.search('IMG_[0-9]{4}.jpg', image):
                    alert(args, "\t[-] Working on image " + image + ".")
                    logme(args, "[-] Working on image " + image + ".")
                    main = args.filepath + entries + "/" + image
                    thumb = args.filepath
                    thumb += entries
                    thumb += "/"
                    thumb += image.split('.')[0]
                    thumb += "_thumb."
                    thumb += main.split('.')[1]
                    web = args.filepath
                    web += entries
                    web += "/" + image.split('.')[0]
                    web += ".html"
                    img = IMAGE(main, thumb, web)
                    arr.append(img)
                    images[entries] = arr

    index = "<!DOCTYPE html>\n"
    index += "<html>\n"
    index += "\t<head>\n"
    index += "\t\t<title>Victoria Wolter photography</title>\n"
    index += "\t\t<link rel=\"stylesheet\" href=\"style.css\" />\n"
    index += "\t</head>\n"
    index += "\t<body>\n"

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
                images[image][element].set_previous(images[image][element-1]
                                                    .get_img_path()
                                                    .split('/')[-1])
            if element == len(images[image])-1:
                images[image][element].set_next(None)
            else:
                images[image][element].set_next(images[image][element+1]
                                                .get_img_path()
                                                .split('/')[-1])
            images[image][element].generate_html()
            index += "\t\t\t<td class=\"bottom_description\">"
            index += images[image][element].generate_index_html()
            index += "</td>\n"
            if count == 5:
                index += "\t\t\t</tr>\n"
                index += "\t\t\t<br />\n"
                index += "\t\t\t<br />\n"
                index += "\t\t\t<tr>\n"
                count = 0
            else:
                count = count + 1
        index += "\t\t\t</tr>\n\t\t</table>\n"

    index += "\t</body>\n</html>"
    index = index.replace(args.filepath, '')

    css = "td.top_description\n{\n\tvertical-align:top;\n}\n\n"
    css += "td.bottom_description\n{\n\tvertical-align:bottom;\n}\n\n"
    css += "img\n{\n\tmax-height:1024;\n\theight:auto;\n}"

    output = open(args.filepath + "index.html", "w")
    output.write(index)
    output.close()

    output = open(args.filepath + "style.css", "w")
    output.write(css)
    output.close()


if __name__ == "__main__":
    main()
