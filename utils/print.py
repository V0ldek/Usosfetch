import os
import webbrowser


def open_html(html):

    filename = '.usosfetch_temp.html'

    file = open(filename, 'w')

    file.write(html)

    webbrowser.open('file://' + os.getcwd() + '/' + filename)

    file.close()

