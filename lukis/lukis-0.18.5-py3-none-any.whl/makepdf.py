#!python3
"""
    Generate pdf file from graphic stream

    Require the information of fonts stored in myfont.py
"""
import numpy as np
from datetime import datetime
import os
import zlib as gzip
from . import myfont
from . import myimage
from . import command

#Global constants
SPACE = " "
TAB = " "*4
COMMA = ","
QUOTE = "\""
QUOTE_SINGLE = "\'"
EOL = "\n"

def itos (Int_Value):
        return "%d" %Int_Value
def GetPaperSize(PaperSize, Unit="pt", Portrait=True):
    #Allow two input formats:
    #    eg.    PaperSize = "A4"
    #    or    PaperSize = [400, 500]
    #    return
    CommonPaperSizeByName = {
        "Letter"        :"612 792",
        "Tabloid"        :"792 1224",
        "Ledger"        :"1224 792",
        "Legal"            :"612 1008",
        "Statement"        :"396 612",
        "Executive"        :"540 720",
        "A0"            :"2384 3371",
        "A1"            :"1685 2384",
        "A2"            :"1190 1684",
        "A3"            :"842 1190",
        "A4"            :"595 842",
        "A5"            :"420 595",
        "B4"            :"729 1032",
        "B5"            :"516 729",
        "Folio"            :"612 936",
        "Quarto"        :"610 780",
        "10x14"            :"720 1008"
        }
    if isinstance(PaperSize, list) or isinstance(PaperSize, tuple):
        if len(PaperSize) ==2:
            if Unit=="pt":
                return itos(int(PaperSize[0])) +\
                    " " +\
                    itos(int(PaperSize[1]))
            else:
                return ftos(ToPt(PaperSize[0],Unit)) +\
                    " " +\
                    ftos(ToPt(PaperSize[1],Unit))
        else:
            print("Invalid Manual Paper Size Parameters." +
                    " Assume Letter")
            return CommonPaperSizeByName["Letter"]

    else:
        if PaperSize in CommonPaperSizeByName:
            S = CommonPaperSizeByName[PaperSize]
            if Portrait == False:
                # assume landscape. Inverse the position for Paper Size
                S = S.split(" ")
                S = S[1] + " " + S[0]

            print(CommonPaperSizeByName[PaperSize])
            return S

        else:
            print("Name Paper of Paper Size Not Valid. Asssume Letter")
            return CommonPaperSizeByName["Letter"]
def Decimal_To_10_DigitsString(value):
    Decimal = int(value) # just in case if user put something else.
    S = "%d"%Decimal
    AdditionalZerosd = "0" * (10- len(S) )
    return AdditionalZerosd + S
def DecimalToAsciiHex(decimal):
    S = "%x"%decimal
    if len(S) ==1:
        S = "0" + S
    return S

def ftos (Float_Value):
    """
    string ftos(float)

    convert float to string
    Instead of using python's ftos(), use this one to control the precision
    my Float to String mini function

    Precision = %.4f
    Unnecessary 0 will be discarded
    """
    S= "%.4f" %Float_Value
    n = len(S)
    if S[n-5] == '.' :
        if S[ n-4 : n ] =="0000":
            S = S[ 0 : n-5 ]
        elif S[n-3:n] == "000":
            S = S[ 0 : n-3]
        elif S[n-2:n] == "00":
            S = S[ 0 : n-2]
        elif S[n-1] == "0":
            S = S[ 0 : n-1]
    return S
def qsplit(S,
        separator = COMMA,
        quote_Double = QUOTE,
        quote_Single = QUOTE_SINGLE):
    """
    splits S according to separator,
    but ignores those within the quote marks
    """
    Location = []
    i = 0
    while i < len(S):
        #loop out until the end of QUOTE
        if (S[i] == quote_Double) | (S[i] == quote_Single) :
            quote_this = S[i]
            #print("hit q")
            i += 1
            while S[i] != quote_this:
                i += 1

        if S[i] == separator:
            Location += [i]
        i += 1

    if len(Location) == 0:
        return [S]
    Result = [
                S[:Location[0] ]
                ]
    for n in range(len(Location)):
        if n != len(Location) -1:
            Result += [
                        S[Location[n]+1 : Location[n + 1]]
                        ]
        else:
            Result += [
                        S[Location[n]+1 : ]
                        ]

    return Result

def lineto(parameters):
    """
    string lineto (string x, string y)
    """
    [x,y] = parameters
    return x\
            + SPACE\
            + y\
            + SPACE\
            + "l"\
            + EOL
