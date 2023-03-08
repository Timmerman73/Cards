import argparse
import logging
import os
from typing import List
import fitz # pip install PyMuPDF
from fitz import Point
from fitz import Rect
from itertools import zip_longest
import json
from math import sqrt


# https://stackoverflow.com/a/434411/104527
def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


class CardWriter:
    def __init__(self, cards_path: str, output: str, col_num: int, row_num: int,guides_enabled=True):
        """Initialises the CardWriter class and saves important variables.

        Args:
            cards_path (str): Lists where to look for the imput images.
            output (str): Lists the location to save the pdf.
            col_num (int): How many colums there should be (And how big each row is)
            row_num (int): How many rows there should be (How many rows are on each page.)
            
        self.output = output location
        self.width, self.height = Width and Height of an A4 paper in pixels
        self.col_num = col_num
        self.row_num = row_num
        self.horizontal_padding = Space in pixels reserved on the sides of the document.
        self.vertical_padding = Space in pixels reserved on te top and bottom of the document.
        self.card_width = Width of each card in pixels
        self.card_height = Height of each card in pixels
        self.card_count = How many times each card should be printed.
        self.cards_path = Where the cards are located
        
        """
        self.output = output
        self.width, self.height = fitz.paper_size('A4')
        self.col_num = col_num
        self.row_num = row_num
        self.horizontal_padding = self.width * (1 / 17)
        self.vertical_padding = self.height * (1 / 44)
        self.card_width = (self.width - (self.horizontal_padding * 2)) / col_num
        self.card_height = (self.height - (self.vertical_padding * 2)) / row_num
        self.card_count = self.__card_counts(cards_path)
        self.cards_path = cards_path
        self.guides_enabled = guides_enabled

    def __card_counts(self,cards_path):
        content = [i for i in os.listdir(cards_path) if i.endswith(".json")]
        if content:
            with open(f"{cards_path}/{content[0]}") as file:
                return {k.lower(): v for k, v in json.load(file).items()}
        else:
            return None




    def __draw_guides(
        self,
        shape,
        x0: int,
        y0: float,
        x1: float,
        y1: float,
    ):
        """Black magic by James Power which i will not touch."""
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

    def __group_images(self, images: List[str]):
        """Groups images into rows and colums using grouper function.

        Args:
            images (List[str]): Images all in one long list

        Returns:
            List: Matrix with grouped images
        """
        groupedRows = grouper(images, self.col_num)
        groupedPages = grouper(groupedRows, self.row_num)
        return groupedPages

    def __images_from_path(self, images_path):
        """
        looks for png, jpg, jpeg, extensions and ignores other files in the given path
        """
        files = os.listdir(images_path)
        images = []
        extensions = ['png', 'jpg', 'jpeg']
        for file in files:
            path = os.path.join(images_path, file)
            if os.path.isfile(path) and any(extension in file for extension in extensions):
                basename = os.path.basename(path)
                #Code block responsible for adding images multiple times
                if self.card_count is not None:
                    if basename in self.card_count:
                        for _ in range(self.card_count[basename]):
                            images.append(path)
                    else:
                        images.append(path)
                        
                else:
                    images.append(path)
        return sorted(images)

    def __add_images(self, images: List[List[str]]):
        pdf_page = self.doc.new_page(width=self.width, height=self.height)
        for row_index, row in enumerate(images):
            if row is not None:
                for image_index, image in enumerate(row):
                    if image is not None:
                        x0 = image_index * self.card_width + self.horizontal_padding 
                        x1 = x0 + self.card_width 
                        y0 = row_index * self.card_height + self.vertical_padding
                        y1 = y0 + self.card_height
                        rect = Rect(x0, y0, x1, y1)
                        img = fitz.open(image)
                        pdfbytes = img.convert_to_pdf()
                        img.close()
                        imgPDF = fitz.open('pdf', pdfbytes)
                        pdf_page.show_pdf_page(rect, imgPDF, 0)
                        shape = pdf_page.new_shape()
                        # Could tell draw guides where we are on the screen
                        # instead of having the magic numbers in that function
                        # determine where to draw the guides from the edges of
                        # sheet. row_index & image_index should be enough here.
                        if self.guides_enabled:
                            self.__draw_guides(shape, x0, y0, x1, y1)

    def __align_back_cards(self, back_pages):
        cards = []
        for page in back_pages:
            if page is None:
                cards.append(page)
                continue
            page_cards = []
            cards.append(page_cards)
            for row in page:
                if row is None:
                    page_cards.append(row)
                    continue
                page_cards.append(reversed(list(row)))
        return cards


    def create_pdf(self):
        self.doc = fitz.open()
        front_cards = self.__images_from_path(self.cards_path + '/front')
        back_cards = self.__images_from_path(self.cards_path + '/back')
        difference = len(front_cards) - len(back_cards)
        if difference > 0 and len(back_cards) > 0:
            back_cards.extend([back_cards[-1] for _ in range(difference)])
        front_cards = self.__group_images(front_cards)
        back_cards = self.__align_back_cards(self.__group_images(back_cards))
        combined = [val for pair in zip(front_cards, back_cards) for val in pair]
        for image_page in combined:
            self.__add_images(image_page)
        self.doc.save(self.output)


def main():
    """Main function. Finds all directories in input directory and creates a seperate PDF for each of them."""
    dirs = os.listdir("input")
    if not os.path.exists("output") and not os.path.isdir("output"):
        os.remove("output")
        os.mkdir("output")
    for dir in dirs:
        CardWriter(cards_path=f"input/{dir}", output=f"output/{dir}.pdf", col_num=3,row_num=5).create_pdf()


# i'm not sure how to tell vscode to run __main__.py lmao
if __name__ == '__main__':
    main()
