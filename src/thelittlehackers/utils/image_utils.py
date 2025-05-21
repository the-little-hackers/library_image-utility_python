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

from enum import StrEnum
from enum import auto
from typing import Generator
from typing import Iterable
from typing import NamedTuple

from PIL import Image


class ImageCropAlignment(StrEnum):
    """
    Alignment strategies to use when cropping an image.
    """
    # Center the crop area within the image.
    CENTER = auto()

    # Align the crop area to the left (horizontal crop) or top (vertical
    # crop).
    LEFT_OR_TOP = auto()

    #  Align the crop area to the right (horizontal crop) or bottom
    #  (vertical crop).
    RIGHT_OR_BOTTOM = auto()


class ImageCropShape(StrEnum):
    """
    Shapes of the cropping area.
    """
    # Crop the image using a circular shape.
    CIRCLE = auto()

    # Crop the image using a rectangular shape.
    RECTANGLE = auto()


class ImageFilter(StrEnum):
    """
    Resampling filters used when resizing an image.
    """
    # High-quality downsampling filter.
    ANTI_ALIAS = auto()

    # Cubic interpolation over a 4x4 pixel area for smoother results.
    BICUBIC = auto()

    # Linear interpolation over a 2x2 pixel area.
    BILINEAR = auto()

    # Nearest-neighbor resampling (fastest but lowest quality).
    NEAREST_NEIGHBOR = auto()


class ImageVariant(StrEnum):
    """
    Predefined image size variants for various use cases.
    """
    # High-resolution version for detailed views.
    LARGE = auto()

    # Medium-sized version for general-purpose display.
    MEDIUM = auto()

    # Small version for lightweight display.
    SMALL = auto()

    # Very small size, typically used for previews or avatars.
    THUMBNAIL = auto()



class ImageVariantSize(NamedTuple):
    """
    Image variant with a specific width and height.
    """
    variant: ImageVariant  # The variant type.
    size: tuple[int, int]  # The target width and height in pixels.


PIL_FILTER_MAPPING = {
    ImageFilter.NEAREST_NEIGHBOR: Image.Resampling.NEAREST,
    ImageFilter.BILINEAR: Image.Resampling.BILINEAR,
    ImageFilter.BICUBIC: Image.Resampling.BICUBIC,
    ImageFilter.ANTI_ALIAS: Image.Resampling.LANCZOS,
}


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


def generate_image_variants(
        image,
        variant_sizes: Iterable[ImageVariantSize],
        crop_alignment: ImageCropAlignment = ImageCropAlignment.CENTER,
        image_filter: ImageFilter = ImageFilter.NEAREST_NEIGHBOR,
        require_cropping: bool = False,
        require_match_orientation: bool = False
) -> Generator[tuple[ImageVariant, Image], None, None]:
    """
    Generate multiple resized versions of an image based on a list of
    variant sizes.

    Each generated image is resized according to the dimensions specified
    in the `variant_sizes` list.  Optional cropping and resampling filters
    can be applied to control the output's appearance and quality.


    :param image: A PIL Image instance to generate resized variants from.

    :param variant_sizes: A list of image variants, each specifying the
        target size and associated variant name.

    :param image_filter: The resampling filter to use for resizing.
        Default to `ImageFilter.NEAREST_NEIGHBOR`.

    :param require_cropping: If `True`, each image is cropped to match the
        aspect ratio of the target size.  Default to `False`.

    :param crop_alignment: Specify how to align the image when cropping.
        Default to `ImageCropAlignment.CENTER`.

    :param require_match_orientation: If `True`, adjust the target size to
        match the orientation (portrait/landscape) of the input image.
        Default to `False`.


    :return: A generator that yields pairs of image variant type and the
        corresponding resized PIL Image instance.
    """
    for variant_size in variant_sizes:
        yield (
            variant_size.variant,
            resize_image(
                image,
                variant_size.size,
                image_filter=image_filter,
                require_cropping=require_cropping,
                crop_alignment=crop_alignment,
                require_match_orientation=require_match_orientation
            )
        )


def resize_image(
        image: Image,
        canvas_size: tuple[int, int],
        crop_alignment: ImageCropAlignment = ImageCropAlignment.center,
        crop_shape: ImageCropShape = ImageCropShape.RECTANGLE,
        image_filter: ImageFilter = ImageFilter.NEAREST_NEIGHBOR,
        require_cropping: bool =False,
        require_match_orientation: bool = False
) -> Image:
    """
    Resize and optionally crop a PIL image to fit a specified canvas size.

    This function adjusts the input image to match the desired dimensions
    while preserving its aspect ratio.  It supports optional cropping and
    resampling filters for better control over output quality.


    :param image: A PIL Image instance to be resized.

    :param canvas_size: The target dimensions as a `(width, height)` tuple.

    :param image_filter: The filter to apply when resizing.  Default to
        `ImageFilter.NEAREST_NEIGHBOR`.

    :param require_cropping: If `True`, the image will be cropped to
        fit the canvas.  Default to `False`.

    :param crop_alignment: The alignment strategy to cropping the image.
        Default to `ImageCropAlignment.CENTER`.

    :param crop_shape: The shape of the crop area. Default to
        `ImageCropShape.RECTANGLE`.

    :param require_match_orientation: If `True`, adjust the canvas size to
        match the image's orientation.  Default to` False`.


    :return: A new PIL Image instance that has been resized and optionally
        cropped.
    """
    source_width, source_height = image.size
    source_aspect = source_width / float(source_height)

    canvas_width, canvas_height = canvas_size
    canvas_aspect = canvas_width / float(canvas_height)

    if require_match_orientation:
        if (
            source_aspect > 1.0 > canvas_aspect
            or source_aspect < 1.0 < canvas_aspect
        ):
            canvas_width, canvas_height = canvas_height, canvas_width
            canvas_aspect = canvas_width / float(canvas_height)

    if require_cropping:
        if source_aspect > canvas_aspect:
            destination_width = int(source_height * canvas_aspect)

            match crop_alignment:
                case ImageCropAlignment.LEFT_OR_TOP:
                    offset = 0
                case ImageCropAlignment.RIGHT_OR_BOTTOM:
                    offset = source_width - destination_width
                case ImageCropAlignment.CENTER:
                    offset = (source_width - destination_width) / 2

            box = (offset, 0, offset + destination_width, source_height)
        else:
            destination_height = int(source_width / canvas_aspect)

            match crop_alignment:
                case ImageCropAlignment.LEFT_OR_TOP:
                    offset = 0
                case ImageCropAlignment.RIGHT_OR_BOTTOM:
                    offset = source_height - destination_height
                case ImageCropAlignment.CENTER:
                    offset = (source_height - destination_height) / 2

            box = (0, offset, source_width, destination_height + offset)

    else:
        if canvas_aspect > source_aspect:
            # The canvas aspect is greater than the image aspect when the canvas's
            # width is greater than the image's width, in which case we need to
            # crop the left and right edges of the image.
            destination_width = int(canvas_aspect * source_height)
            offset = (source_width - destination_width) / 2
            box = (offset, 0, source_width - offset, source_height)
        else:
            # The image aspect is greater than the canvas aspect when the image's
            # width is greater than the canvas's width, in which case we need to
            # crop the top and bottom edges of the image.
            destination_height = int(source_width / canvas_aspect)
            offset = (source_height - destination_height) / 2
            box = (0, offset, source_width, source_height - offset)

    cropped_image = image.crop(box)
    resized_image = cropped_image.resize(
        (canvas_width, canvas_height),
        PIL_FILTER_MAPPING[image_filter]
    )

    return resized_image