def moveto(parameters):
    """
    string moveto (string x, string y)
    """
    [x,y] = parameters
    return x\
            + SPACE\
            + y\
            + SPACE\
            + "m"\
            + EOL
def curveto(parameters):
    [x1, y1, x2, y2, x3, y3] = parameters
    return x1\
            + SPACE\
            + y1\
            + SPACE\
            + x2\
            + SPACE\
            + y2\
            + SPACE\
            + x3\
            + SPACE\
            + y3\
            + SPACE\
            + "c"\
            + EOL
def stroke():
    return "S" + EOL
def close():
    return "h" + EOL
def close_stroke():
    return "s" + EOL
def fill():
    return "f" + EOL
def fill_stroke():
    return "B" + EOL
def close_fill_stroke():
    return "b" + EOL

def translate_coordinate(args):
    """
    This is the generic one
    """
    [tx, ty] = args
    return "1 0 0 1 "\
            + tx\
            + SPACE\
            + ty\
            + " cm"\
            + EOL
def rotate_coordinate(args):
    [angle] = args
    radian = float(angle) * np.pi/180

    return ftos( np.cos(radian))\
            + SPACE\
            + ftos( np.sin(radian))\
            + SPACE\
            + ftos(-1*np.sin(radian) )\
            + SPACE\
            + ftos(np.cos(radian))\
            + SPACE\
            + "0"\
            + SPACE\
            + "0"\
            + SPACE\
            + "cm"\
            + EOL
def scale(args):
    [scalex, scaley] = args
    return  scalex\
            + SPACE\
            + "0 0"\
            + SPACE\
            + scaley\
            + SPACE\
            + "0 0"\
            + " cm"\
            + EOL

def ToPdfRGB(R, G, B):
    """
    Tuple ToPdfRGB(Tuple RGB)

    Convert the standard RGB (0 ~ 255)
    to pdf normalized RGB (0 ~ 1)

    The RGB is 3 elements Tuple, i.e, (R, G, B).
    Returns pdfRGB in tupl, , i.e, (pdfR, pdfG, pdfB)
    """
    return (1.0*R/255, 1.0*G/255, 1.0*B/255)

def setrgb_stroking(args):
    R = int(args[0])
    G = int(args[1])
    B = int(args[2])
    (pdf_R, pdf_G, pdf_B) = ToPdfRGB (R, G, B)
    return ftos(pdf_R)\
            + SPACE\
            + ftos(pdf_G)\
            + SPACE\
            + ftos(pdf_B)\
            + SPACE\
            + "RG"\
            + EOL
def setrgb_nonstroking(args):
    R = int(args[0])
    G = int(args[1])
    B = int(args[2])
    (pdf_R, pdf_G, pdf_B) = ToPdfRGB (R, G, B)
    return ftos(pdf_R)\
            + SPACE\
            + ftos(pdf_G)\
            + SPACE\
            + ftos(pdf_B)\
            + SPACE\
            + "rg"\
            + EOL
def setlinewidth(args):
    [linewidth] = args
    return linewidth + SPACE + "w" + EOL
def setdash(args):
    return

# pdf generic
def text_setposition(x ,y):
    return x\
            + SPACE\
            + y\
            + SPACE\
            + "Td"\
            + EOL

def text_show(thetext):
    return "("\
            + thetext\
            + ")"\
            + SPACE\
            + "Tj"\
            + EOL

# Only need to set once in the pdf document
def setfont(args):
    [font, fontsize] = args
    return "BT"\
            + EOL\
            + "/"\
            + myfont.GetShortFontName(font)\
            + SPACE\
            + fontsize\
            + SPACE\
            + "Tf"\
            + EOL\
            + "ET"\
            + EOL
#Non pdf Generic

def Remove_Quotes(thetext, quote_Double = QUOTE,
    quote_Single = QUOTE_SINGLE):
    if thetext[0] == quote_Double:
        if thetext[-1] == quote_Double:
            return thetext[1:-1]
        else:
            print("Error removing quotes ! Do nothing")
            return thetext
    elif thetext[0] == quote_Single:
        if thetext[-1] == quote_Single:
            return thetext[1:-1]
        else:
            print("Error removing quotes ! Do nothing")
            return thetext
    else:
        print("Error removing quotes ! Do nothing")
        return thetext
def InsertEscapeBeforeParenthesis(thetext):
    thetext = thetext.replace("(", "\(")
    thetext = thetext.replace(")", "\)")
    return thetext
def text(args):
    [x, y, thetext] = args
    thetext = Remove_Quotes(thetext)
    thetext = InsertEscapeBeforeParenthesis(thetext)
    return "BT"\
            + EOL\
            + text_setposition(x,y)\
            + text_show(thetext)\
            + "ET"\
            + EOL

