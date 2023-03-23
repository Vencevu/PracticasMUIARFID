import re
import argparse

specialDatePattern = re.compile(
    "[0-31] de (?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre) de \d{4,}",
    re.I | re.U)
acroPattern = re.compile("(?:EE.UU.|S.L.|CC.OO.|S.A.|D.|U.R.S.S.)")
pattern = re.compile(
    r"\b\S+\b|[(),\'\"?¿!¡:;%]|\.+|^\d*[.,]?\d*|\S+@\S+|\d{1,2}:\d{2}[h]?|http[s]?://[w{3}.]?\S*|\d{1,2}(?:|-)\d{2}(?:|-)\d{2,4}|@\S+|#\S+")


def tokenizarDocumento(listOfSentences):
    result = ""
    for sentence in listOfSentences:
        result += "%s\n" % sentence
        dates = specialDatePattern.findall(sentence)
        sentenceClean = re.sub(specialDatePattern, "DATE", sentence)
        acros = acroPattern.findall(sentenceClean)
        sentenceClean = re.sub(acroPattern, "ACRO", sentenceClean)
        for token in pattern.findall(sentenceClean):
            print(token)
            if token == "ACRO":
                acro = acros.pop(0)
                result += "%s \n" % acro
                print(acro)
            elif token == "DATE":
                date = dates.pop(0)
                result += "%s \n" % date
                print(date)
            else:
                result += "%s \n" % token
                print(token)

    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Tokenizador de español')
    parser.add_argument("--inputFile", dest="inputFile", type=str)
    parser.add_argument("--outputFile", dest="outputFile", type=str)
    args = parser.parse_args()
    inputSentences = open(args.inputFile, "r", encoding="utf-8").readlines()
    result = tokenizarDocumento(inputSentences)
    with open(args.outputFile, "w", encoding="utf-8") as f:
        f.write(result)