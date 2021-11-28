import logging
import os
from typing import List
import fitz
from fitz import Point
from fitz import Rect


class CardWriter:
    def __init__(self, output: str = 'cards.pdf'):
        self.output = output
        self.width, self.height = fitz.paper_size('letter')

    def __draw_guides(
        self,
        shape,
        x0: int,
        y0: float,
        x1: float,
        y1: float,
    ):
        # This all could've been done more elegantly I am certain.
        logging.debug(f'points ({x0}, {y0})\t({x1}, {y1})')
        size = 20
        shape.draw_line(Point(x0, y0 - size), Point(x0, y0 + size))
        shape.draw_line(Point(x0 - size, y0), Point(x0 + size, y0))
        shape.draw_line(Point(x1, y1 - size), Point(x1, y1 + size))
        shape.draw_line(Point(x1 - size, y1), Point(x1 + size, y1))
        shape.draw_line(Point(x0, y1 - size), Point(x0, y1 + size))
        shape.draw_line(Point(x0 - size, y1), Point(x0 + size, y1))
        shape.draw_line(Point(x1, y0 - size), Point(x1, y0 + size))
        shape.draw_line(Point(x1 - size, y0), Point(x1 + size, y0))
        # lol at these hard coded values
        if y0 < 20:
            shape.draw_line(Point(x0, 0), Point(x0, y0))
            shape.draw_line(Point(x1, 0), Point(x1, y0))
        if y0 > 500:
            shape.draw_line(Point(x0, self.height), Point(x0, y1))
            shape.draw_line(Point(x1, self.height), Point(x1, y1))
        if x0 < 40:
            shape.draw_line(Point(0, y0), Point(x0, y0))
            shape.draw_line(Point(0, y1), Point(x0, y1))
        if x0 > 390:
            shape.draw_line(Point(x1, y0), Point(self.width, y0))
            shape.draw_line(Point(x1, y1), Point(self.width, y1))

        shape.finish()
        shape.commit()

    def __images_from_path(self, images_path) -> List[str]:
        """
        looks for png, jpg, jpeg, extensions and ignores other files in the given path
        """
        files = os.listdir(images_path)
        images = []
        extensions = ['png', 'jpg', 'jpeg']
        for file in files:
            path = os.path.join(images_path, file)
            if os.path.isfile(path) and any(
                extension in file for extension in extensions
            ):
                images.append(path)
        return sorted(images)

    def __add_images(self, images: List[str], side_size: int):
        pass

    def create_pdf(self, cards_path: str, side_size: int = 3):
        self.doc = fitz.open()
        front_cards = self.__images_from_path(cards_path + '/front')
        # back_cards = __images_from_path(cards_path + '/back')
        columns = side_size
        rows = side_size
        page = self.doc.new_page(width=self.width, height=self.height)
        horizontal_padding = self.width * (1 / 17)
        vertical_padding = self.height * (1 / 44)
        card_width = (self.width - (horizontal_padding * 2)) / columns
        card_height = (self.height - (vertical_padding * 2)) / rows
        count = 0
        row = 0
        column = 0
        for image_path in front_cards:
            x0 = column * card_width + horizontal_padding
            x1 = x0 + card_width
            y0 = row * card_height + vertical_padding
            y1 = y0 + card_height

            img = fitz.open(image_path)
            rect = Rect(x0, y0, x1, y1)
            pdfbytes = img.convert_to_pdf()
            img.close()
            imgPDF = fitz.open('pdf', pdfbytes)
            page.show_pdf_page(rect, imgPDF, 0)
            count = count + 1
            if count % columns == 0:
                row = row + 1
            column = count % columns

            shape = page.new_shape()
            self.__draw_guides(shape, x0, y0, x1, y1)

        # for a new page call
        # page = doc.new_page(width = width, height = height)
        self.doc.save(self.output)


def main():
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    CardWriter().create_pdf('static/cards')


# i'm not sure how to tell vscode to run __main__.py lmao
if __name__ == '__main__':
    main()