_PictureNumber_ = 0
def increasePictureNumber():
    global _PictureNumber_
    _PictureNumber_ += 1
def resetPictureNumber():
    global _PictureNumber_
    _PictureNumber_ = 0

_PictureFilename_ = []
def appendPictureFilename(f):
    global _PictureFilename_
    _PictureFilename_ += [f]
def resetPictureFilename():
    global _PictureFilename_
    _PictureFilename_ = []


def insertpicture(args):#x, y, w, h):
    [x, y, w, h, picturefilename] =  args

    #Eg: "400 0 0 400 200 150 cm\n"
    S    = "q\n" +\
        w + " 0 0 " +\
        h + " " +\
        x + " " +\
        y + " cm\n" +\
        "/InsertPic" + str(_PictureNumber_) + " Do\n"+\
        "Q\n"
    increasePictureNumber()

    #Get rid of the QUOTES mark
    picturefilename = picturefilename[1:-1]
    appendPictureFilename(picturefilename)
    return S

def ExeCommand(args):
    Command = args[0]
    parameters = args[1:]
    if Command == command.LineTo:
        return lineto(parameters)

    elif Command == command.MoveTo:
        return moveto(parameters)

    elif Command == command.Stroke:
        return stroke()

    elif Command == command.Close:
        return close()

    elif Command == command.Close_Stroke:
        return close_stroke()

    elif Command == command.Close_Fill_Stroke:
        return close_fill_stroke()

    elif Command == command.Fill:
        return fill()

    elif Command == command.Fill_Stroke:
        return fill_stroke()

    elif Command == command.Translate:
        return translate_coordinate(parameters)

    elif Command == command.CurveTo:
        return curveto(parameters)

    elif Command == command.RotateCoordinate:
        return rotate_coordinate(parameters)

    elif Command == command.Scale:
        return scale(parameters)

    elif Command == command.SetLineColor:
        return setrgb_stroking(parameters)

    elif Command == command.SetFillColor:
        return setrgb_nonstroking(parameters)

    elif Command == command.SetLineWidth:
        return setlinewidth(parameters)

    elif Command == command.SetDash:
        return setdash(parameters)

    elif Command == command.Text:
        return text(parameters)

    elif Command == command.SetFont:
        return setfont(parameters)
    elif Command == command.Picture:
        return insertpicture(parameters)

    elif Command == "":
        pass
        return ""
    else:
        print("Unknown Command !")
        print(Command)
        return ""

def lks2gs(LukisStream):
    """
    Convert LUKIS format (lks) to pdf graphic stream
    """
    R =""
    S = LukisStream.split(EOL)
    for s in S:
        s = qsplit(s)
        R += ExeCommand(s)
    return R

#------------------------------------------------------
def obj_definefont(ObjectNumber,
                    GenerationNumber,
                    BaseFont,
                    DefineFontName):
    S = str(ObjectNumber) + " " + str(GenerationNumber) + " obj\n"
    S += ("<</Type /Font\n"+
        "/Subtype /Type1\n"+
        "/Name /" + DefineFontName + "\n"+
        "/BaseFont /"+ BaseFont +"\n"+
        #"/Encoding /MacRomanEncoding\n"+
        #"/Encoding /WinAnsiEncoding\n"+
        ">>\n"+
        "endobj\n"
    )
    return S.encode()
def obj_greeting():
    S =""
    S +=    "%PDF-1.4\n"+\
            "% Created Manually\n"+\
            "%%Creator: Lee Chuin CHEN\n" +\
            "%% [leechuin@yamanashi.ac.jp, leechuin@gmail.com]\n" +\
            "%%Title: pplot\n" +\
            "%%CreationDate: "+ str(datetime.now()) + "\n"
    return S.encode()
def obj_catalog (objnum_base, objnum_outlines, objnum_pages):
    S = str(objnum_base) + " 0 obj\n"+\
        "<</Type /Catalog\n" +\
        "/Outlines " + str(objnum_outlines) + " 0 R\n" +\
        "/Pages " + str(objnum_pages) +" 0 R\n" +\
        ">>\n" +\
        "endobj\n"
    return S.encode()
def obj_outline(objnum_outlines):
    S = str(objnum_outlines) + " 0 obj\n" +\
        "<</Type /Outlines\n" +\
        "/Count 0\n" +\
        ">>" +\
        "endobj\n"
    return S.encode()
