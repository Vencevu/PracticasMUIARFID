import re
import argparse

specialDatePattern = re.compile(
    "(\d{1,2}\s+de\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s*(de\s+\d{4,})*)",
    re.I | re.U
)
acroPattern = re.compile("EE\.UU\.|S\.L\.|CC\.OO\.|S\.A\.|U\.R\.S\.S\.|D\.|Dª\.|Sr\.|Sra\.|Dr\.|Dra\.", re.I | re.U)
namePattern = re.compile("((Á|É|Í|Ó|Ú|[A-Z])\w+\s+(Á|É|Í|Ó|Ú|[A-Z])\w+\s+(Á|É|Í|Ó|Ú|[A-Z])\w+)", re.UNICODE)
pattern = re.compile(
    r"\b\S+\b|[(),\'\"?¿!¡:;%]|\.+|^\d*[.,]?\d*|\S+@\S+|\d{1,2}:\d{2}[h]?|http[s]?://[w{3}.]?\S*|\d{1,2}(?:|-)\d{2}(?:|-)\d{2,4}|@\S+|#\S+|[\u263a-\U0001f919]", re.I | re.U)


def tokenizarDocumento(listOfSentences):
    result = ""
    for sentence in listOfSentences:
        result += "%s\n" % sentence

        names = namePattern.findall(sentence)
        names = [n[0] for n in names]
        print("NAMES: ", names)
        sentenceClean = re.sub(namePattern, "NAME ", sentence)

        dates = specialDatePattern.findall(sentenceClean)
        dates = [d[0] for d in dates]
        print("DATES: ", dates)
        sentenceClean = re.sub(specialDatePattern, "DATE ", sentenceClean)

        acros = acroPattern.findall(sentenceClean)
        print("ACROS: ", acros)
        sentenceClean = re.sub(acroPattern, "ACRO ", sentenceClean)
        for token in pattern.findall(sentenceClean):
            print("TOKEN :",token)
            if token == "ACRO":
                acro = acros.pop(0)
                result += "%s \n" % acro
                print("ACRO: ",acro)
            elif token == "DATE":
                date = dates.pop(0)
                result += "%s \n" % date
                print("DATE: ",date)
            elif token == "NAME":
                name = names.pop(0)
                result += "%s \n" % name
                print("NAME: ",name)
            else:
                result += "%s \n" % token
                # print(token)

    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Tokenizador de español')
    parser.add_argument("--i", dest="inputFile", type=str)
    parser.add_argument("--o", dest="outputFile", type=str)
    args = parser.parse_args()
    inputSentences = open(args.inputFile, "r", encoding="utf-8").readlines()
    result = tokenizarDocumento(inputSentences)
    with open(args.outputFile, "w", encoding="utf-8") as f:
        f.write(result)