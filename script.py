import os
import site

site.addsitedir("../../../PDFNetC/Lib")
import sys
from PDFNetPython3 import *

input_path = "./Input/"
output_path = "./Output/"

file_name = "AaDaHI.jpg"


def img_to_pdf(path_to_img):
    if not OCRModule.IsModuleAvailable():
        print("Unable to run OCRTest: PDFTron SDK OCR module not available.")
    else:
        doc = PDFDoc()
        opts = OCROptions()
        opts.AddLang("rus")
        opts.AddLang("deu")
        OCRModule.ImageToPDF(doc, path_to_img, opts)
        doc.Save(output_path + "test.pdf", 0)



def pdf_to_img():
    PDFNet.Initialize()
    draw = PDFDraw()
    doc = PDFDoc(output_path + "redacted.pdf")
    doc.InitSecurityHandler()
    draw.SetDPI(92)
    itr = doc.GetPageIterator()
    draw.Export(itr.Current(), output_path + "AaDaHI.jpg")
    os.remove(output_path + "redacted.pdf")


def get_style(template_coordinates):
    doc = PDFDoc(output_path + "test.pdf")
    doc.InitSecurityHandler()

    page_begin = doc.GetPageIterator()

    rect = Rect(
                template_coordinates['x1'],
                template_coordinates['y1'],
                template_coordinates['x2'],
                template_coordinates['y2'])
                
    extractor = TextExtractor()
    extractor.Begin(page_begin.Current())
    line = extractor.GetFirstLine()
    words = []
    
    while line.IsValid():
        word = line.GetFirstWord()
        while word.IsValid():
            elRect = word.GetBBox()
            elRect.Normalize()
            if elRect.IntersectRect(elRect, rect):
                words.append(word)
            word = word.GetNextWord()
        line = line.GetNextLine()
    
    style = words[0].GetStyle()
    font = Font(style.GetFont())

    return {'font': font, 'size': style.GetFontSize()}


def search_pattern_text(pattern):
    doc = PDFDoc(output_path + "test.pdf")
    doc.InitSecurityHandler()

    txt_search = TextSearch()
    mode = txt_search.GetMode()
    mode |= TextSearch.e_reg_expression | TextSearch.e_highlight

    txt_search.Begin(doc, pattern, mode)
    while True:
        searchResult = txt_search.Run()

        if searchResult.IsFound():
            hlts = searchResult.GetHighlights()
            hlts.Begin(doc)

            quadsInfo = hlts.GetCurrentQuads()
            i = 0
            while i < len(quadsInfo):
                q = quadsInfo[i]
                x1 = min(min(min(q.p1.x, q.p2.x), q.p3.x), q.p4.x)
                x2 = max(max(max(q.p1.x, q.p2.x), q.p3.x), q.p4.x)
                y1 = min(min(min(q.p1.y, q.p2.y), q.p3.y), q.p4.y)
                y2 = max(max(max(q.p1.y, q.p2.y), q.p3.y), q.p4.y)

                template_coordinates = {'x1': x1, 'x2': x2, 'y1': y1, 'y2': y2}
                i = i + 1
        else:
            break
        
    return template_coordinates


def Redact(input, output, vec, app):
    doc = PDFDoc(input)
    if doc.InitSecurityHandler():
        Redactor.Redact(doc, vec, app, False, True)
        doc.Save(output, SDFDoc.e_linearized)


def template_replacement(replacement_word, template_coordinates):
    vec = VectorRedaction()
    vec.append(
        Redaction(
            1,
            Rect(
                template_coordinates['x1'],
                template_coordinates['y1'],
                template_coordinates['x2'],
                template_coordinates['y2']),
            False,
            replacement_word,
        )
    )

    app = Appearance()
    app.RedactionOverlay = True
    app.Border = False

    doc = PDFDoc(output_path + "test.pdf")

    patern_text_style = get_style(template_coordinates)

    app.TextFont = patern_text_style['font']
    app.MaxFontSize = patern_text_style['size']
    app.MinFontSize = patern_text_style['size']
    app.ShowRedactedContentRegions = True

    Redact(doc, output_path + "redacted.pdf", vec, app)
    os.remove(output_path + "test.pdf")


def main():
    PDFNet.Initialize()
    PDFNet.AddResourceSearchPath("./PDFNetC/ResourceSearch/Lib/")

    img_to_pdf(input_path + "AaDaHI.jpg") 
    template_coordinates = search_pattern_text("Lisa Fay")

    template_replacement('word', template_coordinates)
    pdf_to_img()

if __name__ == "__main__":
    main()
    
    
    