def obj_pages(objnum_pages, objnum_kids):
    #{{{
    S = str(objnum_pages) + " 0 obj\n" +\
        "<</Type /Pages\n" +\
        "/Kids [" + str(objnum_kids) + " 0 R]\n" +\
        "/Count 1\n" +\
        ">>\n" +\
        "endobj\n"
    return S.encode()
def obj_pagetype(
        objnum_kids,
        objnum_pages,
        objnum_fontbase,
        objnum_contents,
        objnum_picture=0,
        objnum_dataimage=0,
        PaperSize="Letter",
        Unit="pt",
        ):
    #DeclareFont = [    ["FH"    ,    fontname.Helvetica],
    #                    ["FHB"    ,    fontname.Helvetica_Bold],
    #                    ...
    DeclaredFont = myfont.ShortFontName.items()
    S_AllFontnames= ""
    S_Xobject = ""


    FontPointer = objnum_fontbase

    GotDataImage = True if objnum_dataimage!=0 else 0
    if len(_PictureFilename_)  | GotDataImage :
        S_Xobject += "/XObject <<\n"
        if len(_PictureFilename_):
            for n in range(_PictureNumber_):
                S_Xobject +=\
                "/InsertPic" + itos(n) + " " +\
                str(objnum_picture + n ) +\
                " 0 R\n"
        if GotDataImage:
            S_Xobject +=\
                "/DataImg0" + " " +\
                str(objnum_dataimage) +\
                " 0 R\n"
        S_Xobject += ">>\n"
    #e.g : /FT 40 0 R
    for f in DeclaredFont:
        S_AllFontnames += "/" + f[1] + " " + str(FontPointer) + " 0 R\n"
        FontPointer = FontPointer + 1
    S = (str(objnum_kids) + " 0 obj\n" +\
        "<</Type /Page\n" +\
        "/Parent " + str(objnum_pages) + " 0 R\n" +\
        #The code to adjust the paper size
        #"/MediaBox [0 0 612 792]\n" +
        "/MediaBox [0 0 " +\
        GetPaperSize(PaperSize,Unit) + "]\n"+\
        "/Contents " + str(objnum_contents) + " 0 R\n" +\
        "/Resources<</ProcSet [/PDF /Text]\n"+\
        "/Font <<\n"+\
            S_AllFontnames+\
        ">>\n"+\
        S_Xobject +\

        ">>\n"+\
        ">>\n"+\
        "endobj\n")
    return S.encode()
def obj_endstream_endobj():
    return     ("\n"+
            "endstream\n"+
            "endobj\n").encode()
def obj_contents(objnum_contents, Stream, Compress):
    #The Stream here is Byte
    StreamLength = len(Stream)
    S = str(objnum_contents) + " 0 obj\n" +\
            "<< /Length %d "%StreamLength +"\n"+\
            ("/Filter /FlateDecode" if Compress else "") +\
            ">>\n"+\
            "stream\n"
    return S.encode()+\
             Stream +\
             obj_endstream_endobj()
def obj_image(objnum_picture, ImageWidth,
        ImageHeight, ImageStream, DCTDecode):
    ImageLength = len(ImageStream)
    S=    str(objnum_picture) + " 0 obj\n" +\
        "<< /Type /XObject\n"+\
        "/Subtype /Image\n"+\
        "/Width " + str(ImageWidth) + "\n" +\
        "/Height " + str(ImageHeight) + "\n" +\
        "/ColorSpace /DeviceRGB\n"+\
        "/BitsPerComponent 8\n"+\
        "/Length "+ str(ImageLength) + "\n"+\
        "/Filter ["+\
                "/FlateDecode "+\
                "/ASCIIHexDecode "+\
                ("/DCTDecode" if DCTDecode else "") +\
                "] >>\n"+\
        "stream\n"
    return S.encode()+\
            ImageStream+\
            obj_endstream_endobj()


def obj_xref(pdf_objects):
    #{{{
    # At last, about time to write the XREF
    # If it is not done correctly, some pdf reader
    #eg. GS will complaint.:(
    NumOfPdfObj = len(pdf_objects)
    offset = [0]*NumOfPdfObj
    for i in range(1, NumOfPdfObj):
        offset[i] = offset[i-1] + len(pdf_objects[i-1])

    startxref = offset[NumOfPdfObj-1] + len(pdf_objects[NumOfPdfObj -1])

    Xref=""
    for i in range(1 , NumOfPdfObj):
        Xref += Decimal_To_10_DigitsString(offset[i]) + " 00000 n\r\n"

    pdf_xref = ("xref\r\n"+
        "0 "+ str(NumOfPdfObj) +" \r\n"+
        "0000000000 65535 f\r\n"+
        Xref +
        "trailer\n"+
        "<</Size 8\n"+
        "/Root 1 0 R\n"+
        ">>\n"+
        "startxref\n"+
        "%d"%(startxref) + "\n"
        "%%%EOF\n")
    return pdf_xref.encode()

