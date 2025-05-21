# MIT License
#
# Copyright (C) 2024 The Little Hackers.  All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from PIL import Image


def convert_image_to_rgb_mode(
        image: Image,
        fill_color: tuple[int, int, int] = (255, 255, 255)
) -> Image:
    """
    Convert a PIL Image to RGB mode, filling transparent areas with a
    specified color.

    This function is primarily intended for images with transparency (e.g.,
    RGBA or LA modes).  Transparent pixels are blended with the given fill
    color to produce a clean RGB result.  If the image is already in a
    non-alpha mode (e.g., RGB), it is returned unchanged.


    :param image: A PIL Image instance to be converted to RGB.

    :param fill_color: RGB color used to replace transparent pixels when
        removing the alpha channel.  Defaults to white (255, 255, 255).


    :return: A PIL Image instance in RGB mode with no alpha channel.
    """
    if image.mode not in ('RGBA', 'LA'):
        return image

    # In most cases simply discarding the alpha channel will give
    # undesirable result, because transparent pixels also have some
    # unpredictable colors.  It is much better to fill transparent pixels
    # with a specified color.
    background_image = Image.new(image.mode[:-1], image.size, fill_color)
    background_image.paste(image, image.split()[-1])

    return background_image