def makepdf(GraphicsStream,
        Compress=False,
        UseJPEGForJPEGFile = False,
        #ImageData=[[128,128,128],[128,128,128],[34,70,24],[67,34,90]]):
        ImageData=[],
        ImageDataWidth =0,
        ImageDataHeigth =0,
        PaperSize="Letter",
        Unit="pt",
        PaperColor="white",
        PDF_Filename="killmex.pdf"):
    """
    Convert LUKIS graphic stream to pdf
    """
    resetPictureNumber()
    resetPictureFilename()
    GraphicsStream = lks2gs(GraphicsStream)
    GraphicsStream=GraphicsStream.encode()
    GotImageData = True if len(ImageData)>0 else False
    NumberOfImageData = 1 if GotImageData else 0
    if Compress:
        # in python 3, Zlib takes only Byte data. No more string.
        GraphicsStream = gzip.compress(GraphicsStream)

    # Manually assignig pdf obj number
    objnum_base     = 1
    objnum_outlines    = objnum_base + 1
    objnum_pages    = objnum_outlines + 1
    objnum_kids        = objnum_pages + 1
    objnum_contents = objnum_kids + 1


    objnum_picture = 0
    objnum_dataimage = 0
    if len(_PictureFilename_):
        objnum_picture    = objnum_contents + 1
        if GotImageData:
            objnum_dataimage =\
                 objnum_picture + NumberOfPicture
            objnum_fontbase = objnum_dataimage + 1
        else:
            objnum_fontbase =\
                 objnum_picture + _PictureNumber_
    else:
        if GotImageData:
            objnum_dataimage= objnum_contents + 1
            objnum_fontbase = objnum_dataimage + 1
        else:
            objnum_fontbase = objnum_contents + 1

    # Start writing pdf objects
    NumOfPdfObj = 1
    pdf_objects = []
    pdf_objects.append(obj_greeting())

    pdf_objects.append(obj_catalog (
                        objnum_base,
                        objnum_outlines,
                        objnum_pages
                        )
                    )

    pdf_objects .append(
         obj_outline(objnum_outlines)
        )

    pdf_objects.append(
        obj_pages(    objnum_pages,
                    objnum_kids)
            )

    pdf_objects.append(
        obj_pagetype(
            objnum_kids,
            objnum_pages,
            objnum_fontbase,
            objnum_contents,
            objnum_picture if len(_PictureFilename_) else 0,
            objnum_dataimage,
            PaperSize,
            Unit,
            )
        )



    pdf_objects.append(obj_contents(objnum_contents,
                        GraphicsStream,
                        Compress ))

    #Start to  insert picture from file
    if len(_PictureFilename_):
        for n in range(_PictureNumber_):
            [imagewidth,
            imageheight,
            imagelength,
            imagestream] = [0,0,0,"".encode()]
            ImageFilename = _PictureFilename_[n]
            DCTDecode =\
                 True if myimage.IsJPGFile(ImageFilename) &\
                UseJPEGForJPEGFile else False

            RetrievedImageData =\
                     myimage.GetImageByteStreamFromFile(
                    ImageFilename,
                    DCTDecode
                    )
            if RetrievedImageData == -1:
                print(
                    "Can not get image stream for \"" +
                    ImageFilename + "\"")
            else:
                [imagestream,
                imagewidth,
                imageheight]  =    RetrievedImageData

            pdf_objects.append(
                obj_image(
                        (objnum_picture + n),
                        imagewidth,
                        imageheight,
                        imagestream,
                        DCTDecode
                        )
                )

    if GotImageData:
        imagestream = myimage.GetImageByteStreamFromData(
            ImageData)
        pdf_objects.append(
                obj_image(
                        (objnum_dataimage),
                        ImageDataWidth,
                        ImageDataHeigth,
                        imagestream,
                        False
                        )
                )

    DeclareFont = myfont.ShortFontName.items()
    # Insert all available fonts
    FontPointer = objnum_fontbase
    for f in DeclareFont:
        pdf_objects.append(
                obj_definefont( FontPointer,
                                0,
                                f[0],    # Full name
                                f[1]    # Short name
                                )
                )
        FontPointer = FontPointer +  1

    #Finally, time to write the xref
    pdf_xref = obj_xref(pdf_objects)

    with open(PDF_Filename, "wb") as TargetFile:
        for myobject in pdf_objects:
            TargetFile.write(myobject)
        TargetFile.write(pdf_xref)
    return
